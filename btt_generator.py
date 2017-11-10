#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import json
import base64
import requests

APP_NAME = 'tbcurrencies'
BITFINEX_URL='https://api.bitfinex.com'
BITTREX_URL='https://bittrex.com'

BUTTONS_COUNT = 20
OPTION_KEY_CODE = 524288

def build_symbol_widget(name, order, widget_script, action_script, modifier_key=None):
    widget = {
        'BTTWidgetName': name,
        'BTTTriggerType': 639,
        'BTTTriggerTypeDescription': 'Apple Script Widget',
        'BTTTriggerClass': 'BTTTriggerTypeTouchBar',
        'BTTPredefinedActionType': 172,
        'BTTPredefinedActionName': 'Run Apple Script (enter directly as text)',
        'BTTInlineAppleScript': action_script,
        'BTTEnabled': 1,
        'BTTOrder': order,
        'BTTTriggerConfig': {
            'BTTTouchBarItemIconHeight': 22,
            'BTTTouchBarItemIconWidth': 22,
            'BTTTouchBarItemPadding': 0,
            'BTTTouchBarFreeSpaceAfterButton': '5.000000',
            'BTTTouchBarButtonColor': '58.650001, 58.650001, 58.650001, 255.000000',
            'BTTTouchBarAlwaysShowButton': '0',
            'BTTTouchBarAppleScriptString': widget_script,
            'BTTTouchBarAlternateBackgroundColor': '109.650002, 109.650002, 109.650002, 255.000000',
            'BTTTouchBarScriptUpdateInterval': 60
        }
    }
    if modifier_key is not None:
        widget['BTTRequiredModifierKeys'] = modifier_key
    return widget

def build_symbol_widgets(currency, widget_script_fun, action_script_fun, modifier_key=None):
    widgets = []
    for i in range(BUTTONS_COUNT):
        widget = build_symbol_widget(
            currency + ':' + str(i),
            i + 1,
            widget_script_fun(currency, i),
            action_script_fun(currency, i),
            modifier_key
        )
        widgets.append(widget)
    return widgets

def build_buttons(currencies, widget_script_fun, action_script_fun):
    symbol_buttons = []
    for currency, modifier_key in currencies.items():
        symbol_buttons += build_symbol_widgets(
            currency, widget_script_fun, action_script_fun, modifier_key
        )
    close_button = {
      'BTTTouchBarButtonName': 'Close Group',
      'BTTTriggerType': 629,
      'BTTTriggerClass': 'BTTTriggerTypeTouchBar',
      'BTTPredefinedActionType': 191,
      'BTTPredefinedActionName': 'Close currently open Touch Bar group',
      'BTTEnabled': 1,
      'BTTOrder': 0,
      'BTTIconData': 'Standard Close Icon',
      'BTTTriggerConfig': {
        'BTTTouchBarItemIconHeight': 0,
        'BTTTouchBarItemIconWidth': 0,
        'BTTTouchBarItemPlacement': 1,
        'BTTTouchBarItemPadding': 0,
        'BTTTouchBarButtonColor': '0.000000, 0.000000, 0.000000, 255.000000',
        'BTTTouchBarOnlyShowIcon': 1
      }
    }
    return [close_button] + symbol_buttons

def build_group(name, order, currencies, widget_script_fun, action_script_fun, icon=None):
    buttons = build_buttons(currencies, widget_script_fun, action_script_fun)
    return {
        'BTTTouchBarButtonName': name,
        'BTTTriggerType': 630,
        'BTTTriggerClass': 'BTTTriggerTypeTouchBar',
        'BTTEnabled': 1,
        'BTTOrder': order,
        'BTTAdditionalActions': buttons,
        'BTTIconData': icon,
        'BTTTriggerConfig': {
            'BTTTouchBarItemIconHeight': 22,
            'BTTTouchBarItemIconWidth': 22,
            'BTTTouchBarItemPadding': 0,
            'BTTTouchBarFreeSpaceAfterButton': '5.000000',
            'BTTTouchBarButtonColor': '75.323769, 75.323769, 75.323769, 255.000000',
            'BTTTouchBarAlwaysShowButton': '0',
            'BTTTouchBarAlternateBackgroundColor': '0.000000, 0.000000, 0.000000, 0.000000',
            'BTTTouchBarOnlyShowIcon': 1
        }
    }

def build_config(name, app_name, triggers):
    return {
        'BTTPresetName': name,
        'BTTPresetContent': [
            {
            'BTTAppBundleIdentifier': 'BT.G',
            'BTTAppName': app_name,
            'BTTTriggers': triggers
            }
        ]
    }

def load_icon(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read())

def build_parser():
    parser = argparse.ArgumentParser(
        prog='BTT Currencies Generator',
        description='Generates BTT configuration.'
    )
    parser.add_argument(
        '-o,', '--output',
        type=str,
        nargs='?',
        default=None,
        help='Output file'
    )
    parser.add_argument(
        '--main',
        metavar='[(BITFINEX | BITTREX):CURRENCY:CURRENCY,]',
        type=str,
        nargs='+',
        default=[],
        dest='main',
        help='Currencies on top bar'
    )
    return parser

def build_main_widgets(main_symbols, start_order):
    bitfinex_widget_fun = lambda x: 'do shell script "/usr/local/bin/redis-cli get ' + APP_NAME + ':bitfinex:' + ':'.join(x) + '"'
    bitfinex_action_fun = lambda x: "tell application \"Google Chrome\"\r\tactivate\r\topen location \"https://www.bitfinex.com/t/" + ':'.join(x) + "\"\rend tell"
    bittrex_widget_fun = lambda x: 'do shell script "/usr/local/bin/redis-cli get ' + APP_NAME + ':bittrex:' + ':'.join(x) + '"'
    bittrex_action_fun = lambda x: "tell application \"Google Chrome\"\r\tactivate\r\topen location \"https://bittrex.com/Market/Index?MarketName=" + '-'.join(reversed(x)) + "\"\rend tell"
    
    main_widgets = []
    for i, (exchange, c1, c2) in enumerate(main_symbols):
        symbol = (c1, c2)
        if exchange == 'BITFINEX':
            widget_script = bitfinex_widget_fun(symbol)
            action_script = bitfinex_action_fun(symbol)
        elif exchange == 'BITTREX':
            widget_script = bittrex_widget_fun(symbol)
            action_script = bittrex_action_fun(symbol)
        else:
            continue
        widget = build_symbol_widget(
            ':'.join(symbol), i + start_order, widget_script, action_script
        )
        main_widgets.append(widget)
    return main_widgets

def main():
    parser = build_parser()
    args = parser.parse_args()
    main_symbols = [tuple(symbol.split(':')) for symbol in args.main]
    output = args.output

    bitfinex_widget_fun = lambda c, id: 'do shell script "/usr/local/bin/redis-cli get ' + ':'.join([APP_NAME, 'bitfinex', 'buttons', c, str(id)]) + '"'
    bitfinex_action_fun = lambda c, id: "set currency to do shell script \"/usr/local/bin/redis-cli get " + ':'.join([APP_NAME, 'bitfinex', 'buttons', c, str(id)]) + " | sed 's/^\\\([A-Z0-9]*\\\):.*$/\\\\1/'\"\rtell application \"Google Chrome\"\r\tactivate\r\topen location \"https://www.bitfinex.com/t/\" & currency & \":" + c + "\"\rend tell"
    bitfinex_group = build_group(
        'Bitfinex',
        0,
        {'USD': None, 'BTC': OPTION_KEY_CODE},
        bitfinex_widget_fun,
        bitfinex_action_fun,
        icon=load_icon('resources/bitfinex_icon.png')
    )

    bittrex_widget_fun = lambda c, id: 'do shell script "/usr/local/bin/redis-cli get ' + ':'.join([APP_NAME, 'bittrex', 'buttons', c, str(id)]) + '"'
    bittrex_action_fun = lambda c, id: "set currency to do shell script \"/usr/local/bin/redis-cli get " + ':'.join([APP_NAME, 'bittrex', 'buttons', c, str(id)]) + " | sed 's/^\\\([A-Z0-9]*\\\):.*$/\\\\1/'\"\rtell application \"Google Chrome\"\r\tactivate\r\topen location \"https://bittrex.com/Market/Index?MarketName=" + c + "-\" & currency\rend tell"
    bittrex_group = build_group(
        'Bittrex',
        1,
        {'BTC': None, 'USDT': OPTION_KEY_CODE},
        bittrex_widget_fun,
        bittrex_action_fun,
        icon=load_icon('resources/bittrex_icon.png')
    )

    main_widgets = build_main_widgets(main_symbols, 2)

    triggers = [bitfinex_group, bittrex_group] + main_widgets
    btt_config = build_config('Cryptocurrencies', 'Global', triggers)

    if output is not None:
        with open(output, 'w') as f:
            json.dump(btt_config, f, indent=2)
    else:
        print(json.dumps(btt_config, indent=2))

if __name__ == '__main__':
    main()
