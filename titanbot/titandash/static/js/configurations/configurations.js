/**
 * configurations.js
 *
 * Control functionality related to the list view for available configurations.
 *
 * We allow users to view, edit, export and delete configurations from the table view.
 */
$(document).ready(function() {
    return new ConfigurationsController();
});

/**
 * Main configuration controller to provide functionality to the configurations page.
 */
let ConfigurationsController = function() {
    /**
     * AjaxUrls to specify which urls to access for certain pieces of functionality.
     */
    let ajaxUrls = {
        delete: "/configurations/delete/",
        import: "/configurations/import/",
    };
    let ajaxDataType = "json";

    /**
     * Configure and allocate all configurations elements needed (jQuery).
     */
    let configureConfigurationsElements = function() {
        return {
            /* Hidden Message Container */
            messageContainer: $("#messageContainer"),
            /* Alert Container */
            alertContainer: $("#alert-container"),
            /* Import Modal */
            importButton: $("#importConfigurationButton"),
            importImportButton: $("#importImportButton"),
            importModal: $("#importModal"),
            importModalTitle: $("#importModalTitle"),
            importImportString: $("#importImportString"),
            importAlertContainer: $("#importAlertContainer"),
            /* Export Modal */
            exportModal: $("#exportModal"),
            exportModalTitle: $("#exportModalTitle"),
            exportModalExportString: $("#exportModalExportString"),
            exportModalExportStringInput: $("#exportModalExportStringInput"),
            exportCopyButton: $("#exportCopyButton"),
            exportCopyContainer: $("#copyAlertContainer"),
            /* Delete Modal */
            deleteModal: $("#deleteModal"),
            deleteModalTitle: $("#deleteModalTitle"),
            deleteModalBody: $("#deleteModalBody"),
            deleteModalConfirm: $("#confirmDeleteButton"),
            deleteModalConfirmMessage: $("#deleteModalConfirmationMessage"),
            deleteAlertContainer: $("#deleteAlertContainer"),
            /* Configurations Table */
            configurationsTable: $("#configurationsTable"),
            configurationsExportButtons: $(".btn-export"),
            configurationsDeleteButtons: $(".btn-delete"),
        }
    };

    /* Controller Elements. */
    let elements = configureConfigurationsElements();

    /**
     * Callback function used to determine if the import button should be enabled or not.
     */
    let importStringEnteredCallback = function() {
        // Check that the element contains some sort of data.
        if (elements.importImportString.val()) {
            elements.importImportButton.attr("disabled", false);
        } else {
            elements.importImportButton.attr("disabled", true);
        }
    };

    /**
     * Setup the input listener used to determine if the import button should be enabled.
     */
    elements.importImportString.off("input").on("input", importStringEnteredCallback);

    /**
     * Setup ajax functionality to attempt to import a new configuration.
     */
    elements.importImportButton.off("click").on("click", function() {
        let importString = elements.importImportString.val();

        // Send an ajax request to attempt the import.
        // Errors should be caught and displayed as an error
        // within the modal.
        $.ajax({
            url: ajaxUrls.import,
            dataType: ajaxDataType,
            data: {
                importString: importString
            },
            // We catch error through the success function as well.
            success: function(data) {
                // Successfully imported the configuration string...
                // Update the datatable, hide the modal, and display
                // generic alert message.
                if (data["status"] === "success") {
                    // Update datatable with new config.
                    elements.table.row.add(
                        $(`
                            <tr data-export-string="${data["config"]["export"]}" data-name="${data["config"]["name"]}" data-id="${data["config"]["pk"]}">
                                <td><a href="${data["config"]["url"]}">${data["config"]["pk"]}</a></td>
                                <td><a href="${data["config"]["url"]}">${data["config"]["name"]}</a></td>
                                <td data-order="${data["config"]["created"]["timestamp"]}">${data["config"]["created"]["formatted"]}</td>
                                <td data-order="${data["config"]["updated"]["timestamp"]}">${data["config"]["updated"]["formatted"]}</td>
                                <td><button style="width: 100%;" type="button" class="btn btn-primary btn-export">Export<span style="margin-left: 8px;" class="fa fa-file-export"></span></button></td>
                                <td><button style="width: 100%;" type="button" class="btn btn-danger btn-delete">Delete<span style="margin-left: 8px;" class="fa fa-trash"></span></button></td>
                            </tr>
                        `)).draw();

                    // Hiding the modal.
                    elements.importModal.modal("hide");
                    // Display generic message.
                    sendAlert(data["message"], elements.alertContainer);
                    // Remove content from import string area.
                    elements.importImportString.val("");
                }

                // Error occurred... Display the error message in the alert
                // container present within the modal.
                if (data["status"] === "error") {
                    sendAlert(data["message"], elements.importAlertContainer);
                }
            },
        });
    });

    /**
     * Setup Import Modals.
     */
    elements.importButton.off("click").on("click", function() {
        // Open and display the import modal.
        elements.importModal.modal("show");
    });

    /**
     * Setup Export Modals.
     */
    elements.configurationsTable.off("click", ".btn-export").on("click", ".btn-export", function() {
        // Grab all data from the parent "tr" row, which should contain
        // the export string, and name of the configuration in question.
        let data = $(this).closest("tr").data();

        // Update modal data before showing...
        elements.exportModalTitle.text(`Export Configuration: ${data["name"]}`);
        elements.exportModalExportString.text(data["exportString"]);

        // Display the modal.
        elements.exportModal.modal("show");
    });

    /**
     * Setup the copy button present within the export modal.
     */
    elements.exportCopyButton.off("click").on("click", function() {
        // Create temporary element and append export string for copying.
        copyToClipboard("exportModalExportString");
        sendAlert("Export String Copied...", elements.exportCopyContainer, "margin-left: 2px; margin-right: 2px;");
    });

    /**
     * Setup Configuration Delete Confirmation Modals.
     */
    elements.configurationsTable.off("click", ".btn-delete").on("click", ".btn-delete", function() {
        // Grab all data from the parent "tr" row.
        let tr = $(this).closest("tr");
        let data = tr.data();

        // Update confirmation modal before showing...
        elements.deleteModalTitle.text(`Delete Configuration: ${data["name"]}`);

        // Setup the confirm deletion button...
        elements.deleteModalConfirm.off("click").on("click", function() {
           $.ajax({
               url: ajaxUrls.delete,
               dataType: ajaxDataType,
               data: {
                   "id": data["id"]
               },
               beforeSend: function() {

               },
               success: function(data) {
                   elements.deleteModal.modal("hide");
                   if (data["status"] === "success") {
                       // Send alert letting user know that the configuration
                       // they chose was deleted.
                       sendAlert(data["message"], elements.alertContainer);
                       // We also want to remove that table row from the table.
                       elements.table.row(tr).remove().draw();
                   } else {
                       // Send error alert.
                       sendAlert(data["message"], elements.alertContainer, null, "danger");
                   }
               }
           });
        });

        // Show modal now.
        elements.deleteModal.modal("show");
    });

    // Check for messages on load.
    if (elements.messageContainer.data("message")) {
        sendAlert(elements.messageContainer.data("message"), elements.alertContainer);
    }

    /* Setup Base Datatable With Configurations In It. */
    elements["table"] = elements.configurationsTable.DataTable({
        columnDefs: [{orderable: false, targets: [4, 5]}],
        responsive: true,
        pageLength: 25,
        order: [[3, "desc"]]
    });
};