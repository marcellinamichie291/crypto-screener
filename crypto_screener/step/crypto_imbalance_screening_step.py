import logging

import pandas as pd

from crypto_screener.constants import SEPARATOR
from crypto_screener.service.data_downloader import DataDownloader
from crypto_screener.service.imbalance_service import ImbalanceService
from crypto_screener.utils import parse_last_date, parse_last_price


class CryptoImbalanceScreeningStep:

    def __init__(self, four_hours_ohlc_history: int, daily_ohlc_history: int, weekly_ohlc_history: int,
                 monthly_ohlc_history: int, data_downloader: DataDownloader):
        self.four_hours_ohlc_history = four_hours_ohlc_history
        self.daily_ohlc_history = daily_ohlc_history
        self.weekly_ohlc_history = weekly_ohlc_history
        self.monthly_ohlc_history = monthly_ohlc_history
        self.data_downloader = data_downloader
        self.imbalance_service = ImbalanceService()

    def process(self, assets: pd.DataFrame):
        result_buyer_imbalances = pd.DataFrame()
        result_seller_imbalances = pd.DataFrame()

        logging.info(SEPARATOR)
        logging.info("Start crypto imbalance screening step")
        logging.info(SEPARATOR)

        count_assets = assets.shape[0]

        for index, asset in assets.iterrows():
            logging.info("Process asset - {} ({}/{})".format(asset["Asset"], index + 1, count_assets))
            try:
                exchange = asset["Exchange"]
                ohlc_4h = self.data_downloader.download_ohlc(exchange, asset["Asset"], "4h",
                                                             self.four_hours_ohlc_history)
                ohlc_daily = self.data_downloader.download_ohlc(exchange, asset["Asset"], "1d",
                                                                self.daily_ohlc_history)
                ohlc_weekly = self.data_downloader.download_ohlc(exchange, asset["Asset"], "1w",
                                                                 self.weekly_ohlc_history)
                ohlc_monthly = self.data_downloader.download_ohlc(exchange, asset["Asset"], "1M",
                                                                  self.monthly_ohlc_history)

                last_price = parse_last_price(ohlc_daily)
                asset["LastPrice"] = last_price
                asset["LastDate"] = parse_last_date(ohlc_daily)

                asset_with_buyer_imbalances = asset.copy()
                self.append_first_buyer_untested_imbalance(asset_with_buyer_imbalances, last_price, "4h", ohlc_4h)
                self.append_first_buyer_untested_imbalance(asset_with_buyer_imbalances, last_price, "M", ohlc_monthly)
                self.append_first_buyer_untested_imbalance(asset_with_buyer_imbalances, last_price, "W", ohlc_weekly)
                self.append_first_buyer_untested_imbalance(asset_with_buyer_imbalances, last_price, "D", ohlc_daily)

                asset_with_seller_imbalances = asset.copy()
                self.append_first_buyer_untested_imbalance(asset_with_buyer_imbalances, last_price, "4h", ohlc_4h)
                self.append_first_seller_untested_imbalance(asset_with_seller_imbalances, last_price, "M", ohlc_monthly)
                self.append_first_seller_untested_imbalance(asset_with_seller_imbalances, last_price, "W", ohlc_weekly)
                self.append_first_seller_untested_imbalance(asset_with_seller_imbalances, last_price, "D", ohlc_daily)

                result_buyer_imbalances = pd.concat(
                    [result_buyer_imbalances, pd.DataFrame([asset_with_buyer_imbalances])])
                result_seller_imbalances = pd.concat(
                    [result_seller_imbalances, pd.DataFrame([asset_with_seller_imbalances])])
            except:
                logging.exception("Problem with compute imbalance on coin {}".format(asset["Asset"]))
                result_buyer_imbalances = pd.concat(
                    [result_buyer_imbalances, pd.DataFrame([asset])])
                result_seller_imbalances = pd.concat(
                    [result_seller_imbalances, pd.DataFrame([asset])])

        logging.info(SEPARATOR)
        logging.info("Finished crypto imbalance screening step")
        logging.info(SEPARATOR)

        return result_buyer_imbalances, result_seller_imbalances

    def append_first_buyer_untested_imbalance(self, asset, last_price, time_frame, ohlc):
        buyer_imbalances = self.imbalance_service.find_buyer_imbalances(ohlc)

        if buyer_imbalances.empty:
            asset["IMB_BUY_{} date".format(time_frame)] = ""
            asset["IMB_BUY_{} price".format(time_frame)] = ""
            asset["IMB_BUY_{} %distance".format(time_frame)] = 1
            return

        first_buyer_untested_imbalance = buyer_imbalances.loc[buyer_imbalances["tested"] == False].tail(1)

        if first_buyer_untested_imbalance.empty:
            asset["IMB_BUY_{} date".format(time_frame)] = ""
            asset["IMB_BUY_{} price".format(time_frame)] = ""
            asset["IMB_BUY_{} %distance".format(time_frame)] = 1
            return

        imbalance_price = first_buyer_untested_imbalance["price"].values[0]
        asset["IMB_BUY_{} date".format(time_frame)] = first_buyer_untested_imbalance["date"].values[0]
        asset["IMB_BUY_{} price".format(time_frame)] = imbalance_price
        asset["IMB_BUY_{} %distance".format(time_frame)] = round(1 - (imbalance_price / last_price), 2)

    def append_first_seller_untested_imbalance(self, asset, last_price, time_frame, ohlc):
        seller_imbalances = self.imbalance_service.find_selling_imbalances(ohlc)

        if seller_imbalances.empty:
            asset["IMB_SELL_{} date".format(time_frame)] = ""
            asset["IMB_SELL_{} price".format(time_frame)] = ""
            asset["IMB_SELL_{} %distance".format(time_frame)] = 1
            return

        first_seller_untested_imbalance = seller_imbalances.loc[seller_imbalances["tested"] == False].tail(1)

        if first_seller_untested_imbalance.empty:
            asset["IMB_SELL_{} date".format(time_frame)] = ""
            asset["IMB_SELL_{} price".format(time_frame)] = ""
            asset["IMB_SELL_{} %distance".format(time_frame)] = 1
            return

        imbalance_price = first_seller_untested_imbalance["price"].values[0]
        asset["IMB_SELL_{} date".format(time_frame)] = first_seller_untested_imbalance["date"].values[0]
        asset["IMB_SELL_{} price".format(time_frame)] = imbalance_price
        asset["IMB_SELL_{} %distance".format(time_frame)] = round(1 - (imbalance_price / last_price), 2) * -1
