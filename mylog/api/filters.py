import django_filters
from django_filters import FilterSet
from mylog.models import UserDailyLogs, Project, CustomUser


class ListUserFilter(FilterSet):
    user = django_filters.ModelChoiceFilter(method="user_filter", queryset=CustomUser.objects.all())
    date = django_filters.DateFilter(lookup_expr='icontains')
    project_name = django_filters.ModelChoiceFilter(method='project_filter', queryset=Project.objects.all())

    class Meta:
        model = UserDailyLogs
        fields = ['user', 'date', 'project_name']

    @classmethod
    def user_filter(self, queryset, value):
        return queryset.filter(user__username=value)

    @classmethod
    def project_filter(cls, queryset, name, value):
        return queryset.filter(project_name__name=value)