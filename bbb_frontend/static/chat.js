class Chat {
    constructor() {
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
        this.setupSocket();
    };


    setupSocket() {
        const url = window.location;
        const protocol = url.protocol.replace("http", "ws");
        const meeting_id = new URLSearchParams(url.search).get("session");

        this.socket = new WebSocket(`${protocol}//${url.host}/watch/${meeting_id}`);

        this.socket.onopen = () => {
        };

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === "chat.message") {
                this.onMessage(data);
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

    onMessage({type, user_name, message}) {
        // TODO
        console.log("" + user_name + " wrote:\n" + message)
    }
}


let instance = null;
try {
    instance = new Chat();
} catch {
    document.addEventListener("DOMContentLoaded", () => {
        instance = new Chat();
    })
}
export function getChat() {
    return instance;
}
