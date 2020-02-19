"""Views Module for User App"""
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator

from rest_framework import (generics, authentication, permissions,
                            status, mixins, exceptions)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import mixins,generics,permissions
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils.translation import ugettext_lazy as _
from rest_framework.response import Response
from rest_framework import viewsets
from user.mixins import HttpResponseMixin
from user.permissions import UserViewPermission, IsAdminOwner
from user.utils import is_json
from passwordreset.serializers import EmailSerializer
from user.serializers import UserSerializer, AuthTokenSerializer, \
                              MyTokenObtainPairSerializer, RegistrationActivationSerializer, \
                              ModifyUserSerializer, ItemSerializer
User = get_user_model()

def getID(request):
  urlID=request.GET.get('id',None)
  inputJsonData={}
  if is_json(request.body):
    inputJsonData=json.loads(request.body)
  inputJsonID=inputJsonData.get("id",None)
  inputID = urlID or inputJsonID or None
  return inputID

class ModifyUserView(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = ModifyUserSerializer

    def patch(self, request, *args, **kwargs):
        avatar = request.data['avatar']
        name = request.data['name']
        user_id = 1
        obj = get_user_model().objects.filter(id=user_id).first()
        obj.avatar = avatar
        obj.name = name
        obj.save()
        return HttpResponse({'message': 'User Updated'}, status=200)

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

class CreateTokenView(ObtainAuthToken):
    """View that would generate auth token"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView,
                     generics.DestroyAPIView):
    """View that would update the user"""
    serializer_class = ModifyUserSerializer
   # authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user

class MyTokenObtainPairView(TokenObtainPairView):
    """Custom token View to include custom user fields based on custom token serializer"""
    serializer_class = MyTokenObtainPairSerializer
        
class UserActivateView(GenericAPIView):
    """
    An Api View which provides a method to activate a user based on the token
    """
    serializer_class = RegistrationActivationSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        uidb64 = serializer.validated_data['uidb64']
        token = serializer.validated_data['token']
        print(f"token-{token} uidb64-{uidb64}")
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            print(f"User id is {uid}")
            user = get_user_model().objects.get(pk=uid)
        except :
            user = None
        if not user:
            return Response({'status': 'notfound'}, status=status.HTTP_404_NOT_FOUND)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'status': 'OK'} )
        else:
            return Response({'status': 'expired'}, status=status.HTTP_404_NOT_FOUND)

class InviteAPIView(GenericAPIView):
    permission_classes=[UserViewPermission]
    serializer_class = EmailSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email__iexact=email).first()
        if user:
            raise exceptions.ValidationError({
                'detail': [_(
                    "There is already a user associated with this email ID")],
            })

        text_content = 'Invitation to Toptal Demo'
        subject = 'Invitation to Toptal Demo'
        template_name = "email/invitation.html"
        from_email = settings.EMAIL_HOST_USER
        recipients = [email]
        context = {
            'web_name' : settings.WEB_NAME,
            'activate_url': settings.FRONTEND_REGISTER_URL
        }
        html_content = render_to_string(template_name, context)
        email = EmailMultiAlternatives(subject, text_content, from_email, recipients)
        email.attach_alternative(html_content, "text/html")
        email.send()
        return Response({'status': 'OK'})

class UserBulkDeleteView(GenericAPIView):
    throttle_classes = ()
    permission_classes = [IsAdminOwner]
    serializer_class = ItemSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_ids = serializer.data['user_ids']
        if (len(user_ids) == 1) and (user_ids[0] == 'all'):
            User.objects.filter(is_superuser=False).delete()
        else:
            User.objects.filter(id__in=user_ids).delete()
        return Response({'status': 'OK'})
class UserAPIView(HttpResponseMixin,
                           mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           generics.ListAPIView):
  permission_classes=[UserViewPermission]
  serializer_class = UserSerializer
  passedID=None
  inputID=None
  search_fields = ('name', 'email')
  ordering_fields = ('name', 'id', 'created', 'updated')
  #filterset_class = ReportFilter

  filter_fields=("is_staff","is_locked","is_active","user_role")
  queryset=User.objects.all()
  def get_queryset(self, *args, **kwargs):
    if self.request.user.is_superuser:
        return User.objects.all()
    return User.objects.filter(is_superuser=False)
  def get_object(self):
    inputID=self.inputID
    queryset=self.get_queryset()
    obj=None
    if inputID is not None:
      obj=get_object_or_404(queryset,id=inputID)
      self.check_object_permissions(self.request,obj)
    return obj
  def get(self,request,*args,**kwargs):
    print(f"request user {request.user}")
    if not request.user.is_staff:
       raise PermissionDenied()
    self.inputID=getID(request)
    if self.inputID is not None:
      return self.retrieve(request,*args,**kwargs)
    return super().get(request,*args,**kwargs)

  def post(self,request,*args,**kwargs):
    print(request.data)
    return self.create(request,*args,**kwargs)

  def put(self,request,*args,**kwargs):
    self.inputID=getID(request)
    if self.inputID is None:
      data=json.dumps({"message":"Need to specify the ID for this method"})
      return self.render_to_response(data,status="404")
    return self.update(request,*args,**kwargs)

  def patch(self,request,*args,**kwargs):
    self.inputID=getID(request)
    print(request.POST)
    if self.inputID is None:
        data=json.dumps({"message":"Need to specify the ID for this method"})
        return self.render_to_response(data,status="404")
    return self.partial_update(request,*args,**kwargs)
   #self.inputID=getID(request)
   #print("I am here")
   #print(self.inputID)
   #serializer = UserSerializer(data=request.POST)
   #if serializer.is_valid():
   #    serializer.save()
   #    return Response(serializer.data)
   #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   #avatar = request.data['avatar']
   #print("wow")
   #obj = get_user_model().objects.filter(id=self.inputID).first()
   #obj.avatar = avatar
   #obj.name = name
   #obj.save()
   #return HttpResponse({'message': 'User Updated'}, status=200)
  #if self.inputID is None:
  #    data=json.dumps({"message":"Need to specify the ID for this method"})
  #    return self.render_to_response(data,status="404")
  #return self.partial_update(request,*args,**kwargs)

  def delete(self,request,*args,**kwargs):
    self.inputID=getID(request)
    if self.inputID is None:
      data=json.dumps({"message":"Need to specify the ID for this method"})
      return self.render_to_response(data,status="404")
    return self.destroy(request,*args,**kwargs)


