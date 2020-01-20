/**
 * allArtifacts.js
 *
 * Controls the simple initialization and creation of a DataTable that holds all artifacts and their
 * associated information available.
 */
$(document).ready(function() {
    let ajaxUrls = {
        artifacts: "/artifacts",
        artifactsToggle: "/ajax/artifacts/toggle"
    };
    let elements = {
        cardBody: $("#artifactsCardBody"),
        instanceSelector: $("#artifactsInstanceSelect"),
        toggleButton: $(".artifact-toggle")
    };

    function reloadDataTable() {
        $("#artifactsTable").DataTable({
            responsive: true,
            paging: false,
            info: false,
            order: [[1, "asc"]],
            columnDefs: [
                {targets: [0], orderable: false}
            ]
        });
    }

    elements.instanceSelector.off("change").change(function() {
        $.ajax({
            url: ajaxUrls.artifacts,
            dataType: "json",
            data: {
                instance: $(this).val(),
                context: true
            },
            beforeSend: function() {
                $("#artifactContent").empty().append(loaderTemplate);
                $(".loader-template").fadeIn();
            },
            success: function(data) {
                let body = $("#artifactContent");
                body.find(".loader-template").fadeOut(100, function() {
                    $(this).remove();
                    body.empty().append(data["table"]);
                    reloadDataTable();
                });
            }
        });
    });

    /**
     * Send an ajax request to toggle the owned status of the specified artifact.
     */
    function toggleArtifactStatus(button, artifactKey) {
        $.ajax({
            url: ajaxUrls.artifactsToggle,
            dataType: "json",
            data: {
                key: artifactKey,
                instance: elements.instanceSelector.val()
            },
            beforeSend: function() {
                button.prop("disabled", true);
            },
            success: function(data) {
                let artifactSpan = $(`#artifact-${artifactKey}`);
                if (data["state"] === true) {
                    artifactSpan.removeClass("fa-times").removeClass("text-danger").addClass("text-success").addClass("fa-check");
                    artifactSpan.parent().data("order", 1);
                }
                else if (data["state"] === false) {
                    artifactSpan.removeClass("fa-check").removeClass("text-success").addClass("text-danger").addClass("fa-times");
                    artifactSpan.parent().data("order", 0);
                }
            },
            complete: function() {
                button.prop("disabled", false);
            }
        });
    }

    // Using delegated event handler to ensure toggle buttons work when switching
    // between instances available.
    elements.cardBody.on("click", "button.artifact-toggle", function() {
        toggleArtifactStatus($(this), $(this).data("key"));
    });

    /**
     * Generate DataTable Instance...
     *
     * Disabled Paging.
     * Disabled Base Info.
     */
    reloadDataTable();

    /**
     * Allow users to export their artifacts data to a JSON file.
     */
    $("#exportArtifactsJson").off("click").click(function() {
        exportToJsonFile($("#jsonData").data("json"), "artifacts")
    });
});