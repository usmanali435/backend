from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

from core_account.utiles.register.username_slicer import get_email_username

User = get_user_model()


def register_agent(data, provider='google'):

    filtered_user_by_email = User.objects.filter(email=data.email)

    if filtered_user_by_email.exists():
        if provider == filtered_user_by_email[0].auth_provider:
            registered_user = User.objects.get(email=data.email)
            registered_user.check_password(settings.SOCIAL_SECRET)
            Token.objects.filter(user=registered_user).delete()
            Token.objects.create(user=registered_user)
            new_token = Token.objects.get(user=registered_user).key

            return {
                'username': registered_user.username,
                'email': registered_user.email,
                'tokens': new_token
            }
        else:
            raise AuthenticationFailed(
                detail=f'Please continue your login using {filtered_user_by_email[0].auth_provider}'
            )
    else:
        user = {
            'email':data.email,
            'username': get_email_username(data.email),
            'password': settings.SOCIAL_SECRET
        }
        user = User.objects.create_user(**user)
        user.is_active = True
        user.auth_provider = provider
        user.save()
        new_user = User.objects.get(email=data.email)
        new_user.check_password(settings.SOCIAL_SECRET)
        new_token = Token.objects.create(user=new_user).key
        return {
            'email': new_user.email,
            'username': new_user.username,
            'tokens': new_token,
        }