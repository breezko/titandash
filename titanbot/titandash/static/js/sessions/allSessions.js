/**
 * allSessions.js
 *
 * Controls the simple initialization and creation of a DataTable that hold
 * all sessions and their associated information.
 */
$(document).ready(function() {
    let ajaxSessionUrl = "/sessions";
    let instanceSelector = $("#sessionsInstanceSelect");

    function reloadDataTable() {
        $("#allSessionsTable").DataTable({
            responsive: true,
            pageLength: 25,
            order: [[1, "desc"]],
            columnDefs: [
                {targets: [0], orderable: false},
            ]
        });
    }

    /**
     * Generate change listener to modify the sessions data table.
     */
    instanceSelector.off("change").change(function() {
        $.ajax({
            url: ajaxSessionUrl,
            dataType: "json",
            data: {
                instance: $(this).val(),
                context: true
            },
            beforeSend: function() {
                $("#sessionsCardBody").empty().append(loaderTemplate);
                $(".loader-template").fadeIn();
            },
            success: function(data) {
                let body = $("#sessionsCardBody");
                body.find(".loader-template").fadeOut(100, function() {
                    $(this).remove();
                    body.empty().append(data["table"]);
                    reloadDataTable();
                });
            }
        });
    });

    /**
     * Generate DataTable Instance...
     */
    reloadDataTable();

    /**
     * Allow users to export their sessions data to a JSON file.
     */
    $("#exportSessionsJson").off("click").click(function() {
        exportToJsonFile($("#jsonData").data("json"), "sessions")
    });
});