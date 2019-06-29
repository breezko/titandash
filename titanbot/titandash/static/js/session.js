/**
 * session.js
 *
 * Controls the initialization of a DataTable containing all prestiges
 * associated with the session.
 */
$(document).ready(function() {
    let table = $("#sessionPrestigesTable");

    /**
     * Generate DataTableInstance
     */
    table.DataTable();

    /**
     * Allow users to export their prestiges data to a JSON file.
     */
    $("#exportSessionJson").off("click").click(function() {
        exportToJsonFile($("#jsonData").data("json"), $("#sessionUuidValue").text());
    });
});