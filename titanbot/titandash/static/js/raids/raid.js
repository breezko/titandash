/**
 * raid.js
 *
 * Controls the initialization of all specific raid functionality.
 */
$(document).ready(function() {
    let table = $("#attacksTable");
    let initLoader = $("#dashboardRaidLoader");
    let raidJson = $("#jsonData").data("json");
    let formats = [];

    function randomColor() {
        let num = Math.round(0xffffff * Math.random());
        let r = num >> 16;
        let g = num >> 8 & 255;
        let b = num & 255;

        return "rgba(" + r + ", " + g + ", " + b + ", 0.6)";
    }

    function generateDataset() {
        let data = [];
        let labels = [];
                let colors = [];

        raidJson["raid"]["attacks"].forEach(function(obj) {
             data.push(obj["damage"]["damage"]);
             formats.push(obj["damage"]["formatted"]) ;
             labels.push(obj["member"]["name"])
        });

        for(let i = 0; i < data.length; i++) {
            colors.push(randomColor());
        }

        return {
            datasets: [{
                label: "Damage By Member",
                data: data,
                backgroundColor: colors
            }],
            labels: labels
        }
    }

    /**
     * Generate DataTable.
     */
    table.DataTable({
        responsive: true,
        pageLength: 50,
        order: [
            [0, "asc"]
        ]
    });

    /**
     * Generate Raid Chart.
     */
    let attacksChart = $("#attacksChart");
    let attacksData = generateDataset();
    new Chart(attacksChart, {
        type: 'doughnut',
        data: attacksData,
        options: {
            legend: {
                display: false
            },
            tooltips: {
                callbacks: {
                    label: function(tooltipItem, data) {
                        let label = data.labels[tooltipItem.index];
                        let format = formats[tooltipItem.index];
                        if (label) {
                            label += ": ";
                        }

                        label += format;
                        return label;
                    }
                }
            }
        }
    });

    initLoader.fadeOut(200, function() {
        $(this).remove();
        attacksChart.slideToggle("fast");
    });

    /**
     * Allow users to export their raid data to a JSON file.
     */
    $("#exportRaidJson").off("click").click(function() {
        exportToJsonFile($("#jsonData").data("json"), $("#raidDigestValue").text());
    });
});