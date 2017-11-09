#!/bin/bash

ln -s `pwd`/touchbar_currencies.py /usr/local/bin/touchbar-currencies || exit 1
cp `pwd`/com.nwsoft.TouchbarCurrencies.plist ~/Library/LaunchAgents/ || \
  (rm /usr/local/bin/touchbar-currencies && exit 1)
launchctl load ~/Library/LaunchAgents/com.nwsoft.TouchbarCurrencies.plist || \
  (rm /usr/local/bin/touchbar-currencies && rm ~/Library/LaunchAgents/com.nwsoft.TouchbarCurrencies.plist && exit 1)
exit 0
