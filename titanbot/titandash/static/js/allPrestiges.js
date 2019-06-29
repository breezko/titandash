/**
 * allPrestiges.js
 *
 * Controls thr simple initialization and creation of a DataTable that holds all prestiges and their
 * associated information available.
 */
$(document).ready(function() {
    let table = $("#allPrestigeTable");

    /**
     * Generate DataTable Instance...
     *
     * PageLength: 50
     */
    table.DataTable({
        pageLength: 50,
    });

    /**
     * Allow users to export their prestiges data to a JSON file.
     */
    $("#exportPrestigesJson").off("click").click(function() {
        exportToJsonFile($("#jsonData").data("json"), "prestiges")
    });
});