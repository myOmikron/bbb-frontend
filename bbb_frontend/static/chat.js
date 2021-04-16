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

        function onEvent(event) {
            if (event.type === "chat.message") {
                onMessage(event);
            } else if (event.type === "chat.redirect") {
                onRedirect(event);
            } else if (event.type === "chat.update") {
                onUpdate(event);
            } else if (event.type === "chat.reload") {
                onReload(event);
            } else {
                console.error("Incoming WebSocket json object is of unknown type: '"+event.type+"'");
            }
        }
        socket.onmessage = function(event) {
            var data = JSON.parse(event.data);
            if (Array.isArray(data)) {
                for (var i = 0; i < data.length; i++) {
                    onEvent(data[i]);
                }
            } else {
                onEvent(data);
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
        if (viewers.innerHTML != obj.viewers) {
            viewers.innerHTML = "" + obj.viewers;
        }
    }

    function onRedirect(obj) {
        window.location = obj.url;
    }

    var overflowing = false;
    function onMessage(obj) {
        messages.insertBefore(parse(
            TEMPLATE
            .replace("$COLOR", "#01579b")
            .replace("$ID", obj.user_name.slice(0, 2))
            .replace("$USER", obj.user_name)
            .replace("$MESSAGE", obj.message)
        ), messages.firstChild);

        if (!overflowing) {
            if (messages.scrollHeight > messages.offsetHeight) {
                document.getElementsByClassName("viewerCountContent")[0].classList.add("overflowShadow");
                overflowing = true;
            }
        }
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
        if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                type: "chat.update"
            }));
        }
    }, 1000);
});
