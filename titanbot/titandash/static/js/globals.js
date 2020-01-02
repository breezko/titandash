/**
 * globals.js
 *
 * Control the settings page within the web application.
 */
$(document).ready(function() {
    let ajaxUrls = {save: "/globals/save/"};
    let ajaxDataType = "json";

    /**
     * Configure and allocate all configuration elements needed (jQuery).
     */
    let configureGlobalElements = function() {
        return {
            form: $("#globalsForm"),
            failsafeSettings: $("#failsafe_settings"),
            eventSettings: $("#event_settings"),
            piholeAdSettings: $("#pihole_ad_settings"),
            saveButton: $("#saveGlobalsButton"),
            alertContainer: $("#alert-container")
        };
    };

    /**
     * Setup the json export functionality when the user presses the export button present on the page.
     */
    let setupJsonExport = function() {
        $("#exportGlobalsJson").off("click").click(function() {
            exportToJsonFile($("#jsonData").data("json"), "globals");
        });
    };

    /**
     * Setup the save functionality that occurs when the user presses the save button on the page.
     */
    let setupSaveRequest = function() {
        elements.saveButton.off("click").click(function() {
            elements.saveButton.prop("disabled", true);
            $.ajax({
                url: ajaxUrls.save,
                method: "post",
                dataType: ajaxDataType,
                data: elements.form.serialize(),
                success: function(data) {
                    if (data["status"] === "success")
                        sendAlert("Global settings have been saved successfully...", elements.alertContainer);
                    if (data["status"] === "error")
                        sendAlert("An error occurred while saving global settings: " + data["message"], elements.alertContainer, null, "danger");
                },
                complete: function() {
                    elements.saveButton.prop("disabled", false);
                }
            });
        });
    };

    // Save Current Values.
    let elements = configureGlobalElements();
    // setup Functionality.
    setupJsonExport();
    setupSaveRequest();
});