class Chat {
    constructor() {
        this.setupSocket();
    }

    setupSocket() {
        const url = window.location;
        const protocol = url.protocol.replace("http", "ws");
        const meeting_id = new URLSearchParams(url.search).get("meeting_id");

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

export let chat = null;
document.addEventListener("DOMContentLoaded", () => {
    chat = new Chat();
})
