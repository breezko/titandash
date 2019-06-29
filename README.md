# TitanDash [![star this repo](http://githubbadges.com/star.svg?user=becurrie&repo=titandash&style=flat)](https://github.com/becurrie/titandash) [![fork this repo](http://githubbadges.com/fork.svg?user=becurrie&repo=titandash&style=flat)](https://github.com/becurrie/titandash/fork)

---
Titandash is a django web application that allows users to control and automate the mobile game TapTitans2. Data is updated in realtime
on the dashboard to provide information about what is currently happening while the Bot is running.

## Features
### Dashboard
- Main dashboard screen providing real-time updates and the ability to start, pause or stop the bot and view information about the current session.
- View a real time view of the current in game screen.
- View all log records associated with the current bot session.
- Countdowns until specific functionality takes place.
- View all sessions that have taken place and review logs/duration/prestiges that happened while a session was active.
- Create multiple configurations that can be swapped out quickly when needed (farming, tournaments, push).
- Review all current statistics taken from the game, as well as statistics related to the bot.
- View all prestiges and review additional information (average stage, average duration).
- View all artifact statistics and whether or not you currently own each one.

---

### Bot
- Activate chosen in game skills on a specified cooldown, with the option to wait for a specific skill before activating others.
- Automatically level up the sword master, skills and heroes in game with a specific intensity (clicks).
- Automatically prestige after a threshold has been reached (stage, percent of max stage, max stage, time limit).
- Upgrade or ignore specific artifacts or tiers after a prestige.
- Participate in tournaments when they are available (enter/collect rewards).
- Hatch and collect any eggs when they become available.
- Collect daily achievements when they are completed.
- Collect daily rewards when they are available.

---

## Requirements
- Windows 10
- [Python 3.7](https://www.python.org/downloads/release/python-370/)
- [Node/NPM](https://nodejs.org/en/)
- [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract)
- [Redis Server](https://redislabs.com/)
- [Nox Android Emulator](https://www.bignox.com/)


## Setup
### The Environment
If you haven't already, make sure you have Python 3.7 installed on your system. Once complete, we're going to setup a virtual environment that we can use to install the project dependencies into (This part isn't required, but it's worth keeping your system python separate from the project. If you don't care about this, you can skip this part).

Install the following on your machine with a PowerShell window.
```
pip install virtualenv
mkvirtualenv titandash
<path_to_env>/Scripts/activate.ps1`
pip install -r <path_to_project>/requirements.txt
```

This will install the required modules and packages that titandash uses when running.

---

### NPM
NPM (Node Package Manager) is used to control which packages are available and collected by Django when running the `collectstatis` command.
Once you have installed Node, you can open up a PowerShell terminal from your project directory and running the following command.

`npm install`

This will create a `node_modules` directory with all the files needed and included when titandash collects static files.

---

### Nox Android Emulator
The Nox android emulator is currently the only supported emulator, you may be able to get away with using different ones, you just need to make sure that your resolution is set to **480x800**. Some padding is configured within the Bot
currently and the emulator should be placed at the top-left portion (0, 0) of your screen.

If you're having trouble installing TapTitans2 on your emulator within Nox, see [this](https://i.redd.it/3gv7n15r43t21.jpg) image for some instructions on setting it up.

---

### Tesseract-OCR
The Tesseract OCR (Optical Character Recognition) software is used by titandash to read image data from the game, into parsable and readable data used by the Bot. You can download the Tesseract installer [here](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.0.0-alpha.20190623.exe)

The installation for this is pretty straight-forward, follow the prompts and no configuration is required after installing the software.
You can test that tesseract is installed and working by running the command `tesseract` in your terminal. You should see some help docs printed out.

---

### Redis
Redis is used by titandash to allow for WebSocket integration within the web application, this lets the Bot update the dashboard in real time.

Installing Redis on Windows 10 is very easy now that WSL (Windows Subsystem Linux) is available for simple to setup. Take a look at [this](https://redislabs.com/blog/redis-on-windows-10/) article for an in depth guide if the commands below do not work.

Start by enabling the WSL within Windows, in a PowerShell terminal, type the following command:

`Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux`

You may need to reboot your computer after doing this (You only need to do this one time).

Afterwards, install Ubuntu within your Windows instance, you can find Ubuntu in the Microsoft Store [here](https://www.microsoft.com/en-us/p/ubuntu-1804/9n9tngvndl3q).

Once Ubuntu is successfully installed, you can open up a Ubuntu instance and type the following commands:
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install redis-server
```

Run the following command to make sure the server is running.

`sudo service redis-server restart`

---

### Migrations
You can run the migrations by running the following command in a terminal targeting the projects `titanbot` directory. This directory contains the `manage.py` file which is used to perform all of the django management commands.

`./manage.py migrate`

#### Upgrading
When any new updates are released, you can pull down the latest master branch and run this command to ensure your database is up to date. Make sure you backup your database before updating your repository in case something irrversible happens, you'll be able to overwrite the database with your data if this happens.

---

### Static Files
Static files are needed to ensure the styling and javascript files are available and can be served by the webapp. Following the same instructions as the migrations, run the following command.

`./manage.py collectstatic`

---

## On The Go
You can optionally install a program like NGrok to allow access to the local dashboard from anywhere!

`ngrok http 8000`

You will now be able to access your dashboard from anywhere!

## Development
Thanks for taking the time to check out this project. If you have any suggestions, 
you can create a new issue about it or create a pull request with your changes!
