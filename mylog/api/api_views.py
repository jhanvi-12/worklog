import csv
import datetime
from http import HTTPStatus
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.core.validators import EMPTY_VALUES
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from drf_excel.mixins import XLSXFileMixin
from drf_excel.renderers import XLSXRenderer
from rest_framework import generics
from rest_framework.generics import ListAPIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

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
        breakpoint()
        serializer = RegisterSerializer(data=request.data)  # serializer obj and send parsed data
        if serializer.is_valid(raise_exception=True):  # validate if is valid or not
            group = Group.objects.get(id=request.data['group'])
            user = serializer.save()
            user.groups.add(group)
            Response(serializer.data, status=HTTPStatus.CREATED)
            messages.success(self.request, USER_CREATED)
            return redirect('mylog:login')
        messages.error(self.request, USER_REGISTER_ERROR)
        return redirect('mylog:register')


class UserLoginView(APIView):
    """
    user login view
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'login.html'

    def get(self, request):
        serializer = LoginSerializer()
        return Response({'serializer': serializer, 'style': serializer.style})

    def post(self, request, *args, **kwargs):
        breakpoint()
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if 'user' in serializer.validated_data:
                user = serializer.validated_data['user']
                login(request, user)
                messages.success(self.request, USER_LOGIN)
                if request.user.groups.filter(name="Admin").exists():
                    return redirect('mylog:get_admin_option')
                return redirect('mylog:daily_log')
        messages.error(self.request, INVALID_LOGIN_CREDENTIAL)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)


class UserDailyLogsView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'daily_log_update.html'

    def get(self, request):
        serializer = UserLogSerializer()
        return Response({'serializer': serializer, 'style': serializer.style})

    def post(self, request, *args, **kwargs):
        serializer = UserLogSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            Response({'user': serializer.data}, status=HTTPStatus.CREATED)
            messages.success(self.request, USER_LOG_CREATED)
            return redirect('mylog:daily_log')
        messages.error(self.request, INVALID_LOGIN_CREDENTIAL)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST, template_name='mylog:daily_log')


class CreateProjectView(APIView):
    """ class for project creation """
    def post(self, request, format=None):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'serializer': serializer.data}, status=HTTPStatus.CREATED)
        return Response({'error': serializer.errors}, status=HTTPStatus.BAD_REQUEST)


class CreateTaskView(APIView):
    """ class for task creation """
    def post(self, request, format=None):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'serializer': serializer.data}, status=HTTPStatus.CREATED)
        return Response({'error': serializer.errors}, status=HTTPStatus.BAD_REQUEST)


class ListUserView(ListAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_log_list.html'
    context_object_name = 'users_list'
    serializer_class = ListUserSerializer
    paginate_by = 5

    def get(self, request, *args, **kwargs):
        queryset = UserDailyLogs.objects.all()
        user = self.request.GET.get('user', None)
        project = self.request.GET.get('project', None)
        date = self.request.GET.get('date', None)
        logs_filter = ListUserFilter(self.request.GET, queryset=queryset)
        if (user or project or date) is not None:
            if date in EMPTY_VALUES:
                date_obj = None
            else:
                date_obj = datetime.datetime.strptime(date, '%m/%d/%Y').date()
            filter_queryset = logs_filter.qs.filter(Q(user__username=user)
                                                    | Q(project_name__name=project)
                                                    | Q(date=date_obj))
            users = self.get_users_filter_paginate_queryset(filter_queryset)
            return Response({'users': users}, template_name='user_log_list.html')
        users = self.get_users_filter_paginate_queryset(queryset)
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


class DailyUpdateExcelView(XLSXFileMixin, ReadOnlyModelViewSet):
    """ class for generating spreadsheet for daily update list"""
    queryset = UserDailyLogs.objects.all()
    serializer_class = UserLogSerializer
    renderer_classes = (XLSXRenderer, TemplateHTMLRenderer)
    template_name = 'daily_log_update.html'

    column_header = {
        'titles': [
            "Column_1_name",
            "Column_2_name",
            "Column_3_name",
        ],
        'column_width': [17, 30, 17],
        'height': 25,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        },
    }
    body = {
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': False,
                'color': 'FF000000',
            }
        },
        'height': 40,
    }
    column_data_styles = {
        'distance': {
            'alignment': {
                'horizontal': 'right',
                'vertical': 'top',
            },
            'format': '0.00E+00'
        },
        'created_at': {
            'format': 'd.m.y h:mm',
        }
    }

    def get(self, request):
        serializer = UserLogSerializer()
        return Response({'serializer': serializer, 'style': serializer.style})