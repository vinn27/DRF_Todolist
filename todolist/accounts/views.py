from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth import logout
from django.views.decorators.http import require_POST, require_http_methods
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from .serializers import TaskSerializer
from rest_framework import generics
from .models import Task
import requests
import json


class TaskListCreateView(generics.ListCreateAPIView):
    # queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.all()
        userid = self.kwargs.get('userid')
        if userid is not None:
            try:
                user = User.objects.get(id=userid)
            except User.DoesNotExist:
                raise NotFound('User not found')
            queryset = queryset.filter(user=user)
        return queryset


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


def Userlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('todolist_UI')
        else:
            # Authentication failed, render login form with error
            return render(request, 'accounts/login.html', {'error_message': 'Invalid username or password.'})

        # Render login form for GET request or initial load
    return render(request, 'accounts/login.html')


@login_required
def todo(request):
    context = {}

    if request.method == "GET":
        url = f'http://127.0.0.1:8000/task/user/{request.user.id}/'
        response = requests.get(url)

        if response.status_code == 200:
            print("Successfully fetched the to-do list.")
            tasks = response.json()
            context['tasks'] = tasks
        else:
            print("Failed to fetch the to-do list.")
            context['tasks'] = []

        context['username'] = request.user.username

    elif request.method == "POST":
        url = f'http://127.0.0.1:8000/task/user/{request.user.id}/'
        task_data = {
            'title': request.POST.get('title'),
            'description': request.POST.get('description'),
            'user': request.user.id
        }

        # Check for duplicate task before creating a new one
        existing_tasks = requests.get(url).json()
        if any(task['title'] == task_data['title'] for task in existing_tasks):
            print("Task with the same title already exists.")
            return redirect('todolist_UI')  # Redirect to avoid duplicate submissions

        response = requests.post(url, json=task_data, headers={'Content-Type': 'application/json'})

        if response.status_code == 201:
            print("Successfully created a new task.")
        else:
            print("Failed to create a new task.")

        return redirect('todolist_UI')  # Redirect to avoid duplicate submissions

    return render(request, 'accounts/todolist.html', context)


@login_required
def logoutUser(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('login')


def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.create_user(username=username, email=email, password=password, first_name=name)
        login(request, user)
        return redirect('todolist_UI')
    return render(request, 'accounts/register.html')


@login_required
@require_POST
def delete_task(request):
    task_id = request.POST.get('task_id')
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('todolist_UI')


@require_http_methods(["POST"])
def update_task_api(request, user_id, task_id):
    if request.POST.get('_method') == 'PUT':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')

            task = get_object_or_404(Task, id=task_id, user_id=user_id)
            task.title = title
            task.description = description
            task.save()

            return redirect('todolist_UI')

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return redirect('todolist_UI')
