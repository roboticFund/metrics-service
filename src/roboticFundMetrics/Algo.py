
from .roboticFundMetrics import RoboticFundMetrics
from .emitNewTradeEvent import emitNewTradeEvent
import pandas


class Algo:
    algo_number: str
    algo_name: str
    instrument: str
    resolution: str
    accounts_to_run_on: map
    one_pip: float
    event: map
    metrics: RoboticFundMetrics
    latest_tick: pandas.DataFrame

    def __init__(self, algo_params, event, metrics):
        self.algo_name = algo_params['algo_name']
        self.algo_number = algo_params['algo_number']
        self.accounts_to_run_on = algo_params['accounts_to_run_on']
        self.instrument = algo_params['instrument']
        self.resolution = algo_params['resolution']
        self.set_one_pip()
        self.event = event
        self.metrics = metrics

    def set_one_pip(self):
        if self.instrument == 'AUDUSD':
            self.one_pip = 0.0001
        elif self.instrument == 'USDJPY':
            self.one_pip = 0.01
        else:
            self.one_pip = 0.0001

    def run_algo(self):
        print(
            f"Starting RoboticFund {self.algo_number} trading strategy ({self.algo_name})")
        self.set_latest_tick()
        self.generate_trade_events()

    def is_right_instrument_and_resolution(self) -> bool:
        result = self.event['instrument'] == self.instrument and self.event['resolution'] == self.resolution
        if not result:
            print(
                f"Not running {self.algo_number}, {self.algo_name}: The inbound event instrument is not {self.instrument} nor a {self.resolution} ticker which are required to run this trade decision engine.")
        return result

    def set_latest_tick(self) -> None:
        self.latest_tick = self.metrics.df.iloc[-1]

    def generate_trade_events(self) -> None:
        current_price = self.latest_tick['closePrice']
        long_stop = self.latest_tick['long_stop']
        long_profit_take = self.latest_tick['long_profit_take']
        short_stop = self.latest_tick['short_stop']
        short_profit_take = self.latest_tick['short_profit_take']
        algo_name = self.algo_name

        for account in self.accounts_to_run_on:
            print(f"Running on broker account {account['secret_name']}")
            # Long open position
            if self.latest_tick['entry_long']:
                print(f"Placing long trade for {self.instrument}...")
                emitNewTradeEvent(str(self.latest_tick['snapshotTimeUTC']), self.event,
                                  account['secret_name'], algo_name, account['secret_name'], self.instrument, 'LONG', 'Open', long_stop, long_profit_take, current_price, account['size'])
            else:
                print(
                    f"No LONG position to be placed right now for {self.instrument}")

            # Short open position
            if self.latest_tick['entry_short']:
                print(f"Placing short trade for {self.instrument}...")
                emitNewTradeEvent(str(self.latest_tick['snapshotTimeUTC']), self.event,
                                  account['secret_name'], algo_name, account['secret_name'], self.instrument, 'SHORT', 'Open', short_stop, short_profit_take, current_price, account['size'])
            else:
                print(
                    f"No SHORT position to be placed right now for {self.instrument}")

            # Long exit position
            if self.latest_tick['exit_long']:
                print(f"Exiting long positions for {self.instrument}...")
                emitNewTradeEvent(str(self.latest_tick['snapshotTimeUTC']), self.event,
                                  account['secret_name'], algo_name, account['secret_name'], self.instrument, 'LONG', 'Close', None, None, current_price, account['size'])
            else:
                print(
                    f"No LONG position to exit right now for {self.instrument}")

            # Short exit position
            if self.latest_tick['exit_short']:
                print(f"Exiting SHORT positions for {self.instrument}...")
                emitNewTradeEvent(str(self.latest_tick['snapshotTimeUTC']), self.event,
                                  account['secret_name'], algo_name, account['secret_name'], self.instrument, 'SHORT', 'Close', None, None, current_price, account['size'])
            else:
                print(
                    f"No SHORT position to exit right now for {self.instrument}")
