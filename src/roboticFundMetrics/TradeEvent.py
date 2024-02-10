# Class must match Schema definition in ../lib/trade-decision-engine.ts
import json

trade_event_schema = {
    "datetime": "date-time",
    "inputEvent": "string",
    "accountName": "string",
    "instrument": "string",
    "direction": "string",
    "action": "string",
    "stop": "number",
    "limit": "number"
}


class TradeEvent:

    def __init__(self, datetime, inputEvent, accountName, algoName, secretName, instrument, direction, action, stop, limit, current_price, size):
        self.datetime = datetime
        self.inputEvent = inputEvent
        self.accountName = accountName
        self.algoName = algoName
        self.instrument = instrument
        self.direction = direction
        self.action = action
        self.stop = stop
        self.limit = limit
        self.level = current_price
        self.secretName = secretName
        self.size = size

    def returnSnsFormat(self):
        return json.dumps({
            "datetime": self.datetime,
            "inputEvent": self.inputEvent,
            "accountName": self.accountName,
            "algoName": self.algoName,
            "secretName": self.secretName,
            "instrument": self.instrument,
            "direction": self.direction,
            "action": self.action,
            "stop": self.stop,
            "limit": self.limit,
            "level": self.level,
            "size": self.size
        })
