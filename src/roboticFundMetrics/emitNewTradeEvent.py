
from .TradeEvent import TradeEvent
import boto3


def emitNewTradeEvent(datetime, inputEvent, accountName, instrument, direction, action, stop, limit):
    client = boto3.client('sns')
    tradeEvent = TradeEvent(datetime, inputEvent,
                            accountName, instrument, direction, action, stop, limit)

    return client.publish(TargetArn="arn:aws:sns:ap-southeast-2:302826945104:TradeDecisionEngine-newTradeEventA11BB639-ZEoklthJHhYP", Message=tradeEvent.returnSnsFormat(), MessageStructure='json')
