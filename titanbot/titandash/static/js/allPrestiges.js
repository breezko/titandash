/**
 * allPrestiges.js
 *
 * Controls thr simple initialization and creation of a DataTable that holds all prestiges and their
 * associated information available.
 */
$(document).ready(function() {
    let ajaxPrestigesUrl = "/all_prestiges";
    let instanceSelector = $("#prestigesInstanceSelect");

    function reloadDataTable() {
        $("#allPrestigeTable").DataTable({
            responsive: true,
            pageLength: 50,
            order: [[1, "desc"]],
        });
    }

    instanceSelector.off("change").change(function() {
        $.ajax({
            url: ajaxPrestigesUrl,
            dataType: "json",
            data: {
                instance: $(this).val(),
                context: true
            },
            beforeSend: function() {
                $("#prestigesCardBody").empty().append(loaderTemplate);
                $(".loader-template").fadeIn();
            },
            success: function(data) {
                let body = $("#prestigesCardBody");
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
     * PageLength: 50
     */
    reloadDataTable();

    /**
     * Allow users to export their prestiges data to a JSON file.
     */
    $("#exportPrestigesJson").off("click").click(function() {
        exportToJsonFile($("#jsonData").data("json"), "prestiges");
    });
});