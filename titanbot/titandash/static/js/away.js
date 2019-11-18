/**
 * away.js
 *
 * Control the ability to fade the screen out and display a count
 * of time away from the screen, the bot may still be running at this point
 * but the screen will fade out to provide less screen burn from the dashboard.
 */
$(document).ready(function() {
    let timeSinceLastClick = new Date();
    let overlayShown = false;
    let stopwatch = null;

    $(document).click(function() {
        if (overlayShown) {
            hideOverlay();
            timeSinceLastClick = new Date();
        }
    });

    setInterval(function() {
        let diff = (timeSinceLastClick.getTime() - new Date().getTime());
        let secs = Math.abs(diff / 1000);
        if (secs >= 1200)
            if (!overlayShown) {
                displayOverlay();
            }
    }, 1000);

    // Display our overlay.
    function displayOverlay() {
        let awayOverlay = $("#away-overlay");
        let flex = $(".d-flex");

        awayOverlay.fadeIn(250);
        flex.delay(750).css({"filter": "blur(1px)"});

        overlayShown = true;
        stopwatch = new Stopwatch(timeSinceLastClick, null, $("#away-time"), "0");
    }

    // Hide our overlay.
    function hideOverlay() {
        let awayOverlay = $("#away-overlay");
        let awayTime = $("#away-time");
        let flex = $(".d-flex");

        awayOverlay.fadeOut(750, function() {
            if (stopwatch) {
                stopwatch.destroy();
                stopwatch = null;

                awayTime.remove();
                awayOverlay.append("<h1 class='text-center' id='away-time'></h1>")
            }
        });

        flex.css({"filter": ""});
        overlayShown = false;
    }
});