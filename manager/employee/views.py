from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import EmployeeForm
from django.urls import reverse
from .models import Employee, Position
from django.views.generic.edit import FormView
from django.urls import reverse
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
# Create your views here.


class EmployeeListView(ListView):
    model = Employee
    context_object_name = 'employee_list'
    queryset = Employee.objects.active().order_by('position__id')
    template_name = 'employee/employee-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Create any data and add it to the context
        context['inactive_employee_list'] = Employee.objects.inactive()
        return context


class EmployeeEditView(UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name_suffix = ''

    def get_initial(self):
        initial = super().get_initial()
        emp = self.get_object()
        initial['username'] = emp.user.username
        initial['first_name'] = emp.user.first_name
        initial['last_name'] = emp.user.last_name
        initial['email'] = emp.user.email
        initial['is_sm'] = emp.position == Position.store_manager()
        initial['is_asm'] = emp.position == Position.assistant_store_manager()
        initial['status'] = emp.status
        return initial


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
