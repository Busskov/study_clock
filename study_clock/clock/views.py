from django.contrib.auth import authenticate, login
from django.core.serializers import serialize
from django.db import models
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
    EmailUpdateSerializer, AvatarUpdateSerializer, PrivateMessageSerializer, ActivitySerializer
from .permissions import IsAdmin
from .models import User, PrivateMessage, Activity
from .utils import send_email_confirmation
import logging
import uuid
import json

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
    permission_classes = [IsAdmin]


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class UserFilterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

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
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='Updates user information based on the provided user ID.',
        request_body=UserSerializer,
        responses={
            200: openapi.Response(
                description='User updated successfully',
                schema=UserSerializer,
                examples={'application/json': {'id': 1, 'username': 'updated_user', 'email': 'updated@example.com'}}
            ),
            400: openapi.Response(
                description='Validation Error',
                schema=ErrorSerializer,
                examples={'application/json': {'username': ['This field is required.']}}
            ),
            404: openapi.Response(
                description='User not found',
                schema=ErrorSerializer,
                examples={'application/json': {'detail': 'User not found'}}
            )
        }
    )
    def put(self, request):
        try:
            user = request.user
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserReadView(APIView):
    permission_classes = [IsAuthenticated]

    # @swagger_auto_schema(
    #     operation_description='Returns user information.',
    #     request_body=UserSerializer,
    #     responses={
    #         200: openapi.Response(
    #             description='User updated successfully',
    #             schema=UserSerializer,
    #             examples={'application/json': {'id': 1, 'username': 'updated_user', 'email': 'updated@example.com'}}
    #         ),
    #         400: openapi.Response(
    #             description='Validation Error',
    #             schema=ErrorSerializer,
    #             examples={'application/json': {'username': ['This field is required.']}}
    #         ),
    #         404: openapi.Response(
    #             description='User not found',
    #             schema=ErrorSerializer,
    #             examples={'application/json': {'detail': 'User not found'}}
    #         )
    #     }
    # )
    def get(self, request):
        try:
            user = request.user
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # user_data = {}
        # user_data['username'] = user.username
        # user_d
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


#TODO: think about this
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description='Verifies a user\'s email using a provided token.',
        manual_parameters=[
            openapi.Parameter(
                'token',
                openapi.IN_QUERY,
                description='Email confirmation token',
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description='Email successfully confirmed',
                schema=MessageSerializer,
                examples={'application/json': {'message': 'Email successfully confirmed.'}}
            ),
            400: openapi.Response(
                description='Invalid or missing token',
                schema=ErrorSerializer,
                examples={'application/json': {'detail': 'Invalid token'}}
            )
        }
    )
    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({'detail': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            uuid.UUID(token)
        except:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email_confirmation_token=token)
            user.email_confirmed = True
            user.email_confirmation_token = None
            user.save()
            return Response({'message': 'Email successfully confirmed.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

        # try:
        #     #user = User.objects.get(email_confirmation_token=token)
        #     user = request.user
        #     if user.email_confirmation_token == token:
        #         user.email_confirmed = True
        #         user.email_confirmation_token = None
        #         user.save()
        #         return Response({'message': 'Email successfully confirmed.'}, status=status.HTTP_200_OK)
        #     return Response({'detail': 'Provided token doesnt match with expected one'}, status=status.HTTP_400_BAD_REQUEST)
        # except User.DoesNotExist:
        #     return Response({'detail': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)


class UpdateEmailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='Updates a user\'s email and sends a confirmation token to the new address.',
        request_body=EmailUpdateSerializer,
        responses={
            200: openapi.Response(
                description='Email updated successfully',
                schema=MessageSerializer,
                examples={'application/json': {'message': 'Email updated. Please confirm your new email.'}}
            ),
            400: openapi.Response(
                description='Validation Error',
                schema=ErrorSerializer,
                examples={'application/json': {'email': ['Invalid email address']}}
            )
        }
    )
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
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='Updates the user\'s avatar.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'avatar': openapi.Schema(type=openapi.TYPE_FILE, description='New avatar file')
            },
            required=['avatar']
        ),
        responses={
            200: openapi.Response(
                description='Avatar updated successfully',
                schema=MessageSerializer,
                examples={'application/json': {'message': 'Avatar updated successfully.'}}
            ),
            400: openapi.Response(
                description='Validation Error',
                schema=ErrorSerializer,
                examples={'application/json': {'avatar': ['This field is required.']}}
            )
        }
    )
    def post(self, request):
        user = request.user
        if 'avatar' not in request.FILES:
            return Response({'avatar': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AvatarUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Avatar updated successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='Fetches message history between the authenticated user and a specified user.',
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_PATH,
                description='The ID of the user to fetch the message history with.',
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description='Message history retrieved successfully',
                schema=PrivateMessageSerializer(many=True),
                examples={'application/json': [{'sender': 1, 'receiver': 2, 'message': 'Hello!'}]}
            )
        }
    )
    def get(self, request, user_id):
        messages = PrivateMessage.objects.filter(
            (models.Q(sender=request.user) & models.Q(receiver_id=user_id)) |
            (models.Q(sender_id=user_id) & models.Q(receiver=request.user))
        ).order_by('timestamp')
        serializer = PrivateMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='Sends a private message from the authenticated user.',
        request_body=PrivateMessageSerializer,
        responses={
            201: openapi.Response(
                description='Message sent successfully',
                schema=PrivateMessageSerializer,
                examples={'application/json': {'sender': 1, 'receiver': 2, 'message': 'Hello!'}}
            ),
            400: openapi.Response(
                description='Validation Error',
                schema=ErrorSerializer,
                examples={'application/json': {'message': ['This field is required.']}}
            )
        }
    )
    def post(self, request):
        serializer = PrivateMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateActivityView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='Creates new activity',
        request_body=ActivitySerializer,
    )
    def post(self, request):
        logger.debug("Creating new activity view:")
        user = request.user
        name = request.data['name']
        logger.debug(f"Activity name:{name}")
        query = Activity.objects.filter(user=user, name=name)
        if len(query) > 0:
            return Response(data={'message':'activity with such name already exists for this user'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = ActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            response = {'data': serializer.data, 'name': user.username}
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateActivityView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='Updates activity',
        request_body=ActivitySerializer,
    )
    def patch(self, request):
        logger.debug("Updating new activity view:")
        user = request.user
        name = request.data['old_name']
        activity = Activity.objects.get(user=user, name=name)

        activity.name = request.data['new_name']
        activity.save()
        response = {'name':activity.name, 'username': user.username}
        return Response(response, status=status.HTTP_200_OK)


class DeleteActivityView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='Deletes activity',
        request_body=ActivitySerializer,
    )
    def delete(self, request):
        user = request.user
        activity_name = request.data['name']

        activities = Activity.objects.filter(user=user, name=activity_name)
        if len(activities) == 0:
            return Response(data={'message':'there is no such activity'}, status=status.HTTP_400_BAD_REQUEST)
        for activity in activities:
            activity.delete()
        return Response(data={'message':f'activity {activity_name} has been deleted'}, status=status.HTTP_200_OK)


class GetActivitiesListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        activities = list(Activity.objects.filter(user=user))
        all_activities = []
        for activity in activities:
            dict = {}
            dict['name'] = activity.name
            dict['username'] = activity.user.username
            dict['minutes_spent_today'] = activity.minutes_spent_today
            dict['minutes_spent_this_week'] = activity.minutes_spent_this_week
            dict['minutes_spent_this_month'] = activity.minutes_spent_this_month
            dict['minutes_spent_in_total'] = activity.minutes_spent_in_total
            all_activities.append(dict)
        return Response(json.loads(json.dumps(all_activities, indent=4)), status=status.HTTP_200_OK)


class TimerUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        activity_name = request.data['name']
        minutes_spent = request.data['time']

        try:
            minutes_spent = int(minutes_spent)
        except:
            return Response(data={'message': 'error occurred during casting added time to integer'}, status=status.HTTP_400_BAD_REQUEST)

        activities = Activity.objects.filter(user=user, name=activity_name)

        if len(activities) == 0:
            return Response(data={'message': 'there is no such activity'}, status=status.HTTP_400_BAD_REQUEST)

        activity = activities.last()
        activity.add_time(minutes_spent)

        return Response(data={'message': f'{minutes_spent} minutes have been added for {activity.name} activity'}, status=status.HTTP_200_OK)