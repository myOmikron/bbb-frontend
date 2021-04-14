function toggleChat() {
    var chat = document.getElementById("chat");
    var video = document.getElementById("stream");
    var toggleButton = document.getElementById("toggleButton");
    var width = window.innerWidth;
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

var vh = window.innerHeight * 0.01;
document.documentElement.style.setProperty('--vh', ""+vh+"px");

window.addEventListener('resize', function() {
  var vh = window.innerHeight * 0.01;
  document.documentElement.style.setProperty('--vh', ""+vh+"px");
});