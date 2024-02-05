class Broker_Id_Resolver:
    market_id_map = [
        {"market_id": "AUDUSD", "IG": "CS.D.AUDUSD.MINI.IP",
            "CI": "400494179", "EOD": ""},
        {"market_id": "EURUSD", "IG": "CS.D.EURUSD.MINI.IP",
            "CI": "154290", "EOD": ""},
        {"market_id": "USDJPY", "IG": "CS.D.USDJPY.MINI.IP",
            "CI": "154303", "EOD": ""},
        {"market_id": "ANZ", "IG": "AA.D.ANZ.CASH.IP",
            "CI": "101471", "EOD": "ANZ.AU"},
        {"market_id": "BHP", "IG": "AA.D.BHP.CASH.IP",
            "CI": "101475", "EOD": "BHP.AU"},
        {"market_id": "CBA", "IG": "AA.D.CBA.CASH.IP",
            "CI": "101506", "EOD": "CBA.AU"},
        {"market_id": "CSL", "IG": "AA.D.CSL.CASH.IP",
            "CI": "101488", "EOD": "CSL.AU"},
        {"market_id": "FMG", "IG": "AA.D.FMG.CASH.IP",
            "CI": "101652", "EOD": "FMG.AU"},
        {"market_id": "MQG", "IG": "AA.D.MQG.CASH.IP",
            "CI": "101633", "EOD": "MQG.AU"},
        {"market_id": "NAB", "IG": "AA.D.NAB.CASH.IP",
            "CI": "101634", "EOD": "NAB.AU"},
        {"market_id": "NST", "IG": "AA.D.NST.CASH.IP",
            "CI": "400510134", "EOD": "NST.AU"},
        {"market_id": "QAN", "IG": "AA.D.QAN.CASH.IP",
            "CI": "101600", "EOD": "QAN.AU"},
        {"market_id": "RIO", "IG": "AA.D.RIO.CASH.IP",
            "CI": "101670", "EOD": "RIO.AU"},
        {"market_id": "WBC", "IG": "AA.D.WBC.CASH.IP",
            "CI": "101664", "EOD": "WBC.AU"},
        {"market_id": "WES", "IG": "AA.D.WES.CASH.IP",
            "CI": "101671", "EOD": "WES.AU"},
    ]

    def __init__(self, marketName):
        self.market_name = marketName
        self.default = f"{marketName} not found!"

    def return_ig_epic(self):
        for market in self.market_id_map:
            if market['market_id'] == self.market_name:
                return market['IG']

    def return_ci_epic(self):
        for market in self.market_id_map:
            if market['market_id'] == self.market_name:
                return market['CI']

    def return_eod_epic(self):
        for market in self.market_id_map:
            if market['market_id'] == self.market_name:
                return market['EOD']
