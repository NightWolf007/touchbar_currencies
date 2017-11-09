#!/bin/bash

launchctl unload ~/Library/LaunchAgents/com.nwsoft.TouchbarCurrencies.plist
rm ~/Library/LaunchAgents/com.nwsoft.TouchbarCurrencies.plist
rm /usr/local/bin/touchbar-currencies
exit 0
