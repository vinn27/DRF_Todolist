from django.urls import path
from .views import *

urlpatterns =[
    path('', Userlogin, name="login"),
    path('todolist/', todo, name="todolist_UI"),
    path('logout/', logoutUser, name="logoutUser"),
    path('register/', register_user, name="register"),


    path('_task_list_/', TaskListCreateView.as_view(), name='task_list_create'),
    path('task/<int:userid>', TaskDetailView.as_view(), name='task_update'),
    path('task/user/<int:userid>/', TaskListCreateView.as_view(), name='task_list_by_user'),

    path('task/delete/', delete_task, name='task_delete_api'),
    path('user/<int:user_id>/task/<int:task_id>/', update_task_api, name='task_update_api'),







]