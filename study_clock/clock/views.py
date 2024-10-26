from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView
from clock.register_serializer import RegisterSerializer
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

    def get(self, request):
        logger.debug('Request to a protected view')
        return Response({'message': 'This is a protected view'}, status=200)
