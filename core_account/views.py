from rest_framework.views import APIView, Response
from rest_framework import status
from rest_framework import permissions
from core_account.token import get_tokens_for_user
from core_account.renderers import UserRenderer
from core_account.serializers import CreateUserSerializer
from rest_framework.generics import GenericAPIView
from core_account.serializers import GoogleSocialAuthSerializer
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from itsdangerous import URLSafeSerializer
User = get_user_model()
# Create your views here.

class Register(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [UserRenderer]

    def post(self, request):
       
        user_serializer = CreateUserSerializer(data=request.data)
    
        if user_serializer.is_valid():
            current_user = user_serializer.save()
            token = get_tokens_for_user(current_user)

            return Response({"Success": True, 'token':token}, status=status.HTTP_201_CREATED)
        else:
            return Response({"Success": False, "Error": user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class GoogleSocialAuthView(GenericAPIView):

    serializer_class = GoogleSocialAuthSerializer

    def post(self, request):
        """
        POST with "auth_token"
        Send an idtoken as from Google to get user information
        """
        auth_token = request.data.get('auth_token')
        print("Here is auth token:", auth_token)  # Check if the token is received
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            print("Serializer is valid")  # Confirm if the serializer is valid
            data = serializer.validated_data['auth_token']
            print("Validated auth token:", data)  # Confirm if the token is validated
            return Response(data, status=status.HTTP_200_OK)
        else:
            print("Serializer errors:", serializer.errors)

class UserLogin(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Email for this user not found"}, status=status.HTTP_400_BAD_REQUEST)

        authenticated_user = authenticate(request, username=user.email, password=password)

        if authenticated_user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if authenticated_user.is_blocked:
            return Response({"error": "Account banned"}, status=status.HTTP_400_BAD_REQUEST)

        # Encode user ID
        serializer = URLSafeSerializer(settings.SECRET_KEY)
        encoded_user_id = serializer.dumps(authenticated_user.id)

        profile_url = settings.BACKEND + authenticated_user.profile.url if authenticated_user.profile else None
        token = get_tokens_for_user(authenticated_user)

        user_data = {
            "user_id": encoded_user_id,
            "profile": profile_url,
            "username": authenticated_user.username,
            "fullname": authenticated_user.name,
            "email": authenticated_user.email,
            "token": token,
        }

        return Response({"message": "Logged in", "user": user_data}, status=status.HTTP_202_ACCEPTED)