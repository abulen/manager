from django import forms
from django.contrib.auth.models import User
from .models import Employee, Position


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')


class EmployeeForm(forms.ModelForm):
    username = forms.CharField(label="Username", max_length=150)
    first_name = forms.CharField(label="First Name", max_length=30)
    last_name = forms.CharField(label="Last Name", max_length=150)
    email = forms.EmailField(label="Email", required=False)
    password = forms.CharField(label="Password",
                               max_length=32,
                               widget=forms.PasswordInput,
                               required=False)
    v_password = forms.CharField(label="Verify Password",
                                 max_length=32,
                                 widget=forms.PasswordInput,
                                 required=False)
    is_sm = forms.BooleanField(label="Store Manager", required=False)
    is_asm = forms.BooleanField(label="Assistant Store Manager",
                                required=False)

    class Meta:
        model = Employee
        fields = ['username', 'first_name', 'last_name', 'email', 'password',
                  'v_password', 'is_sm', 'is_asm', 'status']

    def clean(self):
        cleaned_data = super().clean()
        is_sm = cleaned_data.get('is_sm')
        is_asm = cleaned_data.get('is_asm')
        password = cleaned_data.get('password', None)
        v_password = cleaned_data.get('v_password', None)

        if is_sm and is_asm:
            raise forms.ValidationError(
                "Cannot select employee as Store Manager and "
                "Assistant Store Manager"
            )
        if is_sm and Employee.store_manager().exists():
            raise forms.ValidationError(
                "Another employee is already assigned as Store Manager"
            )
        if is_asm and Employee.asm().exists():
            raise forms.ValidationError(
                "Another employee is already assigned as "
                "Assistant Store Manager"
            )
        if password and not v_password:
            raise forms.ValidationError(
                'Please Verify Password'
            )
        if password and v_password:
            if password != v_password:
                raise forms.ValidationError(
                    "Passwords do not match!"
                )

    def save(self, commit=True):
        if self.instance:
            instance = self.instance
        instance = self.instance if self.instance else Employee()
        if not instance.user:
            instance.user = User.objects.create_user(
                self.cleaned_data.get('username', None),
                self.cleaned_data.get('email', None),
                self.cleaned_data.get('password', None)
            )
        else:
            instance.user.username = self.cleaned_data.get('username', None)
            instance.user.email = self.cleaned_data.get('email', None)
            instance.user.password = self.cleaned_data.get('password', None)
        instance.user.first_name = self.cleaned_data.get('first_name', None)
        instance.user.last_name = self.cleaned_data.get('last_name', None)
        is_sm = self.cleaned_data.get('is_sm')
        is_asm = self.cleaned_data.get('is_asm')
        if is_sm:
            instance.position = Position.store_manager()
        elif is_asm:
            instance.position = Position.assistant_store_manager()
        else:
            instance.position = Position.sales_rep()
        status = self.cleaned_data.get('status', 'active')
        if status == 'active':
            instance.status = 'active'
            instance.user.is_active = True
        else:
            instance.status = 'inactive'
            instance.user.is_active = False
        if commit:
            instance.save()
        return instance


class CreateEmployeeForm(forms.Form):
    username = forms.CharField(label="Username", max_length=30)
    first_name = forms.CharField(label="First Name", max_length=30)
    last_name = forms.CharField(label="Last Name", max_length=30)
    email = forms.EmailField(label="Email", max_length=50, required=False)
    password = forms.CharField(label="Password",
                               max_length=32,
                               widget=forms.PasswordInput,
                               required=False)
    v_password = forms.CharField(label="Verify Password",
                                 max_length=32,
                                 widget=forms.PasswordInput,
                                 required=False)
    is_sm = forms.BooleanField(label="Store Manager", required=False)
    is_asm = forms.BooleanField(label="Assistant Store Manager",
                                required=False)

    def clean(self):
        cleaned_data = super().clean()
        is_sm = cleaned_data.get('is_sm')
        is_asm = cleaned_data.get('is_asm')
        password = cleaned_data.get('password', None)
        v_password = cleaned_data.get('v_password', None)

        if is_sm and is_asm:
            raise forms.ValidationError(
                "Cannot select employee as Store Manager and "
                "Assistant Store Manager"
            )
        if is_sm and Employee.store_manager().exists():
            raise forms.ValidationError(
                "Another employee is already assigned as Store Manager"
            )
        if is_asm and Employee.asm().exists():
            raise forms.ValidationError(
                "Another employee is already assigned as "
                "Assistant Store Manager"
            )
        if password and not v_password:
            raise forms.ValidationError(
                'Please Verify Password'
            )
        if password and v_password:
            if password != v_password:
                raise forms.ValidationError(
                    "Passwords do not match!"
                )


