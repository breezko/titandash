/**
 * allArtifacts.js
 *
 * Controls the simple initialization and creation of a DataTable that holds all artifacts and their
 * associated information available.
 */
$(document).ready(function() {
    let ajaxArtifactsUrl = "/artifacts";
    let instanceSelector = $("#artifactsInstanceSelect");

    function reloadDataTable() {
        $("#artifactsTable").DataTable({
            responsive: true,
            paging: false,
            info: false,
            order: [[1, "asc"]],
            columnDefs: [
                {targets: [0], orderable: false}
            ]
        });
    }

    instanceSelector.off("change").change(function() {
        $.ajax({
            url: ajaxArtifactsUrl,
            dataType: "json",
            data: {
                instance: $(this).val(),
                context: true
            },
            beforeSend: function() {
                $("#artifactContent").empty().append(loaderTemplate);
                $(".loader-template").fadeIn();
            },
            success: function(data) {
                let body = $("#artifactContent");
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
     *
     * Disabled Paging.
     * Disabled Base Info.
     */
    reloadDataTable();

    /**
     * Allow users to export their artifacts data to a JSON file.
     */
    $("#exportArtifactsJson").off("click").click(function() {
        exportToJsonFile($("#jsonData").data("json"), "artifacts")
    });
});