let reloading = false;

function resetPlayer() {
    if (!reloading) {
        reloading = true;
        try {
            console.info('[info] > Reseting media ...');
            player.error(null);
            player.src(player.currentSrc());
        } catch(err) {
            console.error(err);
        } finally {
            reloading = false;
        }
    }
}

let connecting;
function tryReconnect() {
    setInterval(function() {
        const error = player.error();
        console.debug(error);
        if (error === null) {
            clearInterval(connecting);
        } else {
            switch (error.code) {
                case error.MEDIA_ERR_NETWORK:
                    resetPlayer();
                    break;
                case error.MEDIA_ERR_SRC_NOT_SUPPORTED:
                    resetPlayer();
                    break;
            }
        }
    }, 5000);
}
