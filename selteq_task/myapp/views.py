from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from .models import Task
from .serializers import UserSerializer, LoginSerializer, TaskSerializer
from rest_framework import serializers
from django.db import IntegrityError

from celery import shared_task
from datetime import datetime, timedelta
from django.utils import timezone


@shared_task
def print_task_async(task_name):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Task '{task_name}' executed at: {current_time}")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    try:
        # Extract task_name from request data
        task_name = request.data.get('task_name', '')

        # Create a new Task associated with the authenticated user
        task = Task.objects.create(user=request.user, task_name=task_name)

        # Get the current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Serialize the task object
        task_serializer = TaskSerializer(task)

        # Prepare response data
        response_data = {
            'current_time': current_time,
            'task': task_serializer.data,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task_for_celery(request):
    try:
        # Extract task_name from the request data
        task_name = request.data.get('task_name', '')

        # Set the scheduled time to be 5 seconds from now
        scheduled_time = timezone.now() + timedelta(seconds=5)

        # Schedule the Celery task for execution at the specified time
        print_task_async.apply_async(args=[task_name], eta=scheduled_time)

        # Create a new Task associated with the authenticated user
        task = Task.objects.create(user=request.user, task_name=task_name)

        # Get the current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Serialize the task object
        task_serializer = TaskSerializer(task)

        # Prepare response data
        response_data = {
            'current_time': current_time,
            'task': task_serializer.data,
            'scheduled_time': scheduled_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tasks(request):
    try:
        tasks = Task.objects.filter(user=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    try:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except serializers.ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except IntegrityError as e:
        return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    try:
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(request, email=serializer.data['email'], password=serializer.data['password'])
            if user is not None:
                login(request, user)
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid login credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    try:
        request.auth.delete()  # Revoke the authentication token
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
