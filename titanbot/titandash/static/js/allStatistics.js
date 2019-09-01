/**
 * allStatistics.js
 *
 * Controls the simple initialization and creation of the statistics table. This table is less complex
 * then some of the other tables, no need to use DataTables here.
 */
$(document).ready(function() {
    let ajaxStatisticsUrl = "/statistics";
    let instanceSelector = $("#statisticsInstanceSelect");

    instanceSelector.off("change").change(function() {
        $.ajax({
            url: ajaxStatisticsUrl,
            dataType: "json",
            data: {
                instance: $(this).val(),
                context: true
            },
            beforeSend: function() {
                $("#allStatisticsContent").empty().append(loaderTemplate);
                $(".loader-template").fadeIn();
            },
            success: function(data) {
                let body = $("#allStatisticsContent");
                body.find(".loader-template").fadeOut(100, function() {
                    $(this).remove();
                    body.empty().append(data["table"]);
                });
            }
        })
    });

    /**
     * Allow users to export their statistics data to a JSON file.
     */
    $("#exportStatisticsJson").off("click").click(function() {
        exportToJsonFile($("#jsonData").data("json"), "stats");
    });
});