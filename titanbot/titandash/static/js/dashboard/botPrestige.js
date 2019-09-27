/**
 * botPrestige.js
 *
 * Control the functionality that will append/grab prestiges while the bot
 * is running to display the most recent prestige values.
 */
let BotPrestigeConsumer = function() {
    /* Base Variables */
    let ajaxUrl = "/ajax/prestige";

    /* Active Instance */
    let activeInstance = getActiveInstance();

    /* Consts */
    const RUNNING = "RUNNING";
    const PAUSED = "PAUSED";

    /**
     * Add a single row to the list of the most recent prestiges.
     */
    this.addTableRow = function(data) {
        if (data["artifact"] === "N/A") {
            data["artifact"] = "<td>N/A</td>";
        } else {
             data["artifact"] = `
                <td>
                    <img height="25" width="25" src="${data["artifact"]["path"]}" alt="${data["artifact"]["path"]}">
                    ${data["artifact"]["title"]}
                </td>
            `;
        }

        let row = $(`
            <tr data-duration="${data["duration"]["seconds"]}" data-stage="${data["stage"]}" style="display: none;">
                <td>${data["timestamp"]["formatted"]}</td>
                <td>${data["duration"]["formatted"]}</td>
                <td>${data["stage"]}</td>
                ${data["artifact"]}
            </tr>
        `);
        row.prependTo(elements.prestigeTableBody).fadeIn(250);
    };

    /**
     * Main success function.
     *
     * Control all functionality related to the dynamic updating of recent prestiges
     * present on the dashboard.
     */
    this.socketSuccess = function(data) {
        let _data = data;
        this.addTableRow(data);

        // Grab average values through an ajax request.
        let totalSeconds = 0;
        let totalStages = 0;
        let totalPrestiges = 0;
        let validStages = 0;
        let validSeconds = 0;

        elements.prestigeTableBody.find("tr").each(function() {
            totalPrestiges += 1;
            if ($(this).data("stage") !== "N/A") {
                totalStages += parseInt($(this).data("stage"));
                validStages += 1;
            }
            if ($(this).data("duration") !== "N/A") {
                totalSeconds += parseInt($(this).data("duration"));
                validSeconds += 1;
            }
        });

        $.ajax({
            url: ajaxUrl,
            dataType: "json",
            data: {
                type: "AVG",
                totalSeconds: totalSeconds,
                totalStages: totalStages,
                validSeconds: validSeconds,
                validStages: validStages
            },
            success: function(data) {
                elements.prestigeAvgDuration.fadeOut(150, function() {
                    $(this).text(data["avgPrestigeTime"]).fadeIn(150);
                });
                elements.prestigeAvgStage.fadeOut(150, function() {
                    $(this).text(data["avgPrestigeStage"]).fadeIn(150);
                });
                elements.prestigeThisSession.fadeOut(150, function() {
                    $(this).text(totalPrestiges).fadeIn(150);
                });
                elements.prestigeLastArtifactValue.fadeOut(150, function() {
                    if (_data["artifact"] === "N/A") {
                        $(this).html("N/A");
                    } else {
                        $(this).html(`
                            <img style="margin-right: 5px;" height="25" width="25" src="${_data["artifact"]["path"]}" alt="${_data["artifact"]["image"]}">
                            ${_data["artifact"]["title"]}
                        `).fadeIn(150);
                    }
                });
            }
        });
    };

    /**
     * Initial success function.
     *
     * Control all functionality related to the initial prestiges retrieval based
     * on whether or not a BotInstance is currently running.
     */
    this.initialSuccess = function(data) {
        // Emptying the table on every initial request.
        elements.prestigeTableBody.empty();
        data["prestiges"].forEach(function(item) {
            this.addTableRow(item);
        }.bind(this));

        if (data["prestiges"].length > 0) {
            elements.prestigeAvgDuration.text(data["avgPrestigeTime"]);
            elements.prestigeAvgStage.text(data["avgPrestigeStage"]);
            elements.prestigeThisSession.text(data["totalPrestiges"]);

            if (data["lastArtifact"] === null) {
                elements.prestigeLastArtifactValue.html("N/A");
            } else {
                elements.prestigeLastArtifactValue.html(`
                    <img height="25" width="25" src="${data["lastArtifact"]["path"]}" alt="${data["lastArtifact"]["image"]}">
                    ${data["lastArtifact"]["title"]}
                `);
            }
        }
    }.bind(this);

    /**
     * Configure and allocate all prestige elements (jQuery).
     */
    this.configurePrestigeElements = function() {
        return {
            instanceState: $("#dashboardBotStateValue"),
            instanceSession: $("#dashboardBotSessionValue"),

            prestigeAccordion: $("#dashboardPrestigeAccordion"),
            prestigeHeader: $("#dashboardPrestigeHeader"),
            prestigeLoader: $("#dashboardPrestigeLoader"),
            prestigeBody: $("#dashboardPrestigeBody"),
            prestigeContent: $("#dashboardPrestigeContent"),
            prestigeInitial: $("#dashboardPrestigeInitial"),
            prestigeTableBody: $("#dashboardPrestigeTableBody"),
            prestigeAvgDuration: $("#dashboardPrestigeAvgDurationValue"),
            prestigeAvgStage: $("#dashboardPrestigeAvgStageValue"),
            prestigeThisSession: $("#dashboardPrestigeThisSessionValue"),
            prestigeLastArtifactValue: $("#dashboardPrestigeLastArtifactValue")
        }
    };

    /**
     * Generate a WebSocket that will be used to update recent prestiges in the
     * dashboard in real time.
     */
    this.generateWebSocket = function() {
        let socket = new WebSocket(`ws://${window.location.host}/ws/prestige/`);
        socket.onmessage = function(e) {
            let message = JSON.parse(e.data);
            if (message["prestige"]["instance_id"] === getActiveInstance()) {
                this.socketSuccess(message["prestige"]["prestige"]);
            }
        }.bind(this);
        socket.onclose = function() {
            console.warn("Prestige WebSocket Closed...")
        };
        console.log("Prestige WebSocket Started Now...")
    };

    // Setting a timeout to retrieve the initial Prestige data.
    setTimeout(function() {
        if (elements.instanceState.text() === RUNNING || elements.instanceState.text() === PAUSED) {
            $.ajax({
                url: ajaxUrl,
                dataType: "json",
                data: {
                    type: "PRESTIGES",
                    instance: getActiveInstance()
                },
                success: this.initialSuccess,
                complete: function () {
                    elements.prestigeLoader.fadeOut(150, function () {
                        $(this).remove();
                    })
                }
            })
        } else {
            elements.prestigeLoader.fadeOut(150, function() {
                $(this).remove();
                elements.prestigeInitial.fadeIn(150);
            });
        }
    }.bind(this), 1000);

    // Setting an interval to check for active session changes.
    setInterval(function() {
        if (getActiveInstance() !== activeInstance) {
            activeInstance = getActiveInstance();
            $.ajax({
                url: ajaxUrl,
                dataType: "json",
                data: {
                    type: "PRESTIGES",
                    instance: getActiveInstance()
                },
                success: this.initialSuccess,
            });
        }
    }.bind(this), 250);

    /* Consumer Elements */
    let elements = this.configurePrestigeElements();

    // Create WebSocket to modify/update dashboard prestiges.
    this.generateWebSocket();
};