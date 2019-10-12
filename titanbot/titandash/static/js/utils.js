/**
 * utils.js
 *
 * Place any generic functions here that may be used by any piece of TitanDash functionality.
 */

/**
 * Loader template can be used to place loaders on a page dynamically during loads through javascript.
 */
let loaderTemplate =
    `
    <div class="w-100 d-flex justify-content-center align-items-center loader-template" style="display: none;">
        <div class="spinner">
            <div class="rect1"></div>
            <div class="rect2"></div>
            <div class="rect3"></div>
            <div class="rect4"></div>
            <div class="rect5"></div>
        </div>      
    </div>
    `;

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
function sendAlert(message, container, style, type="success", fade=true, dismissible=false) {
    let alert = $(`
        <div style="display: none; ${style || ""}" class="alert alert-${type} dashboard-alert">
            ${message}
        </div>
    `);

    if (dismissible) {
        alert.append(`
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        `)
    }

    alert.appendTo(container);
    alert.fadeIn(250);

    if (fade) {
        // Fadeout after five full seconds.
        setTimeout(function () {
            alert.fadeOut(500, function () {
                $(this).remove()
            });
        }, 4000);
    }
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

/**
 * Retrieve the active session that is currently selected by the user. This is done to determine
 * the users currently selected session so that multiple sessions can be started, stopped, paused, etc...
 */
function getActiveInstance() {
    let active = null;
    $("#dashboardInstancesTableBody").find("tr").each(function(index, value) {
        if ($(value).find(".instance-select-btn").first().prop("disabled")) {
            active = $(value).data().id;
        }
    });
    return active;
}
