from django.urls import path
from frontend.views import *


urlpatterns = [
    path('join', JoinView.as_view()),
    path('watch', WatchView.as_view()),
]
