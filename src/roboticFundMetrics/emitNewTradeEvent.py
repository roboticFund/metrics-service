
from .TradeEvent import TradeEvent
import boto3
import os


def emitNewTradeEvent(datetime, inputEvent, accountName, instrument, direction, action, stop, limit):
    client = boto3.client('sns')
    tradeEvent = TradeEvent(datetime, inputEvent,
                            accountName, instrument, direction, action, stop, limit)

    return client.publish(TargetArn=os.getenv("TRADE_EVENT_TOPIC_ARN"), Message=tradeEvent.returnSnsFormat(), MessageStructure='json')
