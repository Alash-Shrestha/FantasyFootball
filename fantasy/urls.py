from django.urls import path
from .views import *

app_name = 'fantasy'

urlpatterns = [
    path('sync-match-points/', SyncMatchPointsView.as_view(), name='sync-match-points'),
    path('my-team/<int:pk>/points', MyTeamView.as_view(), name='my-team-overall'),
]
