import pandas as pd
from analyze_edge import load_data, run_backtest

def analyze_losses():
    filepath = 'glbx-mdp3-20250121-20260120.ohlcv-1m.csv'

    print("Loading data...")
    try:
        df = load_data(filepath)
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        return

    # Payout Hunter Strategy Params
    orb = 15
    sl = 100
    tp = 100
    size = 0.4
    target = 3000

    print(f"Running Analysis for Losing Days: Size={size}, SL/TP={sl}/{tp}")

    engine = run_backtest(df, orb_minutes=orb, sl_pts=sl, tp_pts=tp, max_daily_loss=1000, max_dd=2500, contract_size=size, payout_target=target)

    if len(engine.trades) == 0:
        print("No trades found.")
        return

    trades_df = pd.DataFrame(engine.trades)

    # Filter for losses
    losses = trades_df[trades_df['pnl'] < 0].copy()

    if len(losses) == 0:
        print("No losses found! (Unlikely)")
        return

    # Format Date
    if 'exit_time' in losses.columns:
        # Check if datetime, if not convert
        if not pd.api.types.is_datetime64_any_dtype(losses['exit_time']):
             losses['exit_time'] = pd.to_datetime(losses['exit_time'])

        losses['Date'] = losses['exit_time'].dt.date
        losses['DayOfWeek'] = losses['exit_time'].dt.day_name()

    print(f"\n=== LIST OF LOSING TRADES ({len(losses)}) ===")
    print(losses[['Date', 'DayOfWeek', 'pnl', 'reason']].to_string(index=False))

    # Group by Day of Week
    print("\n=== LOSSES BY DAY OF WEEK ===")
    daily_stats = losses.groupby('DayOfWeek')['pnl'].agg(['count', 'sum']).sort_values('sum')
    print(daily_stats)

if __name__ == "__main__":
    analyze_losses()
