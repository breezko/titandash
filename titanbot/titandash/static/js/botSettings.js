/**
 * settings.js
 *
 * Control the settings page within the web application.
 */
$(document).ready(function() {
    let data = $("#jsonData").data("json");
    // Export as JSON File.
    $("#exportSettingsJson").off("click").click(function() {
        exportToJsonFile(data, "settings");
    });
});