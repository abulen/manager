from django import forms
from schedule import tasks
from schedule import models
import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class CreateScheduleForm(forms.Form):
    start = forms.DateField(
        label="Schedule Start",
        widget=forms.TextInput(
            attrs={'type': 'date'}
        )
    )
    end = forms.DateField(
        label="Schedule End",
        widget=forms.TextInput(
            attrs={'type': 'date'}
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'schedule-form'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'schedule:schedule-create'

        self.helper.add_input(Submit('submit', 'Create'))
        date_min = models.Shift.last() + datetime.timedelta(days=1)
        self.fields['start'].widget.attrs['min'] = date_min
        date_min = date_min + datetime.timedelta(days=6)
        self.fields['end'].widget.attrs['min'] = date_min

    def clean(self):
        data = super().clean()
        start_date = data.get('start')
        end_date = data.get('end')
        day = start_date.weekday()
        if day != 6:
            start_date = start_date - datetime.timedelta(days=day + 1)
        day = end_date.weekday()
        if day != 5:
            end_date = end_date + datetime.timedelta(days=5 - day)
        data['start'] = start_date
        data['end'] = end_date
        return data


class CreateSSWForm(forms.Form):
    week = forms.CharField(
        label="Week",
        widget=forms.TextInput(
            attrs={'type': 'week'}
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'ssw-form'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'schedule:ssw-create'

        self.helper.add_input(Submit('submit', 'Create'))
        year, week, weekday = datetime.date.today().isocalendar()
        week_min = "{}-W{}".format(year, week)
        self.fields['week'].widget.attrs['min'] = week_min

    def clean(self):
        data = super().clean()
        week = data.get('week')
        start_datetime = datetime.datetime.strptime(week + '-1', "%Y-W%W-%w")
        jan_1 = datetime.date(start_datetime.year, 1, 1)
        dow = jan_1.weekday()
        if dow <= 4:
            start_date = start_datetime.date() - datetime.timedelta(days=7)
        else:
            start_date = start_datetime.date()
        end_date = start_date + datetime.timedelta(days=6)
        data['start'] = start_date
        data['end'] = end_date
        return data


class CreateLeaveForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=models.Employee.objects.active()
    )
    start = forms.DateField(
        label="Schedule Start",
        widget=forms.TextInput(
            attrs={'type': 'date'}
        )
    )
    end = forms.DateField(
        label="Schedule End",
        widget=forms.TextInput(
            attrs={'type': 'date'}
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'leave-form'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'schedule:leave-create'

        self.helper.add_input(Submit('submit', 'Create'))
        date_min = models.Shift.last() + datetime.timedelta(days=1)
        self.fields['start'].widget.attrs['min'] = date_min
        self.fields['end'].widget.attrs['min'] = date_min

