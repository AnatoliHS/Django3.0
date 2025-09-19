from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Certificate
from django.views.decorators.http import require_POST
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.timezone import now

from django.conf import settings
import base64
import json
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.base import ContentFile


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@login_required
def slideshow(request):
    return render(request, "polls/slideshow.html")

@login_required
def test(request):
    return render(request, "polls/test.html")

@login_required
def certificate_view(request):
    context = {
        "completion_date": timezone.now().strftime("%B %d, %Y"),
    }
    return render(request, "polls/certificate.html", context)



@login_required
def certificate(request):
    user = request.user
    completion_date = now().strftime("%B %d, %Y")

    # Just get or create the certificate object
    certificate_obj, created = Certificate.objects.get_or_create(user=user)

    return render(request, "polls/certificate.html", {
        "user": user,
        "completion_date": completion_date,
        "certificate": certificate_obj
    })

@csrf_exempt
@login_required
def upload_certificate(request):
    if request.method == "POST":
        data = json.loads(request.body)
        image_data = data.get("image")
        user = request.user
        completion_date = timezone.now().strftime("%B %d, %Y")

        if image_data:
            # Decode the image
            image_content = base64.b64decode(image_data)

            # Render the HTML message
            message = render_to_string("emails/whmis_congrats.html", {
                "user": user,
                "completion_date": completion_date
            })

            # Send the email with attachment
            email = EmailMessage(
                subject="🎉 Your WHMIS Certificate is Ready!",
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.content_subtype = "html"
            email.attach("WHMIS_Certificate.png", image_content, "image/png")
            email.send()

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