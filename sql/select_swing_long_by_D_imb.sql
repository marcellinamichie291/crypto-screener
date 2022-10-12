SELECT
  bs.ticker,
  bs.exchange,
  bi.imb_buy_D_date,
  bi.imb_buy_D_price,
  bi."imb_buy_D_distance%",
  bs.last_price,
  bs.last_date,
  bs.oscillators_rating
FROM
  base_screening bs,
  buyer_imbalances bi
WHERE
  bs.ticker = bi.ticker
  AND bs.exchange = bi.exchange
  AND bs.exchange = 'PhemexFutures'
  AND bs.volatility_rating in ('MEDIUM', 'HIGH')
  AND bs.oscillators_rating in ('BEARISH', 'OVERSOLD')
  AND bi."imb_buy_D_distance%" < 0.2
  AND bi.imb_buy_D_date < DATE('now', '-5 day')
ORDER BY
  bi."imb_buy_D_distance%" ASC