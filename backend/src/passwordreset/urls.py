""" URL Configuration for core auth
"""
from django.conf.urls import url, include
from django.urls import path
from passwordreset.views import reset_password_request_token, reset_password_confirm

app_name = 'password_reset'

urlpatterns = [
    path('', reset_password_request_token, name="reset-password-request"),
    path('confirm/', reset_password_confirm, name="reset-password-confirm"),
]
