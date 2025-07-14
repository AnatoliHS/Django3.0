from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@login_required
def slideshow(request):
    return render(request, "polls/slideshow.html")

@login_required
def test(request):
    return render(request, "polls/test.html")

@login_required
def certificate(request):
    context = {
        "completion_date": timezone.now().strftime("%B %d, %Y"),
    }
    return render(request, "polls/certificate.html", context)