from django.urls import path
from .views import SyncMatchPointsView

app_name = 'fantasy'

urlpatterns = [
    path('sync-match-points/', SyncMatchPointsView.as_view(), name='sync-match-points'),
]
