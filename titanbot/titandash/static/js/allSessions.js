/**
 * allSessions.js
 *
 * Controls the simple initialization and creation of a DataTable that hold
 * all sessions and their associated information.
 */
$(document).ready(function() {
    let table = $("#allSessionsTable");

    /**
     * Generate DataTable Instance...
     */
    table.DataTable({
        pageLength: 25,
        order: [[1, "desc"]],
        columnDefs: [
            {targets: [0], orderable: false},
        ]

    });

    /**
     * Allow users to export their sessions data to a JSON file.
     */
    $("#exportSessionsJson").off("click").click(function() {
        exportToJsonFile($("#jsonData").data("json"), "sessions")
    });
});