/**
 * allStatistics.js
 *
 * Controls the simple initialization and creation of the statistics table. This table is less complex
 * then some of the other tables, no need to use DataTables here.
 */
$(document).ready(function() {
    /**
     * Allow users to export their statistics data to a JSON file.
     */
    $("#exportStatisticsJson").off("click").click(function() {
        exportToJsonFile($("#jsonData").data("json"), "stats");
    });
});