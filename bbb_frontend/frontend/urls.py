from django.urls import path
from frontend.views import *


urlpatterns = [
    path('watch', WatchView.as_view()),
    path('/api/v1/join', JoinView.as_view()),
]

