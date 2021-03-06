import hashlib
import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import urlencode
from django.views.generic.base import View, TemplateView
from rc_protocol import validate_checksum

from frontend.consumer import WebsocketConsumer
from frontend.counter import viewers
from frontend.models import Channel
from bbb_common_api.views import PostApiPoint, GetApiPoint

channel_layer = get_channel_layer()


class OnPublishView(View):

    def post(self, request, *args, **kwargs):
        if "name" not in request.POST:
            return HttpResponse("Bad Request", status=400)
        try:
            channel = Channel.objects.get(meeting_id=request.POST["name"])
        except Channel.DoesNotExist:
            return HttpResponse("Not valid", status=404)

        # Signal clients to reload
        WebsocketConsumer.reload_player(channel)

        return HttpResponse("OK", status=200)


class ViewerCounts(GetApiPoint):

    endpoint = "viewerCounts"
    required_parameters = []

    def safe_get(self, request, *args, **kwargs):
        if "meeting_id" in request.GET:
            ids = request.GET.getlist("meeting_id")
        else:
            ids = (channel.meeting_id for channel in Channel.objects.all())

        viewer_counts = {}
        for meeting_id in ids:
            viewer_counts[meeting_id] = viewers[meeting_id].value

        return JsonResponse(
            {"success": True, "message": "Success, see 'content'", "content": viewer_counts}
        )


class CloseChannelView(PostApiPoint):

    endpoint = "closeChannel"
    required_parameters = ["meeting_id"]

    def safe_post(self, request, parameters, *args, **kwargs):
        try:
            channel = Channel.objects.get(meeting_id=parameters["meeting_id"])
            WebsocketConsumer.redirect(channel)
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
        else:
            channel.welcome_msg = f"Welcome to {channel.meeting_id}!"
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
            channel = Channel.objects.get(meeting_id=meeting_id)
            welcome_msg = channel.welcome_msg
            if not welcome_msg:
                welcome_msg = settings.DEFAULT_WELCOME_MSG
        except Channel.DoesNotExist:
            return render(
                request, "info.html",
                {"info": "Channel does not exist!", "status": "Bad request", "code": "400"},
                status=400
            )

        ws_checksum = hashlib.sha512(f"{user_name}{meeting_id}{settings.CHAT_SECRET}".encode("utf-8")).hexdigest()
        ws_url = settings.CHAT_HOST + "?" + urlencode(
            {"user_name": user_name, "meeting_id": meeting_id, "checksum": ws_checksum}
        )

        return render(request, self.template_name, context={
            "session": meeting_id,
            "websocket_url": ws_url,
            "debug": settings.DEBUG,
            "welcome_msg": welcome_msg,
        })
