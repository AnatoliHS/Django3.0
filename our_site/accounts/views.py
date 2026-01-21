from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from experiences.models import Person, GuardianStudent, Participation, Role
from django.contrib import messages
from .forms import ProfilePictureForm, UserRegistrationForm
from constance import config
from polls.models import Certificate
from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

class AccountDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            # Get the user's person profile
            person = user.person
            context['person'] = person
            context['profile_exists'] = True

            # Determine which slideshow URL to show
            participation = person.participation_set.first()
            if participation and participation.group:
                group_name = participation.group.name.strip()

                if group_name == "Dental WHMIS":
                    context["slideshow_url"] = "/polls/slide/"
                elif group_name == "Pharmacy WHMIS":
                    context["slideshow_url"] = "/polls/slidePharm/"
                elif group_name == "General WHMIS":
                    context["slideshow_url"] = "/polls/slideReg/"
                else:
                    context["slideshow_url"] = None
            else:
                context["slideshow_url"] = None
            
            # Get the user's students if they're a guardian
            context['students'] = person.students.all()

            # Check if the user has students and if they are set to is guardian context is True 
            # Checks if a user has more than zero students
            context['is_guardian'] = context['students'].exists()
            
            # Get relationship information for each student
            student_relationships = {}
            for student in context['students']:
                relationship = GuardianStudent.objects.get(guardian=person, student=student)
                student_relationships[student.id] = relationship.relationship
                
            context['student_relationships'] = student_relationships
            
            # Get guardian information if the user is a student
            context['guardians'] = person.guardians.all()
            
            # Get relationship information for each guardian
            guardian_relationships = {}
            for guardian in context['guardians']:
                relationship = GuardianStudent.objects.get(guardian=guardian, student=person)
                guardian_relationships[guardian.id] = relationship.relationship
                
            context['guardian_relationships'] = guardian_relationships
            
            # Get participation preview (first 5) and flag for more
            all_parts = person.participation_set.all()
            context['participations_preview'] = all_parts[:5]
            context['has_more_participations'] = all_parts.count() > 5

            # Get the user's certificate if it exists
            context['certificate_emailed'] = self.request.session.get('certificate_emailed', False)
            
            #Populate context['certificate'] with the user's certificate object
           # try:
                #certificate_obj = user.certificate
            # Get the user's certificate if it exists
            certificate_obj = Certificate.objects.filter(user=user).first()
            context['certificate'] = certificate_obj  # None if not completed
           # except Certificate.DoesNotExist:
               # context['certificate'] = None
           
            
        except Person.DoesNotExist:
            context['profile_exists'] = False
            
        return context

def register_view(request):
    """View for registering a new user"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                selected_group = form.cleaned_data['group']

                # Ensure a student role exists for newly registered users
                student_role = Role.objects.filter(title__iexact='student').order_by('id').first()
                if student_role is None:
                    student_role = Role.objects.create(title='Student', description='Auto-created student role')

                person = Person.objects.create(user=user, role=student_role)

                # Capture the current academic year for participation tracking
                current_year = timezone.now().year
                Participation.objects.create(
                    person=person,
                    group=selected_group,
                    years=[current_year]
                )

                # Send notification email to admin
                try:
                    send_mail(
                        subject='New User Registration',
                        message=f'A new user has registered.\n\nName: {user.first_name} {user.last_name}\nEmail: {user.email}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=['info@whmiswise.com'],
                        fail_silently=True,
                    )
                except Exception as e:
                    # Log error but don't fail registration
                    print(f"Failed to send admin notification email: {e}")

            if config.SIGNUP_NEW_ACCOUNTS_PENDING:
                messages.info(request, "Your account has been created and is pending approval. You will be notified when an administrator approves your account.")
            else:
                messages.success(request, "Your account has been created successfully! You can now log in.")
            # Always redirect to login after registration
            return redirect('login')
    else:
        form = UserRegistrationForm()
        
    return render(request, 'registration/register.html', {
        'form': form,
        'pending_approval': config.SIGNUP_NEW_ACCOUNTS_PENDING
    })

@login_required
def profile_view(request):
    """View for displaying and updating the user's profile"""
    try:
        person = request.user.person
        
        if request.method == 'POST':
            form = ProfilePictureForm(request.POST, request.FILES, instance=person)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile picture updated successfully!")
                return redirect('accounts:profile')
        else:
            form = ProfilePictureForm(instance=person)
            
        return render(request, 'accounts/profile.html', {
            'person': person,
            'form': form
        })
        
    except Person.DoesNotExist:
        # User doesn't have a person profile yet
        return redirect('accounts:create_profile')

@login_required
def create_profile_view(request):
    """View for creating a new profile if one doesn't exist"""
    # This is a placeholder for now
    return render(request, 'accounts/create_profile.html')

@login_required
def update_visibility(request):
    if request.method == 'POST':
        try:
            person = request.user.person
            person.is_public = request.POST.get('is_public') == 'on'
            person.show_activities_publicly = request.POST.get('show_activities_publicly') == 'on'
            person.show_guardians_publicly = request.POST.get('show_guardians_publicly') == 'on'
            person.save()
            messages.success(request, 'Visibility settings updated successfully!')
        except Person.DoesNotExist:
            messages.error(request, 'Profile not found.')
    return redirect('accounts:profile')

@login_required
def toggle_participation_visibility(request, pk):
    """Toggle public visibility of a participation"""
    try:
        participation = Participation.objects.get(pk=pk, person=request.user.person)
    except Participation.DoesNotExist:
        messages.error(request, 'Participation not found.')
        return redirect('accounts:dashboard')
    participation.is_public = not participation.is_public
    participation.save()
    messages.success(request, 'Participation visibility updated.')
    return redirect('accounts:dashboard')
