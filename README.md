# TitanDash [![star this repo](http://githubbadges.com/star.svg?user=becurrie&repo=titandash&style=flat)](https://github.com/becurrie/titandash) [![fork this repo](http://githubbadges.com/fork.svg?user=becurrie&repo=titandash&style=flat)](https://github.com/becurrie/titandash/fork)

![BOS](https://github.com/becurrie/titandash/blob/master/titanbot/titandash/bot/data/images/artifacts/book_of_shadows.png) ![SOTV](https://github.com/becurrie/titandash/blob/master/titanbot/titandash/bot/data/images/artifacts/stone_of_the_valrunes.png) ![FOTS](https://github.com/becurrie/titandash/blob/master/titanbot/titandash/bot/data/images/artifacts/flute_of_the_soloist.png) ![HOS](https://github.com/becurrie/titandash/blob/master/titanbot/titandash/bot/data/images/artifacts/heart_of_storms.png) ![ROC](https://github.com/becurrie/titandash/blob/master/titanbot/titandash/bot/data/images/artifacts/ring_of_calisto.png) ![IG](https://github.com/becurrie/titandash/blob/master/titanbot/titandash/bot/data/images/artifacts/invaders_gjalarhorn.png) ![BOH](https://github.com/becurrie/titandash/blob/master/titanbot/titandash/bot/data/images/artifacts/boots_of_hermes.png)

**Automate TapTitans2 using a web application built in Django.**

![dashboard](https://github.com/becurrie/titandash/blob/master/img/dashboard.png)

## Features
### Dashboard
- Main dashboard screen providing real-time updates and the ability to start, pause or stop the bot and view information about the current session.
- View a real time view of the current in game screen.
- View all log records associated with the current bot session.
- Countdowns until specific functionality takes place.
- View all sessions that have taken place and review logs/duration/prestiges that happened while a session was active.
- View all raid results instances and view data about damage done and who did damage.
- Create multiple configurations that can be swapped out quickly when needed (farming, tournaments, push).
- Review all current statistics taken from the game, as well as statistics related to the bot.
- View all prestiges and review additional information (average stage, average duration).
- View all artifact statistics and whether or not you currently own each one.

### Bot
- Activate chosen in game skills on a specified cooldown, with the option to wait for a specific skill before activating others.
- Activate specific functions using keyboard shortcuts.
- Automatically level up the sword master, skills and heroes in game with a specific intensity (clicks).
- Automatically prestige after a threshold has been reached (stage, percent of max stage, max stage, time limit).
- Automatically parse out clan raid results from in game.
- Upgrade or ignore specific artifacts or tiers after a prestige.
- Participate in tournaments when they are available (enter/collect rewards).
- Hatch and collect any eggs when they become available.
- Collect daily achievements when they are completed.
- Collect daily rewards when they are available.

## Requirements
- Windows 10
- [Python 3.7](https://www.python.org/downloads/release/python-370/)
- [Node/NPM](https://nodejs.org/en/)
- [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract)
- [Redis Server](https://redislabs.com/)
- [Nox Android Emulator](https://www.bignox.com/)

## Setup
Take a look at the [wiki](https://github.com/becurrie/titandash/wiki) for information about setting up and configurating the dependencies and requirements needed to start the dashboard and initiate a new bot instance.

## Development
Thanks for taking the time to check out this project. If you have any suggestions, 
you can create a new issue about it or create a pull request with your changes!
