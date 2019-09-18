/**
 * allStatistics.js
 *
 * Controls the simple initialization and creation of the statistics table. This table is less complex
 * then some of the other tables, no need to use DataTables here.
 */
$(document).ready(function() {
    let ajaxStatisticsUrl = "/statistics";
    let instanceSelector = $("#statisticsInstanceSelect");

    let elements = {
        allStatistics: $("#allStatisticsContent"),
        progress: $("#infoProgressContainer"),
        played: $("#infoPlayedContainer")
    };

    instanceSelector.off("change").change(function() {
        $.ajax({
            url: ajaxStatisticsUrl,
            dataType: "json",
            data: {
                instance: $(this).val(),
                context: true
            },
            beforeSend: function() {
                $.each(elements, function(index, value) {
                    value.empty().append(loaderTemplate);
                });
            },
            success: function(data) {
                $.each(elements, function(index, value) {
                    value.find(".loader-template").fadeOut(100, function() {
                        $(this).remove();
                        value.empty().append(data[index]);
                    });
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