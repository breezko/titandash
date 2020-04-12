/**
 * botGameScreen.js
 *
 * Control the functionality that allows a user to take snapshots of their current in game
 * screen and stream them to the dashboard.
 */
let BotScreenManager = function() {
    /* Base Variables */
    let ajaxUrl = "/ajax/game_screen";
    let interval = null;
    let stopped = true;

    /**
     * Configure and allocate all game screen elements (jQuery).
     */
    this.configureGameScreenElements = function() {
        return {
            screenHeaderLink: $("#dashboardScreenHeaderCollapse"),
            screenStop: $("#dashboardScreenStop"),
            screenStart: $("#dashboardScreenStart"),
            screenImage: $("#dashboardScreenImage")
        }
    };
    /**
     * Start the interval to grab current screen grab from the server every second.
     */
    this.startInterval = function() {
        elements.screenHeaderLink.click();
        clearInterval(interval);
        stopped = false;
        interval = setInterval(function() {
            $.ajax({
                url: ajaxUrl,
                dataType: "json",
                data: {instance: getActiveInstance()},
                success: function(data) {
                    if (!stopped) {
                        if (elements.screenImage.css("display") === "none")
                            elements.screenImage.css({display: "block"}).fadeIn(100);

                        // Setting the image to our Base64 encoded image string.
                        elements.screenImage.attr("src", data["src"])
                    }
                }
            });
        }, 100);
    };
    /**
     * Stop the interval and reset the image present.
     */
    this.stopInterval = function() {
        elements.screenHeaderLink.click();
        clearInterval(interval);
        stopped = true;
        setTimeout(function() {
            elements.screenImage.fadeOut(250, function() {
                $(this).attr("src", "");
            });
        }, 1500);
    };

    /**
     * Configure the click events that control the showing and hiding of the game screen panel.
     */
    this.configureClickEvents = function() {
        elements.screenStop.off("click").click(function () {
            if (!elements.screenStop.hasClass("text-success")) {
                elements.screenStop.toggleClass("text-dark");
                elements.screenStop.toggleClass("text-success");
                elements.screenStart.toggleClass("text-success");
                elements.screenStart.toggleClass("text-dark");

                // Stopping the interval completely.
                this.stopInterval()
            }
        }.bind(this));

        elements.screenStart.off("click").click(function () {
            if (!elements.screenStart.hasClass("text-success")) {
                elements.screenStart.toggleClass("text-dark");
                elements.screenStart.toggleClass("text-success");
                elements.screenStop.toggleClass("text-success");
                elements.screenStop.toggleClass("text-dark");

                // Starting the interval infinitely (until stopped).
                this.startInterval();
            }
        }.bind(this));
    };

    /* Manager Elements */
    let elements = this.configureGameScreenElements();

    // Configure click events for displaying and screen capping
    // the screen in game.
    this.configureClickEvents();
};