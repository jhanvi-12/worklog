from django.urls import path

from mylog.api.api_views import (
    UserLoginView, UserDailyLogsView,
    UseRegistrationView, ListUserView,
    AddDailyLogVieW, GetOptionView, CreateTaskView,
    CreateProjectView, CreateCSvFileView
)

app_name = 'mylog'

urlpatterns = [
    path('', UseRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('log/', UserDailyLogsView.as_view(), name='daily_log'),
    path('users/list/', ListUserView.as_view(), name='list'),
    path('add/log/', AddDailyLogVieW.as_view(), name='add_log'),
    path('create/csv/', CreateCSvFileView.as_view(), name='create_csv_view'),
    path('option/', GetOptionView.as_view(), name='get_admin_option'),
    path('create/project/', CreateProjectView.as_view(), name='create_project'),
    path('create/task/', CreateTaskView.as_view(), name='create_task'),
]
