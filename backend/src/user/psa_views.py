from django.conf import settings

from rest_framework import serializers
from rest_framework import status
#from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import (
        AccessToken, RefreshToken, SlidingToken, Token, UntypedToken,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from requests.exceptions import HTTPError

from social_django.utils import psa
from user.serializers import  MyTokenObtainPairSerializer

class SocialSerializer(serializers.Serializer):
    """
    Serializer which accepts an OAuth2 access token.
    """
    access_token = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )


@api_view(http_method_names=['POST'])
@permission_classes([AllowAny])
@psa()
def exchange_token(request, backend):
    """
    Exchange an OAuth2 access token for one for this site.
    This simply defers the entire OAuth2 process to the front end.
    The front end becomes responsible for handling the entirety of the
    OAuth2 process; we just step in at the end and use the access token
    to populate some user identity.
    The URL at which this view lives must include a backend field, like:
        url(API_ROOT + r'social/(?P<backend>[^/]+)/$', exchange_token),
    Using that example, you could call this endpoint using i.e.
        POST API_ROOT + 'social/facebook/'
        POST API_ROOT + 'social/google-oauth2/'
    Note that those endpoint examples are verbatim according to the
    PSA backends which we configured in settings.py. If you wish to enable
    other social authentication backends, they'll get their own endpoints
    automatically according to PSA.
    ## Request format
    Requests must include the following field
    - `access_token`: The OAuth2 access token provided by the provider
    """
    print(f"I am in this view with backend as {backend}")
    serializer = SocialSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        # set up non-field errors key
        # http://www.django-rest-framework.org/api-guide/exceptions/#exception-handling-in-rest-framework-views
        try:
            nfe = settings.NON_FIELD_ERRORS_KEY
        except AttributeError:
            nfe = 'non_field_errors'

        try:
            # this line, plus the psa decorator above, are all that's necessary to
            # get and populate a user object for any properly enabled/configured backend
            # which python-social-auth can handle.
            user = request.backend.do_auth(serializer.validated_data['access_token'])
        except HTTPError as e:
            # An HTTPError bubbled up from the request to the social auth provider.
            # This happens, at least in Google's case, every time you send a malformed
            # or incorrect access key.
            return Response(
                {'errors': {
                    'token': 'Invalid token',
                    'detail': str(e),
                }},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user:
            if user.is_active:
                #token, _ = Token.objects.get_or_create(user=user)
               # refresh = RefreshToken.for_user(user)
               # return Response({'token': str(refresh.access_token)})
                refresh = MyTokenObtainPairSerializer.get_token(user)
                data={}
                data['refresh'] = str(refresh)
                data['access'] = str(refresh.access_token)
                return Response(data)

            else:
                # user is not active; at some point they deleted their account,
                # or were banned by a superuser. They can't just log in with their
                # normal credentials anymore, so they can't log in with social
                # credentials either.
                return Response(
                    {'errors': {nfe: 'This user account is inactive'}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # Unfortunately, PSA swallows any information the backend provider
            # generated as to why specifically the authentication failed;
            # this makes it tough to debug except by examining the server logs.
            return Response(
                {'errors': {nfe: "Authentication Failed"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
