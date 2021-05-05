from django.urls import path
from frontend.views import *


urlpatterns = [
    path('api/v1/join', JoinView.as_view()),
    path('api/v1/openChannel', OpenChannelView.as_view()),
    path('api/v1/closeChannel', CloseChannelView.as_view()),
    path('api/v1/viewerCounts', ViewerCounts.as_view()),
    path('watch/<str:meeting_id>', WatchView.as_view())
]
