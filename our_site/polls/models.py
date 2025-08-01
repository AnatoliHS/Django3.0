import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return self.question_text
    
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text + " " + str(self.votes) 

class Certificate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='certificates/', null=True, blank=True)  # Optional

    def __str__(self):
        return f"Certificate for {self.user.username} issued on {self.issued_at}"
