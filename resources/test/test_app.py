import unittest
from app import returnMarketDataEventFromMessage
from .data.expectedMarketData import marketDataExpected
from .data.realIboundEvent import event


class TestApp(unittest.TestCase):

    def test_eventbody(self):
        marketdata = returnMarketDataEventFromMessage(event)
        self.assertEqual(marketdata, marketDataExpected,
                         "MarketData should be equal")
