from django.contrib import admin

from frontend.models import Channel


# Register your models here.
@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    pass
