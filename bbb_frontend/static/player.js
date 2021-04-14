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

let connecting = setInterval(function() {
    const error = player.error();
    console.debug(error);
    if (!error) {
        clearInterval(connecting);
    }

    switch (error.code) {
        case error.MEDIA_ERR_NETWORK:
            resetPlayer();
            break;
    }
}, 1000);