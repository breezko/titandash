/**
 * Initializing the entire dashboard on document ready.
 */
$(document).ready(function() {
    let InitializeDashboard = function() {
        new ReleaseInfo();
        new Instances();
        new BotInstanceConsumer();
        new BotQueueConsumer();
        new BotLoggerConsumer();
        new BotPrestigeConsumer();
        new BotScreenManager();
        new ToolHandler();
    };

    /**
     * INITIALIZE.
     */
    InitializeDashboard();
});