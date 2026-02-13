import pandas as pd
from analyze_edge import load_data, run_backtest, BacktestEngine

def detailed_report():
    filepath = 'glbx-mdp3-20250121-20260120.ohlcv-1m.csv'

    # Load data
    try:
        df = load_data(filepath)
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        return

    # Best Params hardcoded based on optimization (Payout Hunting)
    orb = 15
    sl = 100
    tp = 100
    # Aggressive sizing to hit payout target
    contract_size = 0.4 # 4 Micros
    payout_target = 3000

    print(f"Running Detailed Payout Hunting Report: ORB={orb}m, SL={sl}, TP={tp}, Size={contract_size}, Target=${payout_target}")

    # Re-run backtest to get trade details
    engine = run_backtest(df, orb_minutes=orb, sl_pts=sl, tp_pts=tp, max_daily_loss=1000, max_dd=2500, contract_size=contract_size, payout_target=payout_target)

    if len(engine.trades) == 0:
        print("No trades executed.")
        return

    trades_df = pd.DataFrame(engine.trades)

    # Calculate Metrics
    total_trades = len(trades_df)
    net_profit = trades_df['pnl'].sum()
    gross_profit = trades_df[trades_df['pnl'] > 0]['pnl'].sum()
    gross_loss = abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum())

    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    avg_trade = net_profit / total_trades
    win_rate = len(trades_df[trades_df['pnl'] > 0]) / total_trades

    max_dd = engine.max_dd_reached
    return_on_dd = net_profit / max_dd if max_dd > 0 else float('inf')

    # Consecutive Wins/Losses Logic
    max_consecutive_wins = 0
    max_consecutive_losses = 0
    current_win_streak = 0
    current_loss_streak = 0

    for pnl in trades_df['pnl']:
        if pnl > 0:
            current_win_streak += 1
            current_loss_streak = 0
            max_consecutive_wins = max(max_consecutive_wins, current_win_streak)
        elif pnl < 0:
            current_loss_streak += 1
            current_win_streak = 0
            max_consecutive_losses = max(max_consecutive_losses, current_loss_streak)

    print("\n=== PAYOUT HUNTING REPORT ===")
    print(f"Total Payouts:    ${engine.total_payout_amount:,.2f}")
    print(f"Payout Count:     {engine.payouts_count}")
    print(f"Net Profit (Sim): ${net_profit:,.2f}")
    print(f"Total Trades:     {total_trades}")
    print(f"Win Rate:         {win_rate:.2%}")
    print(f"Profit Factor:    {profit_factor:.2f}")
    print(f"Max Drawdown:     ${max_dd:,.2f}")
    print(f"Account Burned:   {engine.failed}")

    if len(engine.payout_history) > 0:
        print("\n--- Payout Timeline ---")
        for ts in engine.payout_history:
            print(f"Payout Triggered: {ts}")

    print("\n--- Trade History (Last 5) ---")
    if 'exit_time' in trades_df.columns:
        trades_df['exit_time'] = pd.to_datetime(trades_df['exit_time'])
        print(trades_df[['exit_time', 'exit_price', 'pnl', 'reason']].tail())

if __name__ == "__main__":
    detailed_report()
