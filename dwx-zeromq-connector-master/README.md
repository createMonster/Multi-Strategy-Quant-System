# DWX ZeroMQ Connector  { Python 3 to MetaTrader 4 }

# Latest version: 2.0.1 [(here)](https://github.com/darwinex/dwx-zeromq-connector/tree/master/v2.0.1)

## Need help? Join the [Darwinex Collective Slack](https://join.slack.com/t/darwinex-collective/shared_invite/enQtNjg4MjA0ODUzODkyLWFiZWZlMDZjNGVmOGE2ZDBiZGI4ZWUxNjM5YTU0MjZkMTQ2NGZjNGIyN2QxZDY4NjUyZmVlNmU3N2E2NGE1Mjk) for code updates, Q&A and more.

## About Darwinex

[Darwinex](https://www.darwinex.com/?utm_source=github&utm_medium=zeromq-readme&utm_content=about-us-above-the-fold) is a **UK FCA-Regulated broker & technology provider**, enabling traders to:

1. Trade the markets on the best terms and competitive execution conditions 
1. Develop their trading skills and build verifiable, investable track records
1. Provide regulatory cover to attract capital and charge a 20% performance fee on investor profits

**Please take a moment to read our Risk Disclosure [here](https://www.darwinex.com/legal/risk-disclaimer?utm_source=github&utm_medium=zeromq-readme&utm_content=about-us-above-the-fold)**

**[Click here to visit our Trader Hall of Fame](https://www.darwinex.com/darwinia/hall-of-fame?utm_source=github&utm_medium=zeromq-readme&utm_content=about-us-above-the-fold)** * **ranked by Performance Fees earned (over 2M EUR paid to date)**

**[Click here to Open a Darwinex Trading Account](https://www.darwinex.com/register?utm_source=github&utm_medium=zeromq-readme&utm_content=about-us-above-the-fold)**

## Table of Contents
* [Introduction](#introduction)
* [Installation](#installation)
* [Configuration](#configuration)
* [Example Usage](#example-usage)
* [Video Tutorials](#video-tutorials)
* [Complete list of available functions](#available-functions)
* [License](#license) 

## Introduction
In this project, we present a technique employing ZeroMQ (an Open Source, Asynchronous Messaging Library and Concurrency Framework) for building a basic – but easily extensible – high performance bridge between external (non-MQL) programming languages and MetaTrader 4.

### IMPORTANT NOTES - PLEASE READ:

1. **Please note that we cannot provide support for Python or MQL as programming languages themselves.** Therefore, if you are new to Python and MQL, incorporating the project into your specific algorithmic trading environment will require some additional work on your part (i.e. enough Python experience to integrate the Bridge into your environment -> it is assumed that users of the Bridge are self-sufficient in Python).

1. Any code provided and/or referenced in this repository is NOT meant to be used "as-is". Users must treat all code as educational content that requires modification / incorporation into existing works, as per their individual requirements.

1. We have drafted as detailed a set of steps as possible in our project README, but cannot cover all the dependencies as they are independent projects on their own that programmers need to account for / follow / keep up to speed with when considering using the DWX ZeroMQ Connector.

1. This project and all accompanying source code should be run standalone (i.g. via a Python or IPython console, or batch process).

1. **Please DO NOT run this code in Jupyter or IPython Notebooks.**

1. The project's dependencies require **MS VC++ Libraries**. Without these installed, you are likely to run into **"Resource Timeout" errors.** The DLLs in the dependency projects (mql-zmq, libzmq, libsodium) require that you have the **latest Visual C++ runtime (2015) libraries already installed.**

1. This project has not been tested on emulated environments (e.g. WINE, VMWare, etc).

1. This project is intended for use solely in Windows 10 environments, at the present time.
	
**Reasons for writing this post:**

* Lack of comprehensive, publicly available literature about this topic on the web.
* Traders have traditionally relied on Winsock/WinAPI based solutions that often require revision with both Microsoft™ and MetaQuotes™ updates.
* Alternatives to ZeroMQ include named pipes, and approaches where filesystem-dependent functionality forms the bridge between MetaTrader and external languages.

**We lay the foundation for a distributed trading system that will:**

* Consist of one or more trading strategies developed outside MetaTrader 4 (non-MQL),
* Use MetaTrader 4 for acquiring market data, trade execution and management,
* Support multiple non-MQL strategies interfacing with MetaTrader 4 simultaneously,
* Consider each trading strategy as an independent “Client”,
* Consider MetaTrader 4 as the “Server”, and medium to market,
* Permit both Server and Clients to communicate with each other on-demand.

**Infographic: ZeroMQ-Enabled Distributed Trading Infrastructure (with MetaTrader 4)**
![DWX ZMQ Infographic 1](resources/images/dwx-zeromq-infographic-1.png)

**Why ZeroMQ?**

* Enables programmers to connect any code to any other code, in a number of ways.
* Eliminates a MetaTrader user’s dependency on just MetaTrader-supported technology (features, indicators, language constructs, libraries, etc.)
* Traders can develop indicators and strategies in C/C#/C++, Python, R and Java (to name a few), and deploy to market via MetaTrader 4.
* Leverage machine learning toolkits in Python and R for complex data analysis and strategy development, while interfacing with MetaTrader 4 for trade execution and management.
* ZeroMQ can be used as a high-performance transport layer in sophisticated, distributed trading systems otherwise difficult to implement in MQL.
* Different strategy components can be built in different languages if required, and seamlessly talk to each other over TCP, in-process, inter-process or multicast protocols.
* Multiple communication patterns and disconnected operation.

## Installation

This project requires the following:

* **Python**: (minimum v3.6)
* **libzmq**: (minimum v4.2.5)
* **pyzmq**: (minimum v17.1.2)
* **libsodium** (https://github.com/jedisct1/libsodium)
* **mql4-lib** (https://github.com/dingmaotu/mql4-lib)
* **mql-zmq** (https://github.com/dingmaotu/mql-zmq)

You may install Python-specific dependencies either via `pip install -r ./v2.0.1/python/api/requirements.txt ` or via installing the latest Anaconda distribution (Python 3 variants).

For your convenience, files from the last three items above have been included in this repository with appropriate copyrights referenced within. 

_This project incorporates functionality authored by Ding Li (GitHub: https://github.com/dingmaotu), who has kindly licensed his work under the Apache 2.0 license._

_We acknowledge copyright as per the terms of the license, the following repositories serving as mandatory dependencies for this project:_

1. _https://github.com/dingmaotu/mql-zmq_

1. _https://github.com/dingmaotu/mql4-lib_

_Thank you Ding for your amazing open source contribution to this space!_

_Sincerely,_<br>
_The Darwinex Labs Team_<br>
_www.darwinex.com_


### Steps:

1. Download and unzip **mql-zmq-master.zip** (by GitHub author @dingmaotu)
1. Copy the contents of **mql-zmq-master/Include/Mql** and **mql-zmq-master/Include/Zmq** into your MetaTrader installation's **MQL4/Include** directory as-is. Your **MQL4/Include** directory should now have two additional folders "Mql" and "Zmq".
1. Copy **libsodium.dll** and **libzmq.dll** from **mql-zmq-master/Library/MT4** to your MetaTrader installation's **MQL4/Libraries** directory.
1. Download **DWX_ZeroMQ_Server_vX.Y.Z_RCx.mq4** and place it inside your MetaTrader installation's **MQL4/Experts** directory.
1. Finally, download **v2.0.1 / python / api / DWX_ZeroMQ_Connector_v2_0_1_RC8.py**.

## Configuration

1. After completing the steps above, terminate and restart MetaTrader 4.
1. Open any new chart, e.g. EUR/USD M, then drag and drop **DWX_ZeroMQ_Server_v2.0.1_RC8**.
1. Switch to the EA's Inputs tab and customize values as necessary:

    ![EA Inputs](resources/images/expert-inputs.png)
1. Note: The variable **Publish_MarketData** was removed in recent versions. There is no need to modify this variable or to manually change the **Publish_Symbols** array. Symbols will automatically be added when the `_DWX_MTX_SEND_TRACKPRICES_REQUEST_()` function is called in python (see code example below). 


	![MetaTrader Publishing Tick Data 1](resources/images/ZeroMQ_Server_Publishing_Symbol_Data.gif)
	
	![MetaTrader Publishing Tick Data 2](resources/images/InAction_ZeroMQ_Server_Publishing_Symbol_Data.gif)

## Example Usage

### Subscribe/Unsubscribe to/from EUR/USD bid/ask prices in real-time:
```
# subscribe to data:
_zmq._DWX_MTX_SUBSCRIBE_MARKETDATA_('EURUSD')
# tell MT4 to publish data:
_zmq._DWX_MTX_SEND_TRACKPRICES_REQUEST_(['EURUSD'])

Output:
[KERNEL] Subscribed to EURUSD BID/ASK updates. See self._Market_Data_DB.

# BID/ASK prices are now being streamed into _zmq._Market_Data_DB.
_zmq._Market_Data_DB

Output: 
{'EURUSD': {
  '2019-01-08 13:46:49.157431': (1.14389, 1.14392),
  '2019-01-08 13:46:50.673151': (1.14389, 1.14393),
  '2019-01-08 13:46:51.010993': (1.14392, 1.14395),
  '2019-01-08 13:46:51.100941': (1.14394, 1.14398),
  '2019-01-08 13:46:51.205881': (1.14395, 1.14398),
  '2019-01-08 13:46:52.283107': (1.14394, 1.14397),
  '2019-01-08 13:46:52.377055': (1.14395, 1.14398),
  '2019-01-08 13:46:52.777823': (1.14394, 1.14398),
  '2019-01-08 13:46:52.870773': (1.14395, 1.14398),
  '2019-01-08 13:46:52.985708': (1.14395, 1.14397),
  '2019-01-08 13:46:53.080652': (1.14393, 1.14397),
  '2019-01-08 13:46:53.196584': (1.14394, 1.14398),
  '2019-01-08 13:46:53.294541': (1.14393, 1.14397)}}

_zmq._DWX_MTX_UNSUBSCRIBE_MARKETDATA('EURUSD')

Output:
**
[KERNEL] Unsubscribing from EURUSD
**
```

### Initialize Connector:
```
_zmq = DWX_ZeroMQ_Connector()
```

### Construct Trade to send via ZeroMQ to MetaTrader:
```
_my_trade = _zmq._generate_default_order_dict()

Output: 
{'_action': 'OPEN',
 '_type': 0,
 '_symbol': 'EURUSD',
 '_price': 0.0,
 '_SL': 500,
 '_TP': 500,
 '_comment': 'DWX_Python_to_MT',
 '_lots': 0.01,
 '_magic': 123456,
 '_ticket': 0}

_my_trade['_lots'] = 0.05

_my_trade['_SL'] = 250

_my_trade['_TP'] = 750

_my_trade['_comment'] = 'nerds_rox0r'
```

### Send trade to MetaTrader:
```
_zmq._DWX_MTX_NEW_TRADE_(_order=_my_trade)

# MetaTrader response (JSON):
{'_action': 'EXECUTION', 
'_magic': 123456, 
'_ticket': 85051741, 
'_open_price': 1.14414, 
'_sl': 250, 
'_tp': 750}
```

### Get all open trades from MetaTrader:
```
_zmq._DWX_MTX_GET_ALL_OPEN_TRADES_()

# MetaTrader response (JSON):

{'_action': 'OPEN_TRADES', 
'_trades': {
    85051741: {'_magic': 123456, 
                '_symbol': 'EURUSD', 
                '_lots': 0.05, 
                '_type': 0, 
                '_open_price': 1.14414, 
                '_pnl': -0.45}
    }
}
```

### Partially close 0.01 lots:
```
_zmq._DWX_MTX_CLOSE_PARTIAL_BY_TICKET_(85051741, 0.01)

# MetaTrader response (JSON):
{'_action': 'CLOSE', 
'_ticket': 85051741, 
'_response': 'CLOSE_PARTIAL', 
'_close_price': 1.14401, 
'_close_lots': 0.01}

# Partially closing a trade renews the ticket ID, retrieve it again.

_zmq._DWX_MTX_GET_ALL_OPEN_TRADES_()

# MetaTrader response (JSON):
{'_action': 'OPEN_TRADES', 
'_trades': {
    85051856: {'_magic': 123456, 
                '_symbol': 'EURUSD', 
                '_lots': 0.04, 
                '_type': 0, 
                '_open_price': 1.14414, 
                '_pnl': -0.36}
    }
}
```

### Close a trade by ticket:
```
_zmq._DWX_MTX_CLOSE_TRADE_BY_TICKET_(85051856)

# MetaTrader response (JSON):
{'_action': 'CLOSE', 
'_ticket': 85051856, 
'_close_price': 1.14378, 
'_close_lots': 0.04, 
'_response': 'CLOSE_MARKET', 
'_response_value': 'SUCCESS'}
```

### Close all trades by Magic Number:
```
# Before running the following example, 5 trades were executed using the same values as in "_my_trade" above, the magic number being 123456.

# Check currently open trades.

_zmq._DWX_MTX_GET_ALL_OPEN_TRADES_()

# MetaTrader response (JSON):
{'_action': 'OPEN_TRADES', 
    '_trades': {
        85052022: {'_magic': 123456, '_symbol': 'EURUSD', '_lots': 0.05, '_type': 0, '_open_price': 1.14353, '_pnl': 1.15}, 
        85052026: {'_magic': 123456, '_symbol': 'EURUSD', '_lots': 0.05, '_type': 0, '_open_price': 1.14354, '_pnl': 1.1}, 
        85052025: {'_magic': 123456, '_symbol': 'EURUSD', '_lots': 0.05, '_type': 0, '_open_price': 1.14354, '_pnl': 1.1}, 
        85052024: {'_magic': 123456, '_symbol': 'EURUSD', '_lots': 0.05, '_type': 0, '_open_price': 1.14354, '_pnl': 1.1}, 
        85052023: {'_magic': 123456, '_symbol': 'EURUSD', '_lots': 0.05, '_type': 0, '_open_price': 1.14356, '_pnl': 1}
    }
}

# Close all trades with magic number 123456
_zmq._DWX_MTX_CLOSE_TRADES_BY_MAGIC_(123456)

# MetaTrader response (JSON):
{'_action': 'CLOSE_ALL_MAGIC', '_magic': 123456, 
'_responses': {
    85052026: {'_symbol': 'EURUSD', '_close_price': 1.14375, '_close_lots': 0.05, '_response': 'CLOSE_MARKET'}, 
    85052025: {'_symbol': 'EURUSD', '_close_price': 1.14375, '_close_lots': 0.05, '_response': 'CLOSE_MARKET'}, 
    85052024: {'_symbol': 'EURUSD', '_close_price': 1.14375, '_close_lots': 0.05, '_response': 'CLOSE_MARKET'}, 
    85052023: {'_symbol': 'EURUSD', '_close_price': 1.14375, '_close_lots': 0.05, '_response': 'CLOSE_MARKET'}, 
    85052022: {'_symbol': 'EURUSD', '_close_price': 1.14375, '_close_lots': 0.05, '_response': 'CLOSE_MARKET'}}, 
'_response_value': 'SUCCESS'}
```

### Close ALL open trades:
```

# Open 5 trades

_zmq._DWX_MTX_NEW_TRADE_()
{'_action': 'EXECUTION', '_magic': 123456, '_ticket': 85090920, '_open_price': 1.15379, '_sl': 500, '_tp': 500}

_zmq._DWX_MTX_NEW_TRADE_()
{'_action': 'EXECUTION', '_magic': 123456, '_ticket': 85090921, '_open_price': 1.15379, '_sl': 500, '_tp': 500}

_zmq._DWX_MTX_NEW_TRADE_()
{'_action': 'EXECUTION', '_magic': 123456, '_ticket': 85090922, '_open_price': 1.15375, '_sl': 500, '_tp': 500}

_zmq._DWX_MTX_NEW_TRADE_()
{'_action': 'EXECUTION', '_magic': 123456, '_ticket': 85090926, '_open_price': 1.15378, '_sl': 500, '_tp': 500}

_zmq._DWX_MTX_NEW_TRADE_()
{'_action': 'EXECUTION', '_magic': 123456, '_ticket': 85090927, '_open_price': 1.15378, '_sl': 500, '_tp': 500}

# Close all open trades
_zmq._DWX_MTX_CLOSE_ALL_TRADES_()

# MetaTrader response (JSON):
{'_action': 'CLOSE_ALL',
 '_responses': {85090927: {'_symbol': 'EURUSD',
   '_magic': 123456,
   '_close_price': 1.1537,
   '_close_lots': 0.01,
   '_response': 'CLOSE_MARKET'},
  85090926: {'_symbol': 'EURUSD',
   '_magic': 123456,
   '_close_price': 1.1537,
   '_close_lots': 0.01,
   '_response': 'CLOSE_MARKET'},
  85090922: {'_symbol': 'EURUSD',
   '_magic': 123456,
   '_close_price': 1.1537,
   '_close_lots': 0.01,
   '_response': 'CLOSE_MARKET'},
  85090921: {'_symbol': 'EURUSD',
   '_magic': 123456,
   '_close_price': 1.15369,
   '_close_lots': 0.01,
   '_response': 'CLOSE_MARKET'},
  85090920: {'_symbol': 'EURUSD',
   '_magic': 123456,
   '_close_price': 1.15369,
   '_close_lots': 0.01,
   '_response': 'CLOSE_MARKET'}},
 '_response_value': 'SUCCESS'}
```

## Video Tutorials

**Step-by-Step Installation & Configuration Tutorials**

1. [Introduction](https://www.youtube.com/watch?v=Qv04zPU7lxQ&list=PLv-cA-4O3y97vTpghgRqiPBjmpgWskYDl&index=1)

1. [Dependencies](https://www.youtube.com/watch?v=YdlSwrKt9TU&list=PLv-cA-4O3y97vTpghgRqiPBjmpgWskYDl&index=2)

1. [MetaTrader 4 Setup](https://www.youtube.com/watch?v=N0-aYLllK3E&list=PLv-cA-4O3y97vTpghgRqiPBjmpgWskYDl&index=3)

1. [Programming Environment Setup](https://www.youtube.com/watch?v=ia1E5xczouc&list=PLv-cA-4O3y97vTpghgRqiPBjmpgWskYDl&index=4)

1. [ZeroMQ Client Configuration](https://www.youtube.com/watch?v=qMNSr-Hiupk&list=PLv-cA-4O3y97vTpghgRqiPBjmpgWskYDl&index=5)

1. [ZeroMQ Server Configuration](https://www.youtube.com/watch?v=ONBFOGsnijU&list=PLv-cA-4O3y97vTpghgRqiPBjmpgWskYDl&index=6)

1. [Example Usage](https://www.youtube.com/watch?v=U2VdXdm2qlM&list=PLv-cA-4O3y97vTpghgRqiPBjmpgWskYDl&index=7)

**The nuts & bolts of the DWX ZeroMQ Connector project**

1. [How to Interface Python/R Trading Strategies with MetaTrader 4](https://www.youtube.com/watch?v=GGOajzvl860)

1. [Algorithmic Trading via ZeroMQ: Trade Execution, Reporting & Management (Python to MetaTrader)](https://youtu.be/3nM0c2kG_Sw)

1. [Algorithmic Trading via ZeroMQ: Subscribing to Market Data (Python to MetaTrader)](https://youtu.be/9EaP_7sSzEI)

1. [Build Algorithmic Trading Strategies with Python & ZeroMQ: Part 1](https://www.youtube.com/watch?v=4MxjFTQHTfw)

1. [Build Algorithmic Trading Strategies with Python & ZeroMQ: Part 2](https://www.youtube.com/watch?v=VtOfF-nhhj8)

1. [Troubleshooting Python, ZeroMQ & MetaTrader Configuration for Algorithmic Trading](https://www.youtube.com/watch?v=7aAsFZ_r5zU&list=PLv-cA-4O3y94ygY4qDlfCcDqkMmqMteah&index=6)

## Available functions:

1. DWX_MTX_NEW_TRADE_(self, _order=None)
1. DWX_MTX_MODIFY_TRADE_BY_TICKET_(self, _ticket, _SL, _TP)
1. DWX_MTX_CLOSE_TRADE_BY_TICKET_(self, _ticket)
1. DWX_MTX_CLOSE_PARTIAL_BY_TICKET_(self, _ticket, _lots)
1. DWX_MTX_CLOSE_TRADES_BY_MAGIC_(self, _magic)
1. DWX_MTX_CLOSE_ALL_TRADES_(self)
1. DWX_MTX_GET_ALL_OPEN_TRADES_(self)
1. generate_default_order_dict(self)
1. generate_default_data_dict(self)
1. DWX_MTX_SEND_MARKETDATA_REQUEST_(self, _symbol, _timeframe, _start, _end)
1. DWX_MTX_SEND_COMMAND_(self, _action, _type, _symbol, _price, _SL, _TP, _comment, _lots, _magic, _ticket)
1. DWX_MTX_SUBSCRIBE_MARKETDATA_(self, _symbol, _string_delimiter=';')
1. DWX_MTX_UNSUBSCRIBE_MARKETDATA_(self, _symbol)
1. DWX_MTX_UNSUBSCRIBE_ALL_MARKETDATA_REQUESTS_(self)

## License

BSD 3-Clause License

Copyright (c) 2019, Darwinex.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

