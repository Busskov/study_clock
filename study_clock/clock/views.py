from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render, redirect
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics, viewsets, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, ErrorSerializer, MessageSerializer, LoginSerializer, UserSerializer, \
    EmailUpdateSerializer, AvatarUpdateSerializer
from .permissions import IsAdmin
from .models import User
from .utils import send_email_confirmation
import logging
import uuid

logger = logging.getLogger(__name__)


def homePageRedirect(request):
    logger.info('Redirecting to the main page')
    return redirect('index')


def homePage(request):
    logger.debug('Displaying the main page')
    return render(request, 'homePage.html')


def chat_view(request):
    logger.debug('Displaying the chat page')
    return render(request, 'chat.html')


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return HttpResponse("Invalid username or password")
    return render(request, 'login.html')


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description='Registers a new user in the system. Returns a message about successful registration and the user ID.',
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description='User created successfully',
                schema=RegisterSerializer,
                examples={'application/json': {'message': 'User created successfully', 'user_id': 1}},
            ),
            400: openapi.Response(
                description='Validation Error',
                schema=ErrorSerializer,
                examples={'application/json': {'username': ['This field is required.']}},
            ),
        },
    )
    def post(self, request):
        logger.debug('Attempt to register a new user')
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info('The user has been created: %s', user.username)
            return Response({'message': 'User created successfully', 'user_id': user.id}, status=HTTP_201_CREATED)
        logger.warning('Error when creating a user: %s', serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='Returns a message confirming access to the protected resource. Requires user authentication.',
        responses={
            200: openapi.Response(
                description='Successful response',
                schema=MessageSerializer,
                examples={'application/json': {'message': 'This is a protected view'}},
            ),
            401: openapi.Response(
                description='Unauthorized - Authentication required',
                schema=ErrorSerializer,
                examples={'application/json': {'detail': 'Authentication credentials were not provided.'}}
            ),
        },
    )
    def get(self, request):
        logger.debug('Request to a protected view')
        return Response({'message': 'This is a protected view'}, status=200)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description='Login a user and return a JWT token upon successful authentication',
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description='User authenticated successfully',
                schema=LoginSerializer,
                examples={'application/json': {'token': 'your_jwt_token'}},
            ),
            400: openapi.Response(
                description='Invalid credentials',
                schema=ErrorSerializer,
                examples={'application/json': {'detail': 'Invalid username or password'}},
            ),
        },
    )
    def post(self, request):
        logger.debug('Attempt to log in a user')
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            logger.info('User logged in successfully: %s', user.username)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        logger.warning('Login failed for user: %s', request.data.get('username'))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserFilterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = ['username', 'email', 'country']
    ordering_fields = ['username', 'date_of_birth', 'country']

    def get_queryset(self):
        queryset = super().get_queryset()

        is_premium = self.request.query_params.get('is_premium', None)
        if is_premium is not None:
            queryset = queryset.filter(is_premium=is_premium)

        return queryset


class UserUpdateView(APIView):
    permission_classes = [AllowAny]

    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({'detail': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email_confirmation_token=token)
            user.email_confirmed = True
            user.email_confirmation_token = None
            user.save()
            return Response({'message': 'Email successfully confirmed.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)


class UpdateEmailView(APIView):
    def post(self, request):
        user = request.user
        serializer = EmailUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            user.email_confirmation_token = uuid.uuid4()
            user.email_confirmed = False
            user.save()
            send_email_confirmation(user)
            return Response({'message': 'Email updated. Please confirm your new email.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateAvatarView(APIView):
    def post(self, request):
        user = request.user
        serializer = AvatarUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Avatar updated successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)