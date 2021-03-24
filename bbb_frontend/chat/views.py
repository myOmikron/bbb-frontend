from asgiref.sync import async_to_sync
from django.http import JsonResponse
from channels.layers import get_channel_layer

from bbb_common_api.views import PostApiPoint
from frontend.models import Channel
from chat.models import Chat


channel_layer = get_channel_layer()


class StartChat(PostApiPoint):

    endpoint = "startChat"
    required_parameters = ["chat_id"]

    def safe_post(self, request, parameters, *args, **kwargs):
        callback_params = ["callback_uri", "callback_secret", "callback_id"]
        missing = []
        for param in callback_params:
            if param not in parameters:
                missing.append(param)

        if len(missing) == 1:
            return JsonResponse(
                {
                    "success": False,
                    "message": f"Parameter {missing[0]} is mandatory when enabling callbacks, but is missing"
                },
                status=403,
                reason=f"Parameter {missing[0]} is mandatory when enabling callbacks, but is missing"
            )
        elif len(missing) == 2:
            return JsonResponse(
                {
                    "success": False,
                    "message": f"Parameters {missing[0]} and {missing[1]} "
                               f"are mandatory when enabling callbacks, but are missing"
                },
                status=403,
                reason=f"Parameters {missing[0]} and {missing[1]} "
                       f"are mandatory when enabling callbacks, but are missing"
            )

        try:
            channel = Channel.objects.get(meeting_id=parameters["chat_id"])
        except Channel.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "No channel found. Please open it first."},
                status=404, reason="No channel found. Please open it first."
            )

        if Chat.objects.filter(channel=channel).count() > 0:
            return JsonResponse(
                {"success": False, "message": "Channel's chat has already been started."},
                status=304,
                reason="Channel's chat has already been started."
            )
        else:
            if len(missing) == 0:
                Chat.objects.create(
                    channel=channel,
                    callback_uri=parameters["callback_uri"],
                    callback_secret=parameters["callback_secret"],
                    callback_id=parameters["callback_id"],
                )
            else:
                Chat.objects.create(
                    channel=channel
                )
            return JsonResponse({"success": True, "message": "Added room successfully."})


class EndChat(PostApiPoint):

    endpoint = "endChat"
    required_parameters = ["chat_id"]

    def safe_post(self, request, parameters, *args, **kwargs):
        try:
            Chat.objects.get(channel__meeting_id=parameters["chat_id"]).delete()
            return JsonResponse(
                {"success": True, "message": "Chat has ended successfully"}
            )
        except Chat.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "No chat was found. Perhaps the channel was already closed?"},
                status=404, reason="No chat was found. Perhaps the channel was already closed?"
            )


class SendMessage(PostApiPoint):

    endpoint = "sendMessage"
    required_parameters = ["chat_id", "message", "user_name"]

    def safe_post(self, request, parameters, *args, **kwargs):
        try:
            chat = Chat.objects.get(channel__meeting_id=parameters["chat_id"])
        except Chat.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "No chat was found."},
                status=404, reason="No chat was found."
            )

        async_to_sync(channel_layer.group_send)(chat.channel.meeting_id, {
            "type": "chat.message",
            "user_name": parameters["user_name"],
            "message": parameters["message"]
        })

        return JsonResponse(
            {"success": True, "message": "Send message successfully."}
        )
