import json

from utils.algoClassInMemory import AlgoClassInMemory
from utils.dbConnect import dbConnect
from utils.algoClass import AlgoClass
import pandas as pd

# This function will listen to a new data event, e.g. new 10 MIN tick data or multiple ticks
# i.e. we could have MINUTE_10 and MINUTE_30 resolution in the same event


def handler(event, context):
    marketDataArray = returnMarketDataEventFromMessage(event)
    db_con = dbConnect()
    for marketData in marketDataArray:
        df = pd.read_sql_query(f"Select      datetime, instrument, closePrice, EMA_12, EMA_26, EMA_50, EMA_80, macd, macd_new, closePrice, highPrice, lowPrice, stoch_k \
                                  from               metrics \
                                  where              instrument='{marketData.instrument}' and resolution='{marketData.resolution}' and datetime <= '{marketData.datetime}' \
                                  order by           dateTime desc \
                                  limit              500", db_con)
        metrics = AlgoClassInMemory(df)

    # con = dbConnect()
    # for currenTick in marketData:
    #     algoClass = AlgoClass(currenTick, con)
    return {
        'statusCode': 200,
        'body': 'Successfully run createMetrics service'}


def returnMarketDataEventFromMessage(event):
    print('Event inbound: {}'.format(json.dumps(event)))
    eventBody = json.loads(event["Records"][0]["Sns"]
                           ["Message"].replace("\\", ""))
    print('MarketData: {}'.format(json.dumps(eventBody)))
    return eventBody


handler({}, {})
