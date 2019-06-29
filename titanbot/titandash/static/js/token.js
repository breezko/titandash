/**
 * token.js
 *
 * Handle all token modal functionality.
 */
let TokenHandler = function() {
    /* Base Variables */
    let ajaxUrl = "/ajax/update_token";

    /**
     * Configure and allocate all token elements (jQuery).
     */
    this.configureTokenElements = function() {
        return {
            tokenInput: $("#tokenValue"),
            saveButton: $("#tokenSaveButton"),
            closeButton: $("#tokenCloseButton"),
            modalAlerts: $("#tokenModalAlerts")
        }
    };

    this.configureSaveButton = function() {
        elements.saveButton.off("click").click(function () {
            let intervals = 0;
            $(this).prop("disabled", true).text("Saving");
            let loadInterval = setInterval(function () {
                intervals += 1;
                let btn = elements.saveButton;
                btn.text(btn.text() + ".");
                if (intervals === 3) {
                    intervals = 0;
                    btn.text("Saving");
                }
            }, 250);

            // Launch AJAX to save Token instance.
            $.ajax({
                url: ajaxUrl,
                dataType: "json",
                data: {
                    "token": elements.tokenInput.val()
                },
                success: function (data) {
                    clearInterval(loadInterval);
                    elements.saveButton.text("Save").prop("disabled", false);

                    sendAlert(
                        data["message"],
                        elements.modalAlerts,
                        "margin: 5px 0 0 !important;"
                    );
                }
            })
        });
    };

    /* Token Elements */
    let elements = this.configureTokenElements()

    // Configure the save button for token.
    this.configureSaveButton();
};