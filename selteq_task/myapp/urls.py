# tasks/urls.py
from django.urls import path
from .views import get_tasks, register, user_login, user_logout, create_task, create_task_for_celery

urlpatterns = [
    path('create/task/', create_task, name='create/task'),
    path('get/tasks/', get_tasks, name='get/tasks'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    # This is for Celery
    path('create/task/', create_task_for_celery, name='create/task'),
]
