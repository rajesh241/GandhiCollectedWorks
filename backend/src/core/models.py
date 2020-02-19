"""
Core Models
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from passwordreset.signals import reset_password_token_created
# Create your models here.

def avatar_upload_path(instance, filename):
    """This function will return the upload path for avatar"""
    return '/'.join(["avatar",str(instance.id),filename])
class UserManager(BaseUserManager):
    """
    Custom User Manager Class
    """
    def create_user(self, email, password=None, **extra_fields):
        """Create and Saves user"""
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    user_role = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    login_attempt_count = models.PositiveSmallIntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    avatar = models.ImageField(blank=True, null=True,
                               upload_to=avatar_upload_path)
    avatar_url = models.URLField(max_length=1024, null=True, blank=True)
    provider = models.CharField(max_length=32, default="native")
    objects = UserManager()
    USERNAME_FIELD = 'email'

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.email,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            #reverse('password_reset:reset-password-request'), reset_password_token.key)
            settings.FRONTEND_PWDRESETCONFIRM_URL, reset_password_token.key)
    }

    # render email text
    email_html_message = render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = render_to_string('email/user_reset_password.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Toptal Demo"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@somehost.local",
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


def get_user_role(user):
    '''Assign a User role based on type of user. This can be used in front end
    to display different kind of UI for each user type'''
    if user.is_superuser:
        my_role = 'admin'
    elif user.is_staff:
        my_role = 'realtor'
    elif user.is_active:
        my_role = 'client'
    else:
        my_role = 'client'
    return my_role

def user_post_save_receiver(sender, instance, *args, **kwargs):
    '''Function to assign a role to user object'''
    my_role = get_user_role(instance)
    if instance.user_role != my_role:
        instance.user_role = my_role
        instance.save()

post_save.connect(user_post_save_receiver, sender=User)
