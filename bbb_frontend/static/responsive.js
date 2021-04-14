function toggleChat() {
    let chat = document.getElementById("chat");
    let video = document.getElementById("stream");
    let toggleButton = document.getElementById("toggleButton");
    let width = window.innerWidth;
    if (width <= 680) {
        if (chat.style.display === "flex") {
            chat.style.display = "none";
            video.style.display = "";
            toggleButton.style.backgroundColor = "transparent";
            toggleButton.style.border = "2px solid white";
        } else {
            chat.style.display = "flex";
            video.style.display = "none";
            toggleButton.style.backgroundColor = "#0F70D7";
            toggleButton.style.border = "2px solid #0F70D7";
        }
    } else {
        if (chat.style.display === "none") {
            chat.style.display = "flex";
            toggleButton.style.backgroundColor = "#0F70D7";
            toggleButton.style.border = "2px solid #0F70D7";
        } else {
            chat.style.display = "none";
            toggleButton.style.backgroundColor = "transparent";
            toggleButton.style.border = "2px solid white";
        }
    }
}
