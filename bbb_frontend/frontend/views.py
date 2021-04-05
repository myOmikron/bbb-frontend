import hashlib
import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic.base import View, TemplateView
from rc_protocol import validate_checksum

from frontend.models import Channel
from bbb_common_api.views import PostApiPoint


channel_layer = get_channel_layer()
HttpResponseRedirect.allowed_schemes.append("rtmp")


class Validate(View):
    def post(self, request, *args, **kwargs):
        if "name" not in request.POST:
            return HttpResponse("Bad Request", status=400)
        try:
            channel = Channel.objects.get(streaming_key=request.POST["name"])
        except Channel.DoesNotExist:
            return HttpResponse("Not valid", status=404)
        return HttpResponseRedirect(f"rtmp://127.0.0.1/accept/{channel.meeting_id}", status=302)


class CloseChannelView(PostApiPoint):

    endpoint = "closeChannel"
    required_parameters = ["meeting_id"]

    def safe_post(self, request, parameters, *args, **kwargs):
        try:
            channel = Channel.objects.get(meeting_id=parameters["meeting_id"])
            if channel.chat:
                async_to_sync(channel_layer.group_send)(channel.meeting_id, {
                    "type": "chat.redirect",
                    "url": channel.redirect_url
                })
            channel.delete()
        except Channel.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Channel does not exist"}, status=400
            )
        return JsonResponse({"success": True, "message": "Channel was deleted"})


class OpenChannelView(PostApiPoint):

    endpoint = "openChannel"
    required_parameters = ["meeting_id"]

    def safe_post(self, request, parameters, *args, **kwargs):
        channel, created = Channel.objects.get_or_create(meeting_id=parameters["meeting_id"])
        if not created:
            return JsonResponse(
                {"success": False, "message": "Channel already exists"}, status=304
            )
        channel.streaming_key = str(uuid.uuid4())
        if "welcome_msg" in parameters:
            channel.welcome_msg = parameters["welcome_msg"]
        if "redirect_url" in parameters:
            channel.redirect_url = parameters["redirect_url"]
        channel.save()

        return JsonResponse(
            {"success": True, "message": "New Channel was created", "content": {"streaming_key": channel.streaming_key}}
        )


class JoinView(View):
    def get(self, request, *args, **kwargs):
        if "user_name" not in request.GET:
            return render(
                request, "info.html",
                {"info": "Missing parameter: user_name", "status": "Bad request", "code": "400"},
                status=400
            )
        if "meeting_id" not in request.GET:
            return render(
                request, "info.html",
                {"info": "Missing parameter: meeting_id", "status": "Bad request", "code": "400"},
                status=400
            )
        if "checksum" not in request.GET:
            return render(
                request, "info.html",
                {"info": "Missing parameter: checksum", "status": "Bad request", "code": "400"},
                status=400
            )
        if not validate_checksum(
                {
                    "checksum": request.GET["checksum"],
                    "meeting_id": request.GET["meeting_id"],
                    "user_name": request.GET["user_name"]
                }, settings.SHARED_SECRET, salt="join", time_delta=settings.SHARED_SECRET_TIME_DELTA
        ):
            return render(
                request, "info.html",
                {"info": "You didn't pass the checksum test", "status": "Unauthorized", "code": "401"},
                status=401
            )
        try:
            Channel.objects.get(meeting_id=request.GET["meeting_id"])
        except Channel.DoesNotExist:
            return render(
                request, "info.html",
                {"info": "Channel does not exist on this server", "status": "Not found", "code": "404"},
                status=404
            )

        user_name = request.GET["user_name"]
        meeting_id = request.GET["meeting_id"]
        request.session["checksum"] = hashlib.sha512(
            f"{user_name}{meeting_id}{settings.SHARED_SECRET}".encode("utf-8")
        ).hexdigest()
        request.session["user_name"] = request.GET["user_name"]
        return redirect(f"/watch/{request.GET['meeting_id']}")


class WatchView(TemplateView):
    template_name = "client.html"

    def get(self, request, *args, meeting_id="", **kwargs):
        if "checksum" not in request.session:
            return render(
                request, "info.html",
                {"info": "Missing parameter: checksum", "status": "Bad request", "code": "400"},
                status=400
            )
        if "user_name" not in request.session:
            return render(
                request, "info.html",
                {"info": "Missing parameter: user_name", "status": "Bad request", "code": "400"},
                status=400
            )

        user_name = request.session["user_name"]
        tmp_checksum = hashlib.sha512(f"{user_name}{meeting_id}{settings.SHARED_SECRET}".encode("utf-8")).hexdigest()
        if request.session["checksum"] != tmp_checksum:
            return render(
                request, "info.html",
                {"info": "You didn't pass the checksum check", "status": "Unauthorized", "code": "401"},
                status=401
            )
        try:
            welcome_msg = Channel.objects.get(meeting_id=meeting_id).welcome_msg
        except Channel.DoesNotExist:
            return render(
                request, "info.html",
                {"info": "Channel does not exist!", "status": "Bad request", "code": "400"},
                status=400
            )
        return render(request, self.template_name, context={
            "session": meeting_id,
            "debug": settings.DEBUG,
            "welcome_msg": welcome_msg,
        })
