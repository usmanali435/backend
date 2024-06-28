from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from core_account.utiles.Google.google import Google
from core_account.utiles.register.register import register_agent
User = get_user_model()


class CreateUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['name', 'username', 'email','password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}
    
   
    def validate(self, data):
        password = data.get('password')
        password2 = data.pop('confirm_password', None)

        validate_password(password)

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords do not match'})

        return data

    def create(self, validated_data):
        email = validated_data.pop('email', None)
        username = validated_data.pop('username', None)
        if email is None:
            raise serializers.ValidationError({'email': 'Email field is required'})
        if username is None:
            raise serializers.ValidationError({'username': 'username field is required'})

        validated_data['password'] = validated_data.get('password')
        user = User.objects.create_user(email=email, username=username, **validated_data)
        return user


class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        print("Received auth token:", auth_token)  # Confirm if the token is received in the serializer
        user_data = Google.validate(auth_token)
        if isinstance(user_data, str):
            raise serializers.ValidationError(
                'The token is invalid or expired. Please login again.'
            )
        try:
            user_data['sub']
        except KeyError:
            raise serializers.ValidationError(
                'The token is invalid or expired. Please login again.'
            )
        
        if user_data['aud'] != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed('Oops, who are you?')

        user_id = user_data['sub']
        email = user_data['email']
        name = user_data['name']
        provider = 'google'

        print("User data:", user_data)  # Print user data received from Google
        return register_agent(
            provider=provider, user_id=user_id, email=email, name=name
        )