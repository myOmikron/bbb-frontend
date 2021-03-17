import hashlib
import json
import uuid

from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic.base import View, TemplateView
from rc_protocol import validate_checksum

from bbb_frontend import settings
from frontend.models import Channel


class Validate(View):
    def post(self, request, *args, **kwargs):
        if "name" not in request.POST:
            return HttpResponse("Bad Request", status=400)
        try:
            channel = Channel.objects.get(streaming_key=request.POST["name"])
        except Channel.DoesNotExist:
            return HttpResponse("Not valid", status=404)
        return HttpResponse("Ok")


class CloseChannelView(View):
    def post(self, request, *args, **kwargs):
        try:
            decoded = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "message": "Unable to parse json"}, status=400
            )
        if "meeting_id" not in decoded:
            return JsonResponse(
                {"success": False, "message": "Missing parameter: meeting_id"}, status=400
            )
        if "checksum" not in decoded:
            return JsonResponse(
                {"success": False, "message": "Missing parameter: checksum"}, status=400
            )
        if not validate_checksum(
                decoded,
                salt="closeChannel",
                shared_secret=settings.SHARED_SECRET,
                time_delta=settings.SHARED_SECRET_TIME_DELTA
        ):
            return JsonResponse(
                {"success": False, "message": "Checksum check was not successful"}, status=401
            )
        try:
            channel = Channel.objects.get(meeting_id=decoded["meeting_id"])
            # TODO Close connections to existing users
            channel.delete()
        except Channel.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Channel does not exist"}, status=400
            )
        return JsonResponse({"success": True, "message": "Channel was deleted"})


class OpenChannelView(View):
    def post(self, request, *args, **kwargs):
        try:
            decoded = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "message": "Unable to parse json"}, status=400
            )
        if "meeting_id" not in decoded:
            return JsonResponse(
                {"success": False, "message": "Missing parameter: meeting_id"}, status=400
            )
        if "checksum" not in decoded:
            return JsonResponse(
                {"success": False, "message": "Missing parameter: checksum"}, status=400
            )
        if not validate_checksum(
                decoded,
                salt="openChannel",
                shared_secret=settings.SHARED_SECRET,
                time_delta=settings.SHARED_SECRET_TIME_DELTA
        ):
            return JsonResponse(
                {"success": False, "message": "Checksum check was not successful"}, status=401
            )
        channel, created = Channel.objects.get_or_create(meeting_id=decoded["meeting_id"])
        if not created:
            return JsonResponse(
                {"success": False, "message": "Channel already exists"}, status=304
            )
        channel.streaming_key = str(uuid.uuid4())
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
        return redirect(f"/watch?session={request.GET['meeting_id']}")


class WatchView(TemplateView):
    template_name = "client.html"

    def get(self, request, *args, **kwargs):
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
        if "session" not in request.GET:
            return render(
                request, "info.html",
                {"info": "Missing parameter: meeting_id", "status": "Bad request", "code": "400"},
                status=400
            )
        user_name = request.session["user_name"]
        meeting_id = request.GET["session"]
        tmp_checksum = hashlib.sha512(f"{user_name}{meeting_id}{settings.SHARED_SECRET}".encode("utf-8")).hexdigest()
        if request.session["checksum"] != tmp_checksum:
            return render(
                request, "info.html",
                {"info": "You didn't pass the checksum check", "status": "Unauthorized", "code": "401"},
                status=401
            )
        return render(request, self.template_name)
