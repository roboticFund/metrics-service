import json
from utils.dbConnect import dbConnect
from utils.algoClass import AlgoClass

# This function will listen to a new data event, e.g. new 10 MIN tick data.


def handler(event, context):
    marketData = returnMarketDataEventFromMessage(event)
    con = dbConnect()
    algoClass = AlgoClass(marketData, con)

    return {
        'statusCode': 200,
        'body': 'Successfully run createMetrics service'}


def returnDataForNewMetricEvent():
    # return all data for newMetric event
    pass


def returnMarketDataEventFromMessage(event):
    print('Event inbound: {}'.format(json.dumps(event)))
    eventBody = json.loads(event["Records"][0]["Sns"]
                           ["Message"].replace("\\", ""))
    print('MarketData: {}'.format(json.dumps(eventBody)))
    return eventBody
