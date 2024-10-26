from django.shortcuts import render, redirect
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView
from clock.serializers import RegisterSerializer, ErrorSerializer, MessageSerializer
import logging

logger = logging.getLogger(__name__)


def homePageRedirect(request):
    logger.info('Redirecting to the main page')
    return redirect('index')


def homePage(request):
    logger.debug('Displaying the main page')
    return render(request, 'homePage.html')


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
        return Response(serializer.errors, status=400)


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
