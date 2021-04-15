from django.contrib import admin
from django.urls import path, include

import frontend.urls
from chat.views import *
from frontend.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/join', JoinView.as_view()),
    path('api/v1/openChannel', OpenChannelView.as_view()),
    path('api/v1/closeChannel', CloseChannelView.as_view()),
    path('api/v1/startChat', StartChat.as_view()),
    path('api/v1/sendMessage', SendMessage.as_view()),
    path('api/v1/endChat', EndChat.as_view()),
    path('api/v1/viewerCount', ViewerCount.as_view()),
    path('', include(frontend.urls)),
]
