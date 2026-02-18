import pandas as pd
from analyze_edge import load_data, run_backtest, BacktestEngine

def verify_trades():
    filepath = 'glbx-mdp3-20250121-20260120.ohlcv-1m.csv'

    # Load data
    try:
        df = load_data(filepath)
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        return

    # Use best params
    orb = 15
    sl = 100
    tp = 100
    contract_size = 0.2

    print(f"Running Backtest Verification: ORB={orb}m, SL={sl}, TP={tp}, Size={contract_size}")

    engine = run_backtest(df, orb_minutes=orb, sl_pts=sl, tp_pts=tp, max_daily_loss=1000, max_dd=2500)

    if len(engine.trades) == 0:
        print("No trades executed.")
        return

    trades_df = pd.DataFrame(engine.trades)

    # Add Entry Date column (US/Eastern)
    # The timestamps are already datetime objects from the engine, but might be just localized or naive
    # Let's inspect first to be safe, but usually just converting is fine if they are tz-aware
    if not pd.api.types.is_datetime64_any_dtype(trades_df['entry_time']):
        trades_df['entry_time'] = pd.to_datetime(trades_df['entry_time'])

    trades_df['entry_date'] = trades_df['entry_time'].dt.tz_convert('US/Eastern').dt.date

    # Group by Date
    daily_counts = trades_df.groupby('entry_date').size()

    print("\n=== TRADE FREQUENCY ANALYSIS ===")
    print(f"Total Trading Days with Activity: {len(daily_counts)}")
    print(f"Total Trades: {len(trades_df)}")

    multi_trade_days = daily_counts[daily_counts > 1]

    if len(multi_trade_days) > 0:
        print(f"\nWARNING: Found {len(multi_trade_days)} days with > 1 trade!")
        print(multi_trade_days)
    else:
        print("\nPASS: All days have exactly 1 trade (or 0).")

    # Check Overnight Holds
    trades_df['exit_time'] = pd.to_datetime(trades_df['exit_time'])
    trades_df['exit_date'] = trades_df['exit_time'].dt.tz_convert('US/Eastern').dt.date

    overnight_trades = trades_df[trades_df['entry_date'] != trades_df['exit_date']]

    if len(overnight_trades) > 0:
         print(f"\nWARNING: Found {len(overnight_trades)} trades held overnight!")
         print(overnight_trades)
    else:
         print("\nPASS: No overnight trades found.")

if __name__ == "__main__":
    verify_trades()
