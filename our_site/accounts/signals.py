from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

@receiver(pre_save, sender=User)
def send_activation_email(sender, instance, **kwargs):
    """
    Send an email to the user when their account is activated.
    """
    if instance.pk:
        try:
            old_user = User.objects.get(pk=instance.pk)
            # Check if is_active changed from False to True
            if not old_user.is_active and instance.is_active:
                try:
                    send_mail(
                        subject='Account Activated - WHMIS Wise',
                        message=f'Dear {instance.first_name},\n\nYour account has been activated by the administrator. You can now log in to your account at https://whmiswise.com/auth/login/\n\nSincerely,\nThe WHMIS Wise Team',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[instance.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"Failed to send activation email to user {instance.email}: {e}")
        except User.DoesNotExist:
            # Should not happen as we checked instance.pk
            pass
