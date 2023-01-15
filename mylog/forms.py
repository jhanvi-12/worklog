from django import forms
from django.contrib.auth.models import User

from mylog.api.serializers import ListUserSerializer
from mylog.models import Project, UserDailyLogs


class ListUserForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control inputDate",
                "placeholder": "DD-MM-YYYY",
            }
        ),
    )
    user = forms.ModelChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-control"
            },
        ),
        queryset=User.objects.all(),
        empty_label="Select User"
    )

    project_name = forms.ModelChoiceField(
        widget=forms.Select(
            attrs={
                "class": "form-control"
            },
        ),
        queryset=Project.objects.all(),
        empty_label="Select Project"
    )

    class Meta:
        model = UserDailyLogs
        fields = ["date", "user", "project_name"]

    def __init__(self, *args, **kwargs):
        breakpoint()
        super(ListUserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False