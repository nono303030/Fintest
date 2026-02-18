import pandas as pd
from analyze_edge import load_data, run_backtest, BacktestEngine

def cycle_report():
    filepath = 'glbx-mdp3-20250121-20260120.ohlcv-1m.csv'

    # Load data
    try:
        df = load_data(filepath)
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        return

    # Payout Hunter Params
    orb = 15
    sl = 100
    tp = 100
    size = 0.4 # 4 Micros
    target = 3000

    print(f"Running Cycle Analysis: Size={size}, Target=${target}, SL/TP={sl}/{tp}")

    engine = run_backtest(df, orb_minutes=orb, sl_pts=sl, tp_pts=tp, max_daily_loss=1000, max_dd=2500, contract_size=size, payout_target=target)

    total_cycles = engine.payouts_count + engine.burns_count
    payout_rate = (engine.payouts_count / total_cycles) * 100 if total_cycles > 0 else 0
    burn_rate = (engine.burns_count / total_cycles) * 100 if total_cycles > 0 else 0

    print("\n=== PROP FIRM CYCLE ANALYSIS (1 Year) ===")
    print(f"Total Cycles Attempted: {total_cycles}")
    print(f"Payouts Won:            {engine.payouts_count}  ({payout_rate:.1f}%)")
    print(f"Accounts Burned:        {engine.burns_count}  ({burn_rate:.1f}%)")
    print("-" * 40)
    print(f"Total Payout Value:     ${engine.total_payout_amount:,.2f}")

    # Cost Analysis (Assuming Eval Cost ~$50)
    eval_cost = 50
    total_cost = total_cycles * eval_cost
    net_profit_after_costs = engine.total_payout_amount - total_cost

    print(f"Estimated Eval Costs:   ${total_cost:,.2f} (@ ${eval_cost}/eval)")
    print(f"Net Profit (Simulated): ${net_profit_after_costs:,.2f}")
    print(f"Risk/Reward Ratio:      1 : {(net_profit_after_costs/total_cost):.2f}")

    print("\n--- Event Log ---")
    events = []
    for ts in engine.payout_history:
        events.append({'time': ts, 'type': 'PAYOUT', 'value': target})
    for ts in engine.burn_history:
        events.append({'time': ts, 'type': 'BURN', 'value': -2500}) # approximate cost of failure is mostly opportunity cost + fee

    events_df = pd.DataFrame(events)
    if not events_df.empty:
        events_df = events_df.sort_values('time')
        print(events_df.to_string(index=False))

if __name__ == "__main__":
    cycle_report()
