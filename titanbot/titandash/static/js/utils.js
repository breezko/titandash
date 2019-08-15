/**
 * utils.js
 *
 * Place any generic functions here that may be used by any piece of TitanDash functionality.
 */

/**
 * Export a JsonObject to a .json file with the specified filename.
 */
function exportToJsonFile(jsonData, filename) {
    let dataStr = JSON.stringify(jsonData);
    let dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    let exportFileDefaultName = `${filename}.json`;

    let linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}

/**
 * Generate and alert with the specified message and append it to the specified container.
 *
 * The alert will automatically fade out after 5 seconds.
 */
function sendAlert(message, container, style, type="success") {
    let alert = $(`
        <div style="${style}" class="alert alert-${type} dashboard-alert">
            ${message}
        </div>
    `);

    // Appending the alert to our specified container.
    container.append(alert);
    alert.fadeIn(250);
    // Fadeout after five full seconds.
    setTimeout(function() {
        alert.fadeOut(500, function() {
            $(this).remove()
        });
    }, 2000);
}

/**
 * Callback function used by theme selection to update the cookie and reload the page
 * once one is selected.
 */
function selectTheme(theme) {
    $.ajax({
        url: "/ajax/theme_change",
        dataType: "json",
        data: {
            "theme": theme
        },
        complete: function() {
            window.location.reload(true);
        }
    });
}
