/**
 * log.js
 *
 * Control the log page and the ability to open a log file.
 */
$(document).ready(function() {
    let ajaxUrl = "/ajax/open_log";

    // Open Log file. This is handled through an AJAX request.
    $("#openLogFileButton").click(function() {
        $.ajax({
            url: ajaxUrl,
            dataType: "json",
            data: {log: $(this).data("log")}
        });
    });
});