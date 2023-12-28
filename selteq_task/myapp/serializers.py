from rest_framework import serializers
from .models import Task
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'task_name', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = get_user_model().objects.create(

            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(email=email, password=password)

        if user is not None:
            if user.is_active:
                return data
            else:
                raise serializers.ValidationError("User account is disabled.")
        else:
            raise serializers.ValidationError("Invalid login credentials")
