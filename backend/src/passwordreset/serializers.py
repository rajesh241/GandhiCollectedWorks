from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

__all__ = [
    'EmailSerializer',
    'PasswordTokenSerializer',
]


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordTokenSerializer(serializers.Serializer):
    password = serializers.CharField(label=_("Password"), style={'input_type': 'password'})
    password2 = serializers.CharField(label=_("Password2"), style={'input_type': 'password'})
    token = serializers.CharField()
