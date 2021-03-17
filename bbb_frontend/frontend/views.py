import hashlib

from django.shortcuts import redirect, render
from django.views.generic.base import View, TemplateView
from rc_protocol import validate_checksum

from bbb_frontend import settings
from frontend.models import Channel


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
                {"info": "Meeting does not exist on this server", "status": "Not found", "code": "404"},
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
