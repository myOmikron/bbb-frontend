"use strict";

function onReady(callbackFunction){
    if (document.readyState !== 'loading') {
        callbackFunction();
    } else {
        document.addEventListener("DOMContentLoaded", callbackFunction);
    }
}

onReady(function() {
    // Template for chat messages
    var TEMPLATE = "" +
    "<div class='message'>" +
    "    <div class='messageColor' style='background-color: $COLOR;'>$ID</div>" +
    "    <div class='messageContent'>" +
    "        <h3>$USER</h3>" +
    "        $MESSAGE" +
    "    </div>" +
    "</div>";

    // Helper object and function to create objects from template
    var parser = document.createElement("div");
    function parse(html) {
        parser.innerHTML = html;
        return parser.firstChild;
    }

    function setupSocket() {
        var url = window.location;
        var protocol = url.protocol.replace("http", "ws");

        socket = new WebSocket(protocol+"//"+url.host+url.pathname);

        socket.onopen = function() {};

        socket.onmessage = function(event) {
            var data = JSON.parse(event.data);
            if (data.type === "chat.message") {
                onMessage(data);
            } else if (data.type === "chat.redirect") {
                onRedirect(data);
            } else if (data.type === "chat.update") {
                onUpdate(data);
            } else if (data.type === "chat.reload") {
                onReload(data);
            } else {
                console.error("Incoming WebSocket json object is of unknown type: '"+data.type+"'");
            }
        };

        socket.onerror = function(event) {
            console.error(event);
        };

        socket.onclose = function() {
            setTimeout(setupSocket, 1000);
        };
    }

    function sendMessage(message) {
        socket.send(JSON.stringify({
            type: "chat.message",
            message: message,
        }));
    }

    function onReload(obj) {
        tryReconnect();
    }

    function onUpdate(obj) {
        viewers.innerHTML = "" + obj.viewers;
    }

    function onRedirect(obj) {
        window.location = obj.url;
    }

    function onMessage(obj) {
        messages.insertBefore(parse(
            TEMPLATE
            .replace("$COLOR", "#00F")
            .replace("$ID", obj.user_name.slice(0, 2))
            .replace("$USER", obj.user_name)
            .replace("$MESSAGE", obj.message)
        ), messages.firstChild);
    }

    var viewers = document.getElementById("viewers");
    var messages = document.getElementsByClassName("messageChatContent")[0];
    var textarea = document.getElementById("chatTextarea");
    var button = document.getElementById("chatSendButton");

    if (!textarea) {
        console.error("Couldn't find chat's textarea");
    }
    if (!button) {
        console.error("Couldn't find chat's send button");
    }
    if ((!button) && (!textarea)) {
        throw Error("Missing DOM elements! See previous logs!");
    }

    button.onclick = function(event) {
        if (textarea.value !== "") {
            sendMessage(textarea.value);
            textarea.value = "";
        }
    };
    textarea.onkeypress = function(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            button.click();
        }
    };

    var socket;
    setupSocket();

    var updateInterval = setInterval(function() {
        socket.send(JSON.stringify({
            type: "chat.update"
        }));
    }, 1000);
});
