from django.contrib import admin
from django.urls import path, include

import frontend.urls
from frontend.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(frontend.urls)),
]
