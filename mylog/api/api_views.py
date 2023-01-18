import csv
import datetime
from http import HTTPStatus
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.core.validators import EMPTY_VALUES
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from drf_excel.mixins import XLSXFileMixin
from drf_excel.renderers import XLSXRenderer
from knox.views import LoginView
from rest_framework import generics, permissions
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from knox.views import LogoutView as KnoxLogoutView

from mylog.api.filters import ListUserFilter
from mylog.api.serializers import (
    LoginSerializer, UserLogSerializer, RegisterSerializer,
    ListUserSerializer, TaskSerializer, ProjectSerializer
)
from mylog.constants import (
    USER_CREATED, USER_LOGIN, USER_REGISTER_ERROR,
    INVALID_LOGIN_CREDENTIAL, USER_LOG_CREATED, INVALID_DETAILS, DAILY_LOG_CSV_COLUMNS
)
from mylog.models import UserDailyLogs, Project, Task


class GetOptionView(APIView):
    """ class when admin login, can see options to create project, task
    and user's list view ."""
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'admin_option.html'

    def get(self, request):
        serializer = TaskSerializer()
        return Response({'serializer': serializer, 'style': serializer.style})


class UseRegistrationView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'register.html'

    def get(self, request):
        serializer = RegisterSerializer()
        return Response({'serializer': serializer, 'style': serializer.style})

    def post(self, request, format=None):
        serializer = RegisterSerializer(data=request.data)  # serializer obj and send parsed data
        if serializer.is_valid():
            serializer.save()
            messages.success(self.request, USER_CREATED)
            return redirect(reverse('mylog:login'))
        else:
            errors = serializer.errors
            return Response({'serializer': serializer, 'errors': errors, 'style': serializer.style},
                            template_name='register.html')


class UserLoginView(LoginView):
    """
    user login view
    """
    permission_classes = (permissions.AllowAny, )
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'login.html'

    def get(self, request):
        serializer = LoginSerializer()
        return Response({'serializer': serializer, 'style': serializer.style})

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            if 'user' in serializer.validated_data:
                user = serializer.validated_data['user']
                login(request, user)
                messages.success(self.request, USER_LOGIN)
                # if request.user.groups.filter(name="Admin").exists():
                #     return redirect('mylog:get_admin_option')
                # elif request.user.groups.filter(name="Software Engineer").exists():
                #     return redirect('mylog:daily_log')
                return redirect(reverse('mylog:daily_log'))
            messages.error(self.request, INVALID_LOGIN_CREDENTIAL)
            return redirect(reverse('mylog:login'))
        except Exception as e:
            # messages.error(self.request, INVALID_LOGIN_CREDENTIAL)
            errors = serializer.errors
            return Response({'status': 'failed', 'errors': errors, 'style': serializer.style},
                            template_name='login.html')


class LogoutView(APIView):
    # renderer_classes = [TemplateHTMLRenderer]
    # template_name = 'login.html'

    def post(self, request, format=None):
        logout(request)
        return redirect(reverse('mylog:login'))


class UserDailyLogsView(CreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'daily_log_update.html'

    def get(self, request):
        if request.user.is_authenticated:
            serializer = UserLogSerializer()
            return Response({'serializer': serializer, 'style': serializer.style})
        else:
            return redirect(reverse('mylog:login'))

    def post(self, request, *args, **kwargs):
        breakpoint()
        if not request.user.is_authenticated:
            return redirect(reverse('mylog:login'))
        serializer = UserLogSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            messages.success(self.request, USER_LOG_CREATED)
            return redirect('mylog:daily_log')
        else:
            data = {
                'status': 'failed',
                'errors': serializer.errors,
                'style': serializer.style,
                'user': request.user
            }
            return Response(data, template_name='daily_log_update.html', status=HTTPStatus.BAD_REQUEST)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        first_project_tasks = Task.objects.filter(project=Project.objects.first()).values_list('id', flat=True)
        context.update({'request': self.request, 'initial': {'task': first_project_tasks}})
        return context


class CreateProjectView(APIView):
    """ class for project creation """
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'serializer': serializer.data}, status=HTTPStatus.CREATED)
        return Response({'error': serializer.errors}, status=HTTPStatus.BAD_REQUEST)


class CreateTaskView(APIView):
    """ class for task creation """
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'serializer': serializer.data}, status=HTTPStatus.CREATED)
        return Response({'error': serializer.errors}, status=HTTPStatus.BAD_REQUEST)


class ListUserView(ListAPIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_log_list.html'
    context_object_name = 'users_list'
    serializer_class = ListUserSerializer
    paginate_by = 5

    def get(self, request, *args, **kwargs):
        queryset = UserDailyLogs.objects.all()
        user = self.request.GET.get('user')
        project = self.request.GET.get('project')
        date = self.request.GET.get('date', None)
        if date in EMPTY_VALUES:
            date_obj = None
        else:
            date_obj = datetime.datetime.strptime(date, '%m/%d/%Y').date()

        if user:
            queryset = queryset.filter(user__username=user)
        if project:
            queryset = queryset.filter(project_name__name=project)
        if date_obj:
            queryset = queryset.filter(date=date_obj)

        page = self.request.GET.get('page')
        serializer = ListUserSerializer(queryset, many=True)
        paginator = Paginator(serializer.data, self.paginate_by)
        users = paginator.get_page(page)
        return Response({'users': users}, template_name='user_log_list.html')

    def get_users_filter_paginate_queryset(self, queryset):
        """
        function for user's filtered or not filtered queryset
        and applied it to paginator class
        """
        page = self.request.GET.get('page')
        serializer = ListUserSerializer(queryset, many=True)
        paginator = Paginator(serializer.data, self.paginate_by)
        users = paginator.get_page(page)
        return users


class AddDailyLogVieW(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    """ class for add task manually"""

    def post(self, request, *args, **kwargs):
        project = request.data.get('project_name')
        task = request.data.get('task')
        description = request.data.get('description')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        date = request.data.get('date')
        project_obj = Project.objects.create(name=project)
        task_obj = Task.objects.create(project=project_obj, title=task)
        daily_log_obj = UserDailyLogs.objects.create(
            user=request.user, date=date, project_name=project_obj,
            task=task_obj, description=description,
            start_time=start_time, end_time=end_time
        )
        if daily_log_obj:
            messages.success(self.request, USER_LOG_CREATED)
            return redirect('mylog:daily_log')
        messages.error(self.request, INVALID_DETAILS)
        return redirect('mylog:daily_log')


class CreateCSvFileView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_log_list.html'

    def post(self, request):
        queryset = UserDailyLogs.objects.all()
        # pass queryset to serializer class to get list format in response
        serializer = ListUserSerializer(queryset, many=True)
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(DAILY_LOG_CSV_COLUMNS)
        for row in serializer.data:
            writer.writerow(row.values())
        messages.success(self.request, "CSV file is created successfully!!")
        response['Content-Disposition'] = 'attachment; filename="daily_log.csv"'
        return response


class TaskListAPIView(APIView):
    def get(self, request, project_id):
        tasks = Task.objects.filter(project_name=project_id).values('id', 'task_name')
        return Response(tasks)

