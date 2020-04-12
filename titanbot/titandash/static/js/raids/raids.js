/**
 * raids.js
 *
 * Controls the initialization of a DataTable containing all raids.
 */
$(document).ready(function() {
    let ajaxRaidsUrl = "/raids";
    let instanceSelector = $("#raidsInstanceSelect");

    function reloadDataTable() {
        $("#raidsTable").DataTable({
            responsive: true,
            order: [[1, "desc"]],
            columnDefs: [
                {targets: [0], orderable: false}
            ]
        });
    }

    instanceSelector.off("change").change(function() {
        $.ajax({
            url: ajaxRaidsUrl,
            dataType: "json",
            data: {
                instance: $(this).val(),
                context: true
            },
            beforeSend: function() {
                $("#raidsCardBody").empty().append(loaderTemplate);
                $(".loader-template").fadeIn();
            },
            success: function(data) {
                let body = $("#raidsCardBody");
                body.find(".loader-template").fadeOut(100, function() {
                    $(this).remove();
                    body.empty().append(data["table"]);
                    reloadDataTable();
                });
            }
        });
    });

    /**
     * Generate DataTable.
     */
    reloadDataTable();

    /**
     * Allow users to export their raids data to a JSON file.
     */
    $("#exportRaidsJson").off("click").click(function() {
        exportToJsonFile($("#jsonData").data("json"), "raids");
    });
});