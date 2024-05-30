
from .TradeEvent import TradeEvent
import boto3
import os


def emitNewTradeEvent(datetime, inputEvent, accountName, algoName, secretName, instrument, direction, action, stop, limit, current_price, size):
    tradeEvent = TradeEvent(datetime, inputEvent,
                            accountName, algoName, secretName, instrument, direction, action, stop, limit, current_price, size)
    print(f"Trade event is {tradeEvent.returnSnsFormat()}")
    if (os.environ.get("ENV").lower() == "dev"):
        print("Running in dev, not sending to AWS...")
        return
    else:
        client = boto3.client('sns')
        return client.publish(TargetArn=os.getenv("TRADE_EVENT_TOPIC_ARN"), Message=tradeEvent.returnSnsFormat())
