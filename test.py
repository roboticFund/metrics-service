from roboticFundMetrics import RoboticFundMetrics
import pandas as pd

marketData = pd.read_csv('./data/AUDUSD_10MIN.csv')

df = RoboticFundMetrics(marketData)

print(df.df.tail(50))
