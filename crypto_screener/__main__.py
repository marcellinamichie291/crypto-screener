import logging.config

import pandas as pd

from crypto_screener.constants import LOGGER_CONFIG_FILE_PATH, CONFIG_FILE_PATH, __logo__
from crypto_screener.service.data_downloader import DataDownloader
from crypto_screener.step.crypto_base_screening_step import CryptoBaseScreeningStep
from crypto_screener.step.crypto_imbalance_screening_step import CryptoImbalanceScreeningStep
from crypto_screener.utils import load_config

logging.config.fileConfig(fname=LOGGER_CONFIG_FILE_PATH, disable_existing_loggers=False)
logging.info(__logo__)
config = load_config(CONFIG_FILE_PATH)

if __name__ == "__main__":
    data_downloader = DataDownloader(config["Services"]["DataDownloader"]["rateExceedDelaySeconds"])
    base_screening_step = CryptoBaseScreeningStep(data_downloader)
    imbalance_screening_step = CryptoImbalanceScreeningStep(
        config["Steps"]["ImbalanceScreeningStep"]["dailyOhlcHistory"],
        config["Steps"]["ImbalanceScreeningStep"]["weeklyOhlcHistory"],
        config["Steps"]["ImbalanceScreeningStep"]["monthlyOhlcHistory"],
        data_downloader)

    assets = pd.read_csv(config["Base"]["assetsPath"])

    if config["Steps"]["BaseScreeningStep"]["enable"]:
        result = base_screening_step.process(assets)
        result.to_csv(config["Steps"]["BaseScreeningStep"]["outputPath"], index=False)

    if config["Steps"]["ImbalanceScreeningStep"]["enable"]:
        result = imbalance_screening_step.process(assets)
        result.to_csv(config["Steps"]["ImbalanceScreeningStep"]["outputPath"], index=False)
