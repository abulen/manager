from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import EmployeeForm
from django.urls import reverse
from .models import Employee, Position
from django.views.generic.edit import FormView
from django.urls import reverse
# Create your views here.


class EmployeeView(FormView):
    template_name = 'employee/employee.html'
    form_class = EmployeeForm
#    success_url = reverse('employee:employee-list')


def create_employee(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EmployeeForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('employee:employee-list'))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = EmployeeForm()

    return render(request, 'employee/employee.html', {'form': form})


def edit_employee(request, employee_id=None):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EmployeeForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('employee:employee-list'))

    # if a GET (or any other method) we'll create a blank form
    else:
        try:
            if employee_id:
                emp = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            emp = None
        form = EmployeeForm(instance=emp)

    return render(request, 'employee/employee.html', {'form': form})
