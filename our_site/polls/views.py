from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Certificate

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

     # Check if the user already has a certificate
    certificate_obj, created = Certificate.objects.get_or_create(user=user)

    if not request.session.get("certificate_emailed", False):
        # Render message from template
        message = render_to_string("emails/whmis_congrats.html", {
            "user": user,
            "completion_date": completion_date
        })

        email = EmailMessage(
            subject="🎉 Your WHMIS Certificate is Ready!",
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.content_subtype = "html"

        # Optional: Attach a certificate image if you've uploaded it via AJAX (see Step 3)
        cert_data = request.session.get("certificate_base64")
        if cert_data:
            email.attach("WHMIS_Certificate.png", base64.b64decode(cert_data), "image/png")

        email.send()
        request.session["certificate_emailed"] = True

    return render(request, "polls/certificate.html", {
        "user": user,
        "completion_date": completion_date,
        "certificate": certificate_obj
    })

@csrf_exempt
def upload_certificate(request):
    if request.method == "POST":
        data = json.loads(request.body)
        image_data = data.get("image")

        if image_data:
            image_content = ContentFile(base64.b64decode(image_data), "certificate.png")

            # Prepare email
            email = EmailMessage(
                "Congratulations! Here's your WHMIS Certificate",
                "Attached is your certificate of completion.",
                to=[request.user.email]  # or hardcoded for testing
            )
            email.attach("WHMIS_Certificate.png", image_content.read(), "image/png")
            email.send()

            return JsonResponse({"status": "success"})

    return JsonResponse({"status": "failed"}, status=400)