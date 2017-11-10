# OSX Touchbar Cryptocurrencies
## Description
Application for showing cryptocurrencies exchange rates on OSX touchbar
Supports Bitfinex and Bittrex
## Requirements
* Installed [BetterTouchTool](https://www.boastr.net/downloads/).
* Installed python (version 2 or 3) on path `/usr/lib/python`.
* Installed python libraries:
  - `requests`
  - `redis`
* Installed and launched Redis database.

## Installation
You just need to run script `install.sh` from the projects directory.
```
git clone https://github.com/NightWolf007/touchbar_currencies
cd touchbar_currencies
./install.sh
```
It will install and launch the launchd daemon for fetching exchange rates.

Then you should generate BetterTouchTool preset with scrupt `btt_generator.py` like this:
```
./btt_generator --main BITFINEX:BTC:USD BITFINEX:ETH:USD BITTREX:ETH:USD BITTREX:ETH:BTC -o ~/btt_config.json
```
Then open BetterTouchTool and import generated preset.

## Uninstallation
You just need to run script `uninstall.sh` from the projects directory.
```
cd touchbar_currencies
./uninstall.sh
```
