const TEMPLATE = "" +
    "<div class='message'>" +
    "    <div class='messageColor' style='background-color: $COLOR;'>$ID</div>" +
    "    <div class='messageContent'>" +
    "        <h3>$USER</h3>" +
    "        $MESSAGE" +
    "    </div>" +
    "</div>";

const parser = document.createElement("div");
function parse(html) {
    parser.innerHTML = html;
    return parser.firstChild;
}

class Chat {
    constructor() {
        this.viewers = document.getElementById("viewers");
        this.messages = document.getElementsByClassName("messageChatContent")[0];
        this.textarea = document.getElementById("chatTextarea")
        this.button = document.getElementById("chatSendButton")
        if (!this.textarea) {
            console.error("Couldn't find chat's textarea")
        }
        if (!this.button) {
            console.error("Couldn't find chat's send button")
        }
        if ((!this.button) && (!this.textarea)) {
            throw Error("Missing DOM elements! See previous logs!");
        }
        this.button.onclick = (event) => {
            this.sendMessage(this.textarea.value);
            this.textarea.value = "";
        }
        this.textarea.onkeypress = (event) => {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                this.button.click();
            }
        };
        this.setupSocket();
        this.updateInterval = setInterval(() => {
            this.socket.send(JSON.stringify({
                type: "chat.update"
            }));
        }, 1000);
    };


    setupSocket() {
        const url = window.location;
        const protocol = url.protocol.replace("http", "ws");

        this.socket = new WebSocket(protocol+"//"+url.host+url.pathname);

        this.socket.onopen = () => {
        };

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === "chat.message") {
                this.onMessage(data);
            } else if (data.type === "chat.redirect") {
                this.onRedirect(data);
            } else if (data.type === "chat.update") {
                this.onUpdate(data);
            } else if (data.type === "chat.reload") {
                this.onReload(data);
            } else {
                console.error(`Incoming WebSocket json object is of unknown type: '${data.type}'`);
            }
        };

        this.socket.onerror = (event) => {
            console.error(event);
        };

        this.socket.onclose = () => {
            setTimeout(this.setupSocket.bind(this), 1000);
        };
    }

    sendMessage(message) {
        this.socket.send(JSON.stringify({
            type: "chat.message",
            message,
        }))
    }

    onReload({type}) {
        tryReconnect();
    }

    onUpdate({type, viewers}) {
        this.viewers.innerHTML = "" + viewers;
    }

    onRedirect({type, url}) {
        window.location = url;
    }

    onMessage({type, user_name, message}) {
        this.messages.appendChild(parse(
            TEMPLATE
            .replace("$COLOR", "#00F")
            .replace("$ID", user_name.slice(0, 2))
            .replace("$USER", user_name)
            .replace("$MESSAGE", message)
        ));
    }
}

function onReady(callbackFunction){
  if(document.readyState !== 'loading')
    callbackFunction()
  else
    document.addEventListener("DOMContentLoaded", callbackFunction)
}

export let instance = null;
onReady(() => {
    instance = new Chat();
});
