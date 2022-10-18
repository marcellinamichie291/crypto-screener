-- TODO 7: LUCKA load oscillators_rating_4h instead oscillators_rating
SELECT
  bs.ticker,
  bs.exchange,
  si.imb_sell_4h_date,
  si.imb_sell_4h_price,
  si."imb_sell_4h_distance%",
  bs.last_price,
  bs.last_date,
  bs.oscillators_rating
FROM
  base_screening bs,
  seller_imbalances si
WHERE
  bs.ticker = si.ticker
  AND bs.exchange = si.exchange
  AND bs.exchange = 'PhemexFutures'
  AND bs.volatility_rating in ('MEDIUM', 'HIGH')
  AND bs.oscillators_rating in ('BULLISH', 'OVERBOUGHT')
  AND si."imb_sell_4h_distance%" < 0.2
  AND si.imb_sell_4h_date < DATE('now', '-5 day')
    -- AND bs.ticker NOT IN (SELECT swing_short_analysed  FROM trader_data td WHERE swing_short_analysed  != "")
ORDER BY
  si."imb_sell_4h_distance%" ASC