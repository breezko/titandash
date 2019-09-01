/**
 * botQueue.js
 *
 * Control all queued functions functionality present on the dashboard.
 */
let BotQueueConsumer = function() {
    /* Base Variables */
    let _this = this;
    let ajaxUrl = "/ajax/generate_queued";

    /* Instance Instance */
    let activeInstance = getActiveInstance();

    /* Consts */
    const SAVED = "saved";
    const FINISHED = "finished";

    /**
     * Generate a queued function through an AJAX request.
     */
    this.generateQueuedFunction = function(func) {
        let data = {
            function: func,
            instance: getActiveInstance()
        };

        $.ajax({
            url: ajaxUrl,
            dataType: "json",
            data: data,
            success: function(data) {
                sendAlert(
                    `FUNCTION: "${data["function"]}" HAS BEEN QUEUED SUCCESSFULLY...`,
                    elements.alertContainer
                );
            }
        })
    };

    /**
     * Configure and allocate all queued elements (jQuery).
     */
    this.configureQueueElements = function() {
        return {
            alertContainer: $("#alert-container"),
            queueContent: $("#dashboardQueueContent"),
            queueFunctionContainer: $("#dashboardQueueFunctionContainer"),
            queueCurrent: $("#dashboardQueueCurrent"),
            queueCurrentTableBody: $("#dashboardQueueCurrentTableBody")
        }
    };

    /**
     * When a queued function returns a successful response/event through our WebSocket, it means one of two things...
     *
     * 1. Function has been created... Newly generated and should be added to the currently queued functions.
     * 2. Function has been executed... Remove function from queued functions container.
     */
    this.success = function(event) {
        if (activeInstance !== getActiveInstance()) {
            activeInstance = getActiveInstance();
            elements.queueCurrentTableBody.empty();
        }

        let type = event["type"];
        let queued = event["queued"]["queued"];

        // Log has been saved/created, prepend to container...
        if (type === SAVED) {
            let elem = $(`
                <tr data-id="${queued["id"]}" style="display: none;">
                    <td><strong>${queued["id"]}</strong></td>
                    <td>${queued["title"]}</td>
                    <td>${queued["created"]}</td>
                </tr>
            `);
            elem.prependTo(elements.queueCurrentTableBody).fadeIn(100);
        }

        // Log has executed/finished, remove from container.
        if (type === FINISHED) {
            let id = queued["id"];
            elements.queueCurrent.find("tr").each(function() {
                if ($(this).data("id") === id) {
                    $(this).fadeOut(200, function() {
                        $(this).remove();
                    });
                }
            });
        }
    };

    this.generateWebSocket = function() {
        let socket = new WebSocket(`ws://${window.location.host}/ws/queued/`);
        socket.onmessage = function (e) {
            let message = JSON.parse(e.data);
            if (message["queued"]["instance_id"] === getActiveInstance()) {
                this.success(message);
            }
        }.bind(this);
        socket.onclose = function () {
            console.warn("BotQueued WebSocket Closed...")
        };
        console.log("BotQueued WebSocket Started Now...")
    };

    this.configureQueueButtons = function() {
        elements.queueFunctionContainer.find("button").each(function() {
            $(this).tooltip().off("click").click(function() {
                _this.generateQueuedFunction($(this).data("func"));
            });
        });
    };

    /* Consumer Elements */
    let elements = this.configureQueueElements();

    // Configure queue buttons (tooltips, click event).
    this.configureQueueButtons();
    // Generate WebSocket to update queued functions when modified.
    this.generateWebSocket();
};