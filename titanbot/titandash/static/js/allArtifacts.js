/**
 * allArtifacts.js
 *
 * Controls the simple initialization and creation of a DataTable that holds all artifacts and their
 * associated information available.
 */
$(document).ready(function() {
    let table = $("#artifactsTable");

    /**
     * Generate DataTable Instance...
     *
     * Disabled Paging.
     * Disabled Base Info.
     */
    table.DataTable({
        paging: false,
        info: false,
    });
    table.fadeIn(200);

    /**
     * Allow users to export their artifacts data to a JSON file.
     */
    $("#exportArtifactsJson").off("click").click(function() {
        exportToJsonFile($("#jsonData").data("json"), "artifacts")
    });
});