/**
 * botLogger.js
 *
 * Control the functionality that will append log records to the logging panel present
 * on the dashboard. They may also toggle the ability to have the logging panel auto scroll.
 */
let BotLoggerConsumer = function() {
    let autoScroll = true;

    /**
     * Configure and allocate all logger elements (jQuery).
     */
    this.configureGameScreenElements = function() {
        return {
            logAccordion: $("#dashboardLogAccordion"),
            logHeader: $("#dashboardLogHeader"),
            logBody: $("#dashboardLogBody"),
            logContent: $("#dashboardLogContent"),
            logInitial: $("#dashboardLogInitial"),
            logScroller: $("#dashboardLogScroller"),
            logTrash: $("#dashboardLogTrash")
        }
    };

    /**
     * On successful log record received, appending the record to log container.
     */
    this.success = function(data) {
        if (elements.logInitial.html() !== "") {
            elements.logInitial.html("");
            elements.logBody
                .removeClass("align-items-center")
                .removeClass("d-flex")
                .removeClass("justify-content-center");
            elements.logInitial.remove();
        }

        let html = $(`
            <code class="text-dark text-uppercase">
                <small>
                    <strong>${data["record"]["message"]}</strong>
                </small>
            </code>
            </br>
        `);

        html.appendTo(elements.logContent);

        if (autoScroll)
            elements.logBody.scrollTop(elements.logBody.prop("scrollHeight"));
    };

    /**
     * Generate a WebSocket that will be used to update the dashboard log panel in real time.
     */
    this.generateWebSocket = function() {
        let socket = new WebSocket(`ws://${window.location.host}/ws/log/`);
        socket.onmessage = function(e) {
            this.success(JSON.parse(e.data)["record"])
        }.bind(this);
        socket.onclose = function() {
            console.warn("BotLogger WebSocket Closed...")
        };
        console.log("BotLogger WebSocket Started Now...");
    };

    /**
     * Configure the click events that affect the log container.
     */
    this.configureClickEvents = function() {
         // Setup the trash button to remove all current log records.
        elements.logTrash.hover(function() {
            $(this).css("filter", "brightness(175%)");
        }, function() {
            $(this).css("filter", "brightness(100%)");
        }).mousedown(function() {
            $(this).css("filter", "brightness(30%)");
        }).mouseup(function() {
            $(this).css("filter", "brightness(100%)");
        }).click(function() {
            if (elements.logInitial.html() === "") {
                elements.logBody.find(".text-dark").remove().find("br").remove()
                    .addClass("align-items-center")
                    .addClass("d-flex")
                    .addClass("justify-content-center");
                elements.logInitial.html(`<h5>Log records will appear here as they are emitted...`);
            }
        });

        // Setup the scroll button to enable/disable auto scrolling.
        elements.logScroller.click(function() {
            elements.logScroller.toggleClass("active");
            if (elements.logScroller.hasClass("active")) {
                autoScroll = true;
                elements.logScroller.addClass("text-success").removeClass("text-dark");
            } else {
                autoScroll = false;
                elements.logScroller.addClass("text-dark").removeClass("text-success");
            }
        });
    };

    /* Consumer Elements */
    let elements = this.configureGameScreenElements();

    // Configure log click events.
    this.configureClickEvents();
    // Generate log web socket.
    this.generateWebSocket();
};