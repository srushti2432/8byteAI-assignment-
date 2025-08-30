import os
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple

import requests
import psycopg2
from psycopg2.extras import execute_values

ALPHAVANTAGE_URL = "https://www.alphavantage.co/query"


def fetch_daily_time_series(symbol: str, api_key: str, output_size: str = "compact") -> Dict:
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": output_size,
        "datatype": "json",
    }
    try:
        resp = requests.get(ALPHAVANTAGE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # Handle Alpha Vantage throttling/errors
        if "Error Message" in data:
            raise RuntimeError(f"API error for {symbol}: {data['Error Message']}")
        if "Note" in data:
            raise RuntimeError(f"API rate limit/notice for {symbol}: {data['Note']}")
        if "Time Series (Daily)" not in data:
            raise RuntimeError(f"Unexpected response for {symbol}: {json.dumps(data)[:300]} ...")

        return data
    except requests.RequestException as e:
        raise RuntimeError(f"HTTP error for {symbol}: {e}")


def parse_time_series(symbol: str, payload: Dict) -> List[Tuple]:
    ts = payload.get("Time Series (Daily)", {})
    rows: List[Tuple] = []
    for day, metrics in ts.items():
        try:
            rows.append(
                (
                    symbol,
                    datetime.strptime(day, "%Y-%m-%d").date(),
                    float(metrics.get("1. open", "nan")),
                    float(metrics.get("2. high", "nan")),
                    float(metrics.get("3. low", "nan")),
                    float(metrics.get("4. close", "nan")),
                    int(metrics.get("5. volume", 0)),
                )
            )
        except Exception:
            # Skip malformed row but continue
            continue
    return rows


def upsert_rows(conn, rows: List[Tuple]) -> int:
    if not rows:
        return 0
    sql = """
        INSERT INTO stock_prices (symbol, date, open, high, low, close, volume)
        VALUES %s
        ON CONFLICT (symbol, date) DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume,
            ingested_at = NOW();
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, rows, page_size=1000)
    conn.commit()
    return len(rows)


def get_pg_connection():
    host = os.getenv("POSTGRES_HOST", "postgres")
    db = os.getenv("POSTGRES_DB", "stockdb")
    user = os.getenv("POSTGRES_USER", "postgres")
    pwd = os.getenv("POSTGRES_PASSWORD", "minds123")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    return psycopg2.connect(host=host, dbname=db, user=user, password=pwd, port=port)


def run(symbols_csv: str, api_key: str, output_size: str = "compact"):
    symbols = [s.strip() for s in symbols_csv.split(",") if s.strip()]
    if not symbols:
        raise ValueError("No symbols provided. Set STOCK_SYMBOLS env var.")

    ingested_total = 0
    for i, symbol in enumerate(symbols):
        # Respect free-tier rate limits (5 req/min). Sleep between symbols.
        if i > 0:
            time.sleep(13)

        data = fetch_daily_time_series(symbol, api_key, output_size)
        rows = parse_time_series(symbol, data)

        with get_pg_connection() as conn:
            upserted = upsert_rows(conn, rows)
            ingested_total += upserted
            print(f"[{symbol}] upserted {upserted} rows")

    print(f"Total upserted rows: {ingested_total}")


if __name__ == "__main__":
    run(
        symbols_csv=os.getenv("STOCK_SYMBOLS", "IBM"),
        api_key=os.getenv("ALPHAVANTAGE_API_KEY", "demo"),
        output_size=os.getenv("OUTPUT_SIZE", "compact"),
    )
