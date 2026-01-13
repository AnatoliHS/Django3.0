from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Certificate
from django.views.decorators.http import require_POST
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.base import ContentFile
import base64
import json


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@login_required
def slideshow(request):
    return render(request, "polls/slideshow.html", {"slideshow_slug": "whmis-general"})

@login_required
def slideshowPharm(request):
    return render(request, "polls/slideshowPharm.html", {"slideshow_slug": "whmis-pharmacy"})

@login_required
def slideshowReg(request):
    return render(request, "polls/slideshowReg.html", {"slideshow_slug": "whmis-dental"})


@login_required
def test(request):
    return render(request, "polls/test.html")


# ✅ Main certificate view
@login_required
def certificate(request):
    user = request.user
    certificate_obj, created = Certificate.objects.get_or_create(user=user)
    completion_date = certificate_obj.issued_at.strftime("%B %d, %Y")

    # Get the linked Person object (if any)
    person = getattr(user, "person", None)
    group_name = "General WHMIS"  # default fallback

    if person:
        participation = person.participation_set.first()
        if participation and participation.group:
            group_name = participation.group.name.strip()

    # Choose logo based on group name
    if group_name == "Pharmacy WHMIS":
        logo_image = "images/pharmaWhmis2.png"
    elif group_name == "Dental WHMIS":
        logo_image = "images/whimiswise.png"
    else:  # General WHMIS
        logo_image = "images/whimiswise2.png"

    return render(request, "polls/certificate.html", {
        "user": user,
        "completion_date": completion_date,
        "certificate": certificate_obj,
        "logo_image": logo_image,
        "group_name": group_name,
    })


# ✅ Upload + email certificate
@csrf_exempt
@login_required
def upload_certificate(request):
    if request.method == "POST":
        data = json.loads(request.body)
        image_data = data.get("image")
        user = request.user

        # Fetch the existing certificate so we use the same issued_at date
        certificate_obj = get_object_or_404(Certificate, user=user)
        completion_date = certificate_obj.issued_at.strftime("%B %d, %Y")

        if image_data:
            image_content = base64.b64decode(image_data)

            # Render the HTML message with the fixed completion date
            message = render_to_string("emails/whmis_congrats.html", {
                "user": user,
                "completion_date": completion_date,
            })

            email = EmailMessage(
                subject="🎉 Your WHMIS Certificate is Ready!",
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.content_subtype = "html"
            email.attach("WHMIS_Certificate.png", image_content, "image/png")
            email.send()

            # (optional) Save the image to the model if you want
            certificate_obj.image.save(
                f"{user.username}_certificate.png",
                ContentFile(image_content),
                save=True
            )

            return JsonResponse({"status": "success"})

    return JsonResponse({"status": "failed"}, status=400)


@login_required
@require_POST
def complete_certificate(request):
    user = request.user
    certificate_obj, created = Certificate.objects.get_or_create(user=user)
    certificate_obj.completed = True
    certificate_obj.save()
    return JsonResponse({"status": "success"})