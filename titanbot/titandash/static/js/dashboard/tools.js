/**
 * tools.js
 *
 * Handle all tools present on the dashboard and their click functionality.
 *
 * Currently supported tools:
 *
 *      - KillInstance: Destroy a stale bot instance if one is present. This happens when the web server crashes
 *                      unexpectedly or the Bot crashes without performing any cleanup.
 */
let ToolHandler = function() {
    /* Base Variables */
    let ajaxUrls = {
        killInstance: "/ajax/bot_instance/kill"
    };

    /**
     * Configure and allocate all tool elements (jQuery).
     */
    this.configureToolElements = function() {
        return {
            killInstanceButton: $("#killInstanceButton"),
            modalAlerts: $("#toolsModalAlerts")
        }
    };

    /**
     * Configure all supported tool buttons.
     */
    this.configureToolButtons = function() {
        this.configureKillButton();
    };

    /**
     * Configure the KillInstance tool/button.
     */
    this.configureKillButton = function() {
        elements.killInstanceButton.off("click").click(function () {
            let intervals = 0;
            $(this).prop("disabled", true).text("Launching");
            let loadInterval = setInterval(function () {
                intervals += 1;
                let btn = elements.killInstanceButton;
                btn.text(btn.text() + ".");
                if (intervals === 10) {
                    intervals = 0;
                    btn.text("Launching");
                }
            }, 500);

            // Launch AJAX to kill bot instance.
            $.ajax({
                url: ajaxUrls.killInstance,
                dataType: "json",
                data: {
                    instance: getActiveInstance()
                },
                success: function (data) {
                    clearInterval(loadInterval);
                    elements.killInstanceButton.text("Kill Instance").prop("disabled", false);

                    let alert = $(`<div class="alert alert-${data["status"]}" style="width: 100%; margin-bottom: 0; margin-top: 5px;">${data["message"]}</div>`);
                    alert.appendTo(elements.modalAlerts);
                    alert.fadeIn(750);

                    setTimeout(function () {
                        alert.fadeOut(500, function () {
                            $(this).remove();
                        });
                    }, 5000);
                }
            });
        });
    };

    /* Tool Elements */
    let elements = this.configureToolElements();

    // Configure all available tools and the buttons used to launch them.
    this.configureToolButtons();

    // Ensure tooltips are available on buttons.
    elements.killInstanceButton.tooltip();
};
