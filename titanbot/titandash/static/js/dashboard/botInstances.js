/**
 * botInstances.js
 *
 * Control functionality related to bot instances and the creation of them for use with the bot.
 */

let Instances = function() {
    /* Base Variables */
    let instanceAjaxUrlCreate = "/ajax/instances/create";
    let instanceAjaxUrlRemove = "/ajax/instances/remove";

    /**
     * Configure and allocate all instance elements (jQuery).
     */
    this.configureInstancesElements = function() {
        return {
            dashboardInstancesHeader: $("#dashboardInstances"),
            dashboardInstancesBody: $("#dashboardInstancesBody"),
            dashboardInstancesContent: $("#dashboardInstancesContent"),
            dashboardInstancesTable: $("#dashboardInstancesTable"),
            dashboardInstancesTableBody: $("#dashboardInstancesTableBody"),
            dashboardNoInstancesContainer: $("#dashboardNoInstancesContainer"),
            dashboardAddInstanceButton: $("#dashboardInstancesAddButton")
        }
    };

    this.configureInstanceButtons = function() {
        this.configureInstanceAdd();
        this.configureInstanceSelect();
        this.configureInstanceRemove();
    };

    this.configureInstanceAdd = function() {
        let _this = this;
        elements.dashboardAddInstanceButton.off("click").on("click", function() {
            $.ajax({
                url: instanceAjaxUrlCreate,
                dataType: "json",
                success: function(data) {
                    elements.dashboardInstancesTableBody.append(
                        `
                        <tr data-id="${data.id}">
                            <td style="width: 20%;">${data.name}</td>
                            <td style="width: 50%;"><button style="width: 100%;" class="btn btn-sm btn-primary instance-select-btn">Select</button></td>
                            <td style="width: 50%;"><button style="width: 100%;" class="btn btn-sm btn-danger instance-remove-btn">Remove</button></td>
                        </tr>
                        `
                    );
                    if (elements.dashboardInstancesTableBody.find("tr").length === 1) {
                        elements.dashboardInstancesTableBody.find(".instance-select-btn").first().text("Selected").prop("disabled", true);
                        elements.dashboardInstancesTableBody.find(".instance-remove-btn").first().prop("disabled", true);
                    }
                    _this.configureInstanceSelect();
                    _this.configureInstanceRemove();
                }
            });
        });
    };

    this.configureInstanceSelect = function() {
        $(".instance-select-btn").off("click").on("click", function() {
            $(".instance-select-btn").each(function(index, value) {
                $(value).text("Select").prop("disabled", false);
            });
            $(".instance-remove-btn").each(function(index, value) {
                $(value).prop("disabled", false);
            });

            $(this).text("Selected").prop("disabled", true);
            $(this).closest("tr").find(".instance-remove-btn").first().prop("disabled", true);
        });
    };

    this.configureInstanceRemove = function() {
        $(".instance-remove-btn").off("click").on("click", function() {
            let row = $(this).closest("tr");
            $.ajax({
                url: instanceAjaxUrlRemove,
                dataType: "json",
                data: {
                    "id": row.data("id")
                },
                success: function() {
                    row.fadeOut(100, function() {
                       row.remove();
                    });
                }
            });
        });
    };

    /* Consumer Elements. */
    let elements = this.configureInstancesElements();

    /* Configure Instance Buttons */
    this.configureInstanceButtons();
};