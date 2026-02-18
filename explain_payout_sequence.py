import pandas as pd
from analyze_edge import load_data, run_backtest

def explain_payout_sequence():
    filepath = 'glbx-mdp3-20250121-20260120.ohlcv-1m.csv'
    df = load_data(filepath)

    # Aggressive Payout Hunter Params
    orb = 15
    sl = 100
    tp = 100
    size = 0.4 # 4 Micros
    target = 3000

    print(f"Running Analysis: Size={size}, Target=${target}, SL/TP={sl}/{tp}")

    engine = run_backtest(df, orb_minutes=orb, sl_pts=sl, tp_pts=tp, contract_size=size, payout_target=target)

    trades_df = pd.DataFrame(engine.trades)
    if 'exit_time' in trades_df.columns:
        trades_df['exit_time'] = pd.to_datetime(trades_df['exit_time'])
        trades_df = trades_df.sort_values('exit_time')

    payout_count = 0
    balance_before_reset = 50000

    output = []
    output.append("=== PAYOUT HUNTER TIMELINE ===")
    output.append(f"Starting Balance: $50,000.00")
    output.append(f"Payout Target: +$3,000.00 (Withdraw & Reset)")
    output.append("-" * 40)

    for _, trade in trades_df.iterrows():
        pnl = trade['pnl']
        reason = trade['reason']
        date = trade['exit_time']

        balance_before_reset += pnl

        line = f"[{date}] Trade PnL: ${pnl:,.2f} ({reason}) | Balance: ${balance_before_reset:,.2f}"
        output.append(line)

        if reason == "PAYOUT HIT":
            payout_count += 1
            output.append(f"\n💰 PAYOUT #{payout_count} TRIGGERED!")
            output.append(f"   -> Withdrawing $3,000 Profit.")
            output.append(f"   -> Account Reset to $50,000.")
            output.append("-" * 40)
            balance_before_reset = 50000 # Reset tracker

        elif reason == "Max Drawdown Hit":
            output.append("\n🔥 BURN: Max Drawdown Limit Reached (-$2,500).")
            output.append("   -> Account Failed. Game Over.")
            output.append("-" * 40)
            break

    output.append(f"\n=== SUMMARY ===")
    output.append(f"Total Payouts Collected: ${payout_count * 3000:,.2f} ({payout_count} cycles)")
    if engine.failed:
        output.append("Final Status: BURNED (Account Lost)")
    else:
        output.append("Final Status: ACTIVE")

    with open("PAYOUT_TIMELINE.txt", "w") as f:
        f.write("\n".join(output))

    print("Timeline generated in PAYOUT_TIMELINE.txt")

if __name__ == "__main__":
    explain_payout_sequence()
