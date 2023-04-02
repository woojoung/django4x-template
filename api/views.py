from django.shortcuts import render
from rest_framework import views, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from library import utils, enums
from http import HTTPStatus
from .models import User
from datetime import datetime, timedelta
from base64 import b64encode
from django.conf import settings
from urllib.parse import urlencode
from django.utils.crypto import get_random_string
import jwt


# Create your views here.
# https://developers.google.com/identity/gsi/web/guides/verify-google-id-token
@permission_classes([permissions.AllowAny])
class GoogleLoginView(views.APIView):

    def post(self, request):
        access_token: str = request.data.get('access_token', '')
        if access_token == '':
            return Response({'detail': 'access_token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        url = 'https://www.googleapis.com:443/oauth2/v4/userinfo?access_token=' + access_token
        resp = utils.http_request('GET', url, {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        })

        if resp.http_status != HTTPStatus.OK:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        json_loaded = utils.try_json_loads(resp.body)
        if isinstance(json_loaded, ValueError):
            return Response({'detail': str(json_loaded)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if 'error' in json_loaded:
            return Response({'detail': json_loaded['error_description']}, status=status.HTTP_401_UNAUTHORIZED)

        social_platform_id = json_loaded.get('sub', '')
        # email = json_loaded.get('email')
        # nickname = json_loaded.get('name', '')
        # profile_image_url = json_loaded.get('picture', '')

        try:
            user = User.objects.get(social_platform_id=social_platform_id, delete_time=0, is_active=True)
        except User.DoesNotExist:
            return Response({'detail': 'User Not Found'}, status=status.HTTP_404_NOT_FOUND)

        if user.is_active is False:
            return Response({'detail': 'user is inactive'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        access = AccessToken.for_user(user)
        setattr(access.payload, 'full_name', user.nickname)
        return Response(
            {
                'access': str(access),
                'refresh': str(refresh),
            }
        )



# https://developer.apple.com/documentation/sign_in_with_apple/generate_and_validate_tokens
@permission_classes([permissions.AllowAny])
class AppleLoginView(views.APIView):

    def post(self, request):
        code = request.data.get('code', '')
        if code == '':
            return Response({'detail': 'code is required'}, status.HTTP_400_BAD_REQUEST)

        client_id = settings.AUTH_APPLE_CLIENT_ID
        client_secret = jwt.encode({
            'iss': settings.AUTH_APPLE_TEAM_ID,
            'iat': datetime.now().timestamp(),
            'exp': datetime.now().timestamp() + timedelta(days=180).total_seconds(),
            'aud': 'https://appleid.apple.com',
            'sub': settings.AUTH_APPLE_CLIENT_ID,
        }, settings.AUTH_APPLE_PRIVATE_KEY,
            algorithm='ES256',
            headers={
                'kid': settings.AUTH_APPLE_KEY_ID
            })

        resp = utils.http_request('POST', 'https://appleid.apple.com:443/auth/token', {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        }, urlencode({
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }))

        if resp.http_status != HTTPStatus.OK:
            return Response({'detail': 'Invalid token'}, status.HTTP_401_UNAUTHORIZED)

        json_loaded_body = utils.try_json_loads(resp.body)
        if isinstance(json_loaded_body, ValueError):
            return Response({'detail': str(json_loaded_body)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        apple_id_token = json_loaded_body.get('id_token', '')

        if apple_id_token == '' or '.' not in apple_id_token:
            return Response({'detail': 'Invalid token'}, status.HTTP_401_UNAUTHORIZED)

        id_token_split = apple_id_token.split('.')
        if len(id_token_split) != 2:
            return Response({'detail': 'Invalid token'}, status.HTTP_401_UNAUTHORIZED)

        padding_count = 4 - len(id_token_split[1]) % 4
        padding = '=' * padding_count
        id_token_padded = id_token_split[1] + padding

        id_token_decoded = b64encode(id_token_padded).decode('ascii')
        json_loaded_id_token_decoded = utils.try_json_loads(id_token_decoded)
        if isinstance(json_loaded_id_token_decoded, ValueError):
            return Response({'detail': str(json_loaded_id_token_decoded)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        social_platform_id = json_loaded_id_token_decoded.get('sub', '')
        # email = json_loaded_id_token_decoded.get('email', '')
        # nickname = 'User' + '(' + get_random_string(6) + ')'

        try:
            user = User.objects.get(social_platform_id=social_platform_id, delete_time=0, is_active=True)
        except User.DoesNotExist:
            return Response({'detail': 'User Not Found'}, status=status.HTTP_404_NOT_FOUND)

        if user.is_active is False:
            return Response({'detail': 'user is inactive'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        access = AccessToken.for_user(user)
        setattr(access.payload, 'full_name', user.nickname)
        return Response(
            {
                'access': str(access),
                'refresh': str(refresh),
            }
        )


@permission_classes([permissions.AllowAny])
class SignupView(views.APIView):

    def post(self, request):
        social_platform_type = request.data.get('social_platform_type', 0)
        social_platform_id = request.data.get('social_platform_id', '')
        email = request.data.get('email', '')
        nickname = request.data.get('nickname', '')
        date_of_birth = request.data.get('date_of_birth', '1970-01-01')
        profile_image_url = request.data.get('profile_image_url', '')

        if social_platform_type == 0:
            return Response({'detail': 'social_platform_type is required'}, status=status.HTTP_400_BAD_REQUEST)
        if social_platform_id == '':
            return Response({'detail': 'social_platform_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        if email == '':
            return Response({'detail': 'email is required'}, status=status.HTTP_400_BAD_REQUEST)
        if nickname == '':
            return Response({'detail': 'nickname is required'}, status=status.HTTP_400_BAD_REQUEST)
        if date_of_birth == '1970-01-01':
            return Response({'detail': 'date_of_birth is required'}, status=status.HTTP_400_BAD_REQUEST)
        if profile_image_url == '':
            return Response({'detail': 'profile_image_url is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, delete_time=0, is_active=True)
        except User.DoesNotExist:
            user = None
            
        if user is None:
            user = User()
            user.set_password(User.objects.make_random_password())
            user.social_platform_id = social_platform_id
            user.social_platform_type = social_platform_type
            user.nickname = nickname
            user.profile_image_url = profile_image_url
            user.email = email
            user.date_of_birth = date_of_birth
            user.save()

        refresh = RefreshToken.for_user(user)
        access = AccessToken.for_user(user)
        setattr(access.payload, 'full_name', nickname)
        return Response(
            {
                'access': str(access),
                'refresh': str(refresh),
            }
        )
