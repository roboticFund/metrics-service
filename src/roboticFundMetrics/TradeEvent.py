# Class must match Schema definition in ../lib/trade-decision-engine.ts
import json


class TradeEvent:

    def __init__(self, datetime, inputEvent, accountName, instrument, direction, action, stop, limit):
        self.datetime = datetime
        self.inputEvent = inputEvent
        self.accountName = accountName
        self.instrument = instrument
        self.direction = direction
        self.action = action
        self.stop = stop
        self.limit = limit

    def returnSnsFormat(self):
        return json.dumps({
            "datetime": self.datetime,
            "inputEvent": self.inputEvent,
            "accountName": self.accountName,
            "instrument": self.instrument,
            "direction": self.direction,
            "action": self.action,
            "stop": self.stop,
            "limit": self.limit
        })
