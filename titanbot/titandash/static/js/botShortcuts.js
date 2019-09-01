/**
 * botShortcuts.js
 *
 * Control the shortcuts page within the web application.
 */
$(document).ready(function() {
    let table = $("#shortcutsTable");

    table.DataTable({
        responsive: true,
        paging: false,
        info: false
    });
});