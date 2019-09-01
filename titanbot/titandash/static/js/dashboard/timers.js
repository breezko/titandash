/**
 * timers.js
 *
 * Create the different libraries that may be used to create countdowns, as well as stopwatch's
 * for tracking different in game intervals from within TitanDash.
 */

/**
 * Generate a Stopwatch instance that will count up from the specified start date.
 *
 * @param startDate Date the stopwatch will use to start from.
 * @param formattedDate Date being used when rendering countdown output. (Null will not use a prepended date).
 * @param element Element modified on each tick / interval.
 * @param padding Specify the character that will be prepended to values if < 10 (padding zeroes).
 */
let Stopwatch = function(startDate, formattedDate, element, padding) {
    this.dateOrig = startDate;

    let date = new Date(startDate).getTime();
    let interval = setInterval(function() {
        let now = new Date().getTime();
        let dist = now - date;
        
        let days = Math.floor(dist / (1000 * 60 * 60 * 24));
        dist = dist % (1000 * 60 * 60 * 24);
        let hour = Math.floor(dist / (1000 * 60 * 60));
        dist = dist % (1000 * 60 * 60);
        let mins = Math.floor(dist / (1000 * 60));
        dist = dist % (1000 * 60);
        let secs = Math.floor(dist / (1000));
        dist = dist % (1000);
        let msec = dist;

        // Apply zero padding if specified.
        if (padding) {
            if (days < 10)
                days = padding + days;
            if (hour < 10)
                hour = padding + hour;
            if (mins < 10)
                mins = padding + mins;
            if (secs < 10)
                secs = padding + secs;
            if (msec < 100 && msec > 10)
                msec = padding + msec;
            if (msec < 10)
                msec = padding + padding + msec;
        }

        let out = "";
        if (days > 0)
            out = `<strong>${days}:${hour}:${mins}:${secs}.${msec}</strong>`;
        else
            out = `<strong>${hour}:${mins}:${secs}.${msec}</strong>`;

        if (dist < 0)
            out = `<strong>00:00:00:00.000</strong>`;

        if (formattedDate)
            element.html(`${formattedDate} (${out})`);
        else
            element.html(out);
    }, 1);

    /**
     * Destroy the current interval function that is being used to determine countdown
     * values every 1000 milliseconds. Destroying the Countdown will end any functionality
     * from taking place again.
     */
    this.destroy = function() {
        clearInterval(interval);
    };
};

/**
 * Generate a Countdown instance that will countdown from the current specified date
 * until the current time.
 *
 * @param countdownDate Date being counted down from.
 * @param formattedDate Date being used when rendering countdown output. (Null will not use a prepended date).
 * @param element Element modified on each tick / interval.
 * @param padding Specify the character that will be prepended to values if < 10. (padding zeroes).
 */
let Countdown = function(countdownDate, formattedDate, element, padding) {
    this.dateOrig = countdownDate;

    let date = new Date(countdownDate).getTime();
    let interval = setInterval(function() {
        let now = new Date().getTime();
        let dist = date - now;

        let hour = Math.floor((dist % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        let mins = Math.floor((dist % (1000 * 60 * 60)) / (1000 * 60));
        let secs = Math.floor((dist % (1000 * 60)) / 1000);

        if (hour < 0)
            hour = 0;
        if (mins < 0)
            mins = 0;
        if (secs < 0)
            secs = 0;

        // Apply zero padding if specified.
        if (padding) {
            if (hour < 10)
                hour = padding + hour;
            if (mins < 10)
                mins = padding + mins;
            if (secs < 10)
                secs = padding + secs;
        }

        if (formattedDate)
            element.html(`${formattedDate} <strong>(${hour}:${mins}:${secs})</strong>`);
        else
            element.html(`<strong>${hour}:${mins}:${secs}</strong>`);

        if (dist <= 0) {
            clearInterval(interval);
            element.fadeOut(0, function() {
                $(this).html("<small><strong class='text-success'>READY...</strong></small>").fadeIn(100)
            });
        }
    }, 1000);

    /**
     * Destroy the current interval function that is being used to determine countdown
     * values every 1000 milliseconds. Destroying the Countdown will end any functionality
     * from taking place again.
     */
    this.destroy = function() {
        clearInterval(interval);
    };
};
