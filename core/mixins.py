from django.contrib  import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, CreateView, ListView
from .models import *
from django.http import JsonResponse


from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class CustomLoginRequiredMixin(LoginRequiredMixin):
    login_url = '/login/' 
    redirect_field_name = 'next' 

    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            if self.request.is_ajax():
                return JsonResponse({'error': 'Authentication required.', 'status': 401})
            else:
                messages.error(self.request, 'Please login to continue.')
                return super().handle_no_permission()
        else:
            return redirect(self.login_url)

class BaseMixin(object):
    def get_context_data(self, **kwargs):
        context = super(BaseMixin,self).get_context_data(**kwargs)
        return context

