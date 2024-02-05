
from .TradeEvent import TradeEvent
import boto3
import os


def emitNewTradeEvent(datetime, inputEvent, accountName, secretName, instrument, direction, action, stop, limit, current_price, size):
    client = boto3.client('sns')
    tradeEvent = TradeEvent(datetime, inputEvent,
                            accountName, secretName, instrument, direction, action, stop, limit, current_price, size)
    print(f"Trade event is {tradeEvent.returnSnsFormat()}")
    return client.publish(TargetArn=os.getenv("TRADE_EVENT_TOPIC_ARN"), Message=tradeEvent.returnSnsFormat())
