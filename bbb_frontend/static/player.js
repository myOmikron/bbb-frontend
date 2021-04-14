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

document.getElementById("my-video").addEventListener('error', function(err) {
    const mediaError = err.currentTarget.error;
    switch(mediaError.code) {
        case mediaError.MEDIA_ERR_NETWORK:
            resetPlayer();
        break;
    }
 });