from django.urls import path
from . import views


app_name = 'accounts'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('activate/<uidb64>/<token>/', views.ActivateView.as_view(), name='activate'),
    path('forgotPassword/', views.ForgotPasswordView.as_view(), name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.ResetPasswordValidateView.as_view(), name='resetpassword_validate'),
    path('resetPassword/', views.ResetPasswordView.as_view(), name='resetPassword'),

    path('profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('change_password/', views.ChangePasswordView.as_view(), name='change_password'),
]
