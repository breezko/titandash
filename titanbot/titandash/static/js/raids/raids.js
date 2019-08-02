/**
 * raids.js
 *
 * Controls the initialization of a DataTable containing all raids.
 */
$(document).ready(function() {
    let table = $("#raidsTable");

    /**
     * Generate DataTable.
     */
    table.DataTable({
        order: [[1, "asc"]]
    });
});