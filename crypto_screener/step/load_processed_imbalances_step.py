import logging

import pandas as pd

from crypto_screener.constants import SEPARATOR


class LoadProcessedImbalancesStep:

    def __init__(self, config, crypto_screener_db_conn):
        step_config = config["steps"]["loadProcessedImbalancesStep"]
        self.buyer_imbalances_processed_path = step_config["buyerImbalancesProcessedPath"]
        self.seller_imbalances_processed_path = step_config["sellerImbalancesProcessedPath"]
        self.buyer_imbalances_interest_path = step_config["buyerImbalancesInterestPath"]
        self.seller_imbalances_interest_path = step_config["sellerImbalancesInterestPath"]
        self.crypto_screener_db_conn = crypto_screener_db_conn

    def process(self):
        logging.info(SEPARATOR)
        logging.info("Start load processed imbalances to database step")
        logging.info(SEPARATOR)

        buyer_imbalances_processed = pd.read_csv(self.buyer_imbalances_processed_path)
        seller_imbalances_processed = pd.read_csv(self.seller_imbalances_processed_path)
        buyer_imbalances_interest = pd.read_csv(self.buyer_imbalances_interest_path)
        seller_imbalances_interest = pd.read_csv(self.seller_imbalances_interest_path)

        buyer_imbalances_processed.to_sql(name="buyer_imbalances_processed", con=self.crypto_screener_db_conn,
                                          if_exists="replace")
        seller_imbalances_processed.to_sql(name="seller_imbalances_processed", con=self.crypto_screener_db_conn,
                                           if_exists="replace")

        buyer_imbalances_interest.to_sql(name="buyer_imbalances_interest", con=self.crypto_screener_db_conn,
                                         if_exists="replace")
        seller_imbalances_interest.to_sql(name="seller_imbalances_interest", con=self.crypto_screener_db_conn,
                                          if_exists="replace")

        logging.info(SEPARATOR)
        logging.info("Finished load processed imbalances to database step")
        logging.info(SEPARATOR)
