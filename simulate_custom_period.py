import pandas as pd
from analyze_edge import load_data, run_backtest, BacktestEngine

def simulate_custom():
    filepath = 'glbx-mdp3-20250121-20260120.ohlcv-1m.csv'

    # Load data
    print("Loading data...")
    try:
        df = load_data(filepath)
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        return

    # Filter for last 140 days ending Jan 20, 2026
    # Data ends 2026-01-20.
    end_date = pd.Timestamp("2026-01-20").tz_localize("UTC")
    start_date = end_date - pd.Timedelta(days=140)

    print(f"Filtering data from {start_date.date()} to {end_date.date()} (140 Days)")

    mask = (df.index >= start_date) & (df.index <= end_date + pd.Timedelta(days=1)) # Include full end day
    df_subset = df[mask].copy()

    if len(df_subset) == 0:
        print("No data found in range.")
        return

    # Params from User Request
    # 50 ticks TP = 12.5 points (NQ tick is 0.25)
    # 400 ticks SL = 100 points
    sl_pts = 100
    tp_pts = 12.5
    orb_minutes = 15
    size = 0.4 # Payout Hunter Size
    target = 3000

    print(f"Running Simulation: SL={sl_pts}pts (400t), TP={tp_pts}pts (50t), ORB={orb_minutes}m, Size={size}")

    engine = run_backtest(df_subset, orb_minutes=orb_minutes, sl_pts=sl_pts, tp_pts=tp_pts,
                          max_daily_loss=1000, max_dd=2500, contract_size=size, payout_target=target)

    # Cycle Stats
    total_cycles = engine.payouts_count + engine.burns_count
    payout_rate = (engine.payouts_count / total_cycles) * 100 if total_cycles > 0 else 0
    burn_rate = (engine.burns_count / total_cycles) * 100 if total_cycles > 0 else 0

    print("\n=== CUSTOM SIMULATION RESULTS (Last 140 Days) ===")
    print(f"Total Cycles:     {total_cycles}")
    print(f"Payouts Won:      {engine.payouts_count}  ({payout_rate:.1f}%)")
    print(f"Accounts Burned:  {engine.burns_count}  ({burn_rate:.1f}%)")
    print(f"Total Payout Amt: ${engine.total_payout_amount:,.2f}")

    if len(engine.trades) > 0:
        wins = len([t for t in engine.trades if t['pnl'] > 0])
        win_rate = (wins / len(engine.trades)) * 100
        print(f"\nTrade Win Rate:   {win_rate:.1f}%")
        print(f"Total Trades:     {len(engine.trades)}")

    print("\n--- Cycle Log ---")
    events = []
    for ts in engine.payout_history:
        events.append({'time': ts, 'type': 'PAYOUT', 'value': target})
    for ts in engine.burn_history:
        events.append({'time': ts, 'type': 'BURN', 'value': -2500})

    events_df = pd.DataFrame(events)
    if not events_df.empty:
        events_df = events_df.sort_values('time')
        print(events_df.to_string(index=False))

if __name__ == "__main__":
    simulate_custom()
