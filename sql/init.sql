-- Initializes the application table inside the ${POSTGRES_DB} database
CREATE TABLE IF NOT EXISTS stock_prices (
  symbol TEXT NOT NULL,
  date   DATE NOT NULL,
  open   NUMERIC,
  high   NUMERIC,
  low    NUMERIC,
  close  NUMERIC,
  volume BIGINT,
  source TEXT DEFAULT 'alphavantage',
  ingested_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (symbol, date)
);
