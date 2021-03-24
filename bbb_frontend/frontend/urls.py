from django.urls import path
from frontend.views import *


urlpatterns = [
    path('watch/<str:meeting_id>', WatchView.as_view()),
    path('internal/validate', Validate.as_view()),
]
