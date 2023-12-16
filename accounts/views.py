from typing import Any
from django.views import View
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
import requests
from .forms import *
from django.views.generic.base import TemplateView
from fantasy.models import Article

from core.mixins import CustomLoginRequiredMixin


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['articles'] = Article.objects.all()[:3] if Article.objects.exists() else None
        return context

class AboutView(TemplateView):
    template_name = 'about.html'


# Registration View
class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        context = {'form': form}
        return render(request, 'accounts/register.html', context)

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            if Account.objects.filter(username=email.split('@')[0]):
                messages.error(request, 'A user with given email already exists. Please try with new email or recover your old one.')
                context = {'form': form}
                return render(request, 'accounts/register.html', context)
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # user_activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            return redirect('/login/?command=verification&email=' + email)

        context = {'form': form}
        return render(request, 'accounts/register.html', context)

# Login View
class LoginView(View):
    def get(self, request):
        return render(request, 'accounts/login.html')

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)

        if user is not None:

            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('accounts:edit_profile')
        else:
            messages.error(request, 'Invalid login credentials')
        return render(request, 'accounts/login.html')

# Logout View
class LogoutView(View, CustomLoginRequiredMixin):
    def get(self, request):
        auth.logout(request)
        messages.success(request, "You are now logged out!")
        return redirect('accounts:login')

# Activation View
class ActivateView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Account._default_manager.get(pk=uid)
        except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Congratulations! Your account is now activated.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid activation link')
            return redirect('accounts:register')


# Forgot Password View
class ForgotPasswordView(View):
    def get(self, request):
        return render(request, 'accounts/forgotPassword.html')

    def post(self, request):
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Please reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('accounts:forgotPassword')

# Reset Password Validation View
class ResetPasswordValidateView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Account._default_manager.get(pk=uid)
        except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            request.session['uid'] = uid
            messages.success(request, 'Please reset your password')
            return redirect('accounts:resetPassword')
        else:
            messages.error(request, 'This link has expired!')
            return redirect('accounts:login')

# Reset Password View
class ResetPasswordView(View):
    def get(self, request):
        return render(request, 'accounts/resetPassword.html')

    def post(self, request):
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful!')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('accounts:resetPassword')

# Edit Profile View
class EditProfileView(CustomLoginRequiredMixin, View):
    def get(self, request):
        user_form = UserProfileForm(instance=request.user)
        try:
            current_profile = UserProfile.objects.get(user=request.user)
        except Exception as e:
            current_profile = UserProfile.objects.create(user=request.user)
            pass
        context = {'user_form': user_form, 'current_profile': current_profile, 'curr_nav': 'profile'}
        return render(request, 'accounts/edit_profile.html', context=context)

    def post(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(
                user=request.user
            )
    
        user_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid():
            user_form.save()

            new_password = request.POST['password']
            confirm_password = request.POST['confirm_password']
            user = self.request.user
            if new_password and confirm_password:
                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                else:
                    messages.error(request, 'Two passwords do not match.')
                    return redirect('edit_profile')
            messages.success(request, 'Your Profile Has Been Updated')
            return redirect('accounts:edit_profile')
        else:
            print('form is not valid...')
            print(user_form.errors)
            
            return redirect('accounts:edit_profile')

# Change Password View
class ChangePasswordView(View, CustomLoginRequiredMixin):
    def get(self, request):
        return render(request, 'accounts/change_password.html')

    def post(self, request):
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password updated successfully.')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Please enter a valid current password')
                return redirect('accounts:change_password')
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('accounts:change_password')
