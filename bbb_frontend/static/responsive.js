function toggleChat() {
    let chat = document.getElementById("chat");
    let toggleButton = document.getElementById("toggleButton");
    if (toggleButton.style.backgroundColor === "transparent") {
        chat.style.display = "flex";
        toggleButton.style.backgroundColor = "#0F70D7";
        toggleButton.style.border = "2px solid #0F70D7";
    } else {
        chat.style.display = "none";
        toggleButton.style.backgroundColor = "transparent";
        toggleButton.style.border = "2px solid white";
    }
}