from django import forms
from .models import Account, UserProfile
from django.core.validators import MinLengthValidator



class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control',
    }),
        validators=[MinLengthValidator(limit_value=6, message="Password must be at least 6 characters.")]
    )
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password'
    }),
        validators=[MinLengthValidator(limit_value=6, message="Password must be at least 6 characters.")]
    )

   
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        phone_number=cleaned_data.get('phone_number')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match!"
            )
        if  len(phone_number) != 10:
            raise forms.ValidationError(
                " Number of digit in Phone Number should be 10 "
            )
            
        if not phone_number.isdigit() or len(phone_number) != 10:
            raise forms.ValidationError(
                "Enter Valid Phone Number "
            )
        

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'



class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    full_name = forms.CharField(max_length=250, required=False)
    email = forms.EmailField(required=False)
    class Meta:
        model = UserProfile
        fields = ('profile_picture' ,)

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        full_name = self.cleaned_data.get('full_name', '').split(' ')
        instance.user.first_name = full_name[0] if full_name else ''
        instance.user.last_name = full_name[1] if len(full_name) > 1 else ''

        instance.user.email = self.cleaned_data.get('email', '')

        if commit:
            instance.user.save()  
            instance.save()  


        return instance