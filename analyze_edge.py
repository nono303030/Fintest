import pandas as pd
import numpy as np
import pytz
import sys
from datetime import datetime, time, timedelta

def load_and_stitch_data(filepath):
    print("Loading data...")
    # Load data
    df = pd.read_csv(filepath)

    # Parse timestamp
    df['ts_event'] = pd.to_datetime(df['ts_event'])

    # Convert to Eastern Time
    eastern = pytz.timezone('US/Eastern')
    df['ts_event'] = df['ts_event'].dt.tz_convert(eastern)

    # Extract date for grouping
    df['date'] = df['ts_event'].dt.date

    print("Calculating daily volume per symbol...")
    # Calculate daily volume per symbol
    daily_volume = df.groupby(['date', 'symbol'])['volume'].sum().reset_index()

    # Identify the symbol with the highest volume for each day
    # Sort by date and volume (descending), then drop duplicates keeping the first (highest volume)
    active_contracts = daily_volume.sort_values(['date', 'volume'], ascending=[True, False]).drop_duplicates('date')
    active_contracts = active_contracts[['date', 'symbol']].set_index('date')

    print("Stitching contracts...")
    # Filter original df to keep only the active contract for each day
    # We can merge or filter. Let's iterate or use a join.
    # A join is faster.

    # Create a mapping of date -> active_symbol
    active_symbol_map = active_contracts['symbol'].to_dict()

    # Apply filter: keep row if symbol matches the active symbol for that date
    # This might be slow if we apply row by row. Vectorized approach:
    # Map the date column to the active symbol
    df['active_symbol'] = df['date'].map(active_symbol_map)

    # Filter
    stitched_df = df[df['symbol'] == df['active_symbol']].copy()

    # Sort by timestamp
    stitched_df = stitched_df.sort_values('ts_event').reset_index(drop=True)

    print(f"Data loaded and stitched. {len(stitched_df)} rows.")
    return stitched_df

def run_backtest(df):
    print("Running backtest...")
    trades = []

    # Strategy Parameters
    ORB_START = time(9, 30)
    ORB_END = time(9, 45)
    EOD_EXIT = time(15, 55)
    STOP_LOSS_PTS = 100.0
    TAKE_PROFIT_PTS = 100.0
    CONTRACT_SIZE = 0.4 # 4 Micros
    POINT_VALUE = 20.0 # NQ point value

    # Group by date to process each day
    # But we need to iterate through days.

    grouped = df.groupby('date')

    for date, day_df in grouped:
        # Check if we have enough data for the day
        if day_df.empty:
            continue

        # 1. Define ORB range (09:30 - 09:45)
        # We need to be careful with strict inequality. Memory says "utilizing a strict < comparison to capture the 09:30-09:44 minute bars"
        # Wait, if data is 1-minute bars, 09:30 bar covers 09:30:00 to 09:30:59.
        # So 09:30 to 09:45 means bars at 09:30, 31, ..., 44. The bar at 09:45 starts at 09:45:00.
        # So we want bars where time >= 09:30 and time < 09:45.

        day_df = day_df.set_index('ts_event')

        # Filter for Regular Trading Hours (RTH) for analysis if needed, but for ORB specifically:
        orb_data = day_df.between_time(ORB_START, ORB_END, inclusive='left') # left inclusive means [start, end)

        if orb_data.empty:
            continue

        orb_high = orb_data['high'].max()
        orb_low = orb_data['low'].min()

        # 2. Look for breakout after 09:45
        # We process bars starting from 09:45
        trading_session = day_df.between_time(ORB_END, EOD_EXIT, inclusive='left') # 09:45 to 15:55

        if trading_session.empty:
            continue

        position = None # 'LONG' or 'SHORT'
        entry_price = 0.0
        entry_time = None

        for ts, row in trading_session.iterrows():
            current_high = row['high']
            current_low = row['low']
            current_open = row['open'] # Assume stop orders trigger immediately if price touches

            # Check for entry if no position
            if position is None:
                # Buy Stop at ORB High
                if current_high >= orb_high:
                    position = 'LONG'
                    entry_price = orb_high + 0.25 # Assume fill at break + 1 tick slippage/stop? Let's use exact level or strictly >.
                    # Usually stop orders fill at the price or worse. Let's assume fill at price for simplicity or slightly worse.
                    # Memory says "immediate pending stop orders".
                    # Let's assume fill at orb_high.
                    entry_price = orb_high
                    entry_time = ts

                    # Check if SL/TP hit in SAME bar?
                    # Long: SL at entry - 100, TP at entry + 100
                    sl_price = entry_price - STOP_LOSS_PTS
                    tp_price = entry_price + TAKE_PROFIT_PTS

                    # If Low <= SL, stopped out. If High >= TP, target hit.
                    # Which happened first? We don't know intra-bar.
                    # Pessimistic assumption: SL hit first if both hit.

                    if current_low <= sl_price:
                        # Loss
                        exit_price = sl_price
                        pnl = (exit_price - entry_price) * CONTRACT_SIZE * POINT_VALUE
                        trades.append({
                            'Date': date,
                            'Symbol': row['symbol'],
                            'Entry Time': entry_time,
                            'Entry Price': entry_price,
                            'Exit Time': ts,
                            'Exit Price': exit_price,
                            'PnL': pnl,
                            'Result': 'Loss'
                        })
                        position = 'FLAT' # Trade done for the day
                        break
                    elif current_high >= tp_price:
                        # Win
                        exit_price = tp_price
                        pnl = (exit_price - entry_price) * CONTRACT_SIZE * POINT_VALUE
                        trades.append({
                            'Date': date,
                            'Symbol': row['symbol'],
                            'Entry Time': entry_time,
                            'Entry Price': entry_price,
                            'Exit Time': ts,
                            'Exit Price': exit_price,
                            'PnL': pnl,
                            'Result': 'Win'
                        })
                        position = 'FLAT'
                        break
                    else:
                        # Position remains open
                        continue

                # Sell Stop at ORB Low
                elif current_low <= orb_low:
                    position = 'SHORT'
                    entry_price = orb_low
                    entry_time = ts

                    sl_price = entry_price + STOP_LOSS_PTS
                    tp_price = entry_price - TAKE_PROFIT_PTS

                    if current_high >= sl_price:
                        # Loss
                        exit_price = sl_price
                        pnl = (entry_price - exit_price) * CONTRACT_SIZE * POINT_VALUE
                        trades.append({
                            'Date': date,
                            'Symbol': row['symbol'],
                            'Entry Time': entry_time,
                            'Entry Price': entry_price,
                            'Exit Time': ts,
                            'Exit Price': exit_price,
                            'PnL': pnl,
                            'Result': 'Loss'
                        })
                        position = 'FLAT'
                        break
                    elif current_low <= tp_price:
                        # Win
                        exit_price = tp_price
                        pnl = (entry_price - exit_price) * CONTRACT_SIZE * POINT_VALUE
                        trades.append({
                            'Date': date,
                            'Symbol': row['symbol'],
                            'Entry Time': entry_time,
                            'Entry Price': entry_price,
                            'Exit Time': ts,
                            'Exit Price': exit_price,
                            'PnL': pnl,
                            'Result': 'Win'
                        })
                        position = 'FLAT'
                        break
                    else:
                        continue

            # Manage existing position
            else:
                if position == 'LONG':
                    sl_price = entry_price - STOP_LOSS_PTS
                    tp_price = entry_price + TAKE_PROFIT_PTS

                    if current_low <= sl_price:
                        # Loss
                        exit_price = sl_price
                        pnl = (exit_price - entry_price) * CONTRACT_SIZE * POINT_VALUE
                        trades.append({
                            'Date': date,
                            'Symbol': row['symbol'],
                            'Entry Time': entry_time,
                            'Entry Price': entry_price,
                            'Exit Time': ts,
                            'Exit Price': exit_price,
                            'PnL': pnl,
                            'Result': 'Loss'
                        })
                        position = 'FLAT'
                        break
                    elif current_high >= tp_price:
                        # Win
                        exit_price = tp_price
                        pnl = (exit_price - entry_price) * CONTRACT_SIZE * POINT_VALUE
                        trades.append({
                            'Date': date,
                            'Symbol': row['symbol'],
                            'Entry Time': entry_time,
                            'Entry Price': entry_price,
                            'Exit Time': ts,
                            'Exit Price': exit_price,
                            'PnL': pnl,
                            'Result': 'Win'
                        })
                        position = 'FLAT'
                        break

                elif position == 'SHORT':
                    sl_price = entry_price + STOP_LOSS_PTS
                    tp_price = entry_price - TAKE_PROFIT_PTS

                    if current_high >= sl_price:
                        # Loss
                        exit_price = sl_price
                        pnl = (entry_price - exit_price) * CONTRACT_SIZE * POINT_VALUE
                        trades.append({
                            'Date': date,
                            'Symbol': row['symbol'],
                            'Entry Time': entry_time,
                            'Entry Price': entry_price,
                            'Exit Time': ts,
                            'Exit Price': exit_price,
                            'PnL': pnl,
                            'Result': 'Loss'
                        })
                        position = 'FLAT'
                        break
                    elif current_low <= tp_price:
                        # Win
                        exit_price = tp_price
                        pnl = (entry_price - exit_price) * CONTRACT_SIZE * POINT_VALUE
                        trades.append({
                            'Date': date,
                            'Symbol': row['symbol'],
                            'Entry Time': entry_time,
                            'Entry Price': entry_price,
                            'Exit Time': ts,
                            'Exit Price': exit_price,
                            'PnL': pnl,
                            'Result': 'Win'
                        })
                        position = 'FLAT'
                        break

        # End of Day Exit
        if position in ['LONG', 'SHORT']:
            # Close at 15:55 (or the last bar available before that)
            # The loop runs up to EOD_EXIT (exclusive). So the last bar processed was 15:54.
            # If we are here, we are still open. We close at the OPEN of the next bar? Or the CLOSE of the last bar?
            # Memory says "EOD exits (15:55 ET)".
            # Let's assume we exit at the CLOSE of the 15:54 bar (which is 15:55:00 effectively) or the OPEN of 15:55 bar.
            # But we filtered `between_time(..., EOD_EXIT, inclusive='left')`, so 15:55 bar is NOT in the loop.
            # So we use the CLOSE of the last processed bar.

            last_bar = trading_session.iloc[-1]
            exit_time = last_bar.name
            exit_price = last_bar['close']

            if position == 'LONG':
                pnl = (exit_price - entry_price) * CONTRACT_SIZE * POINT_VALUE
            else:
                pnl = (entry_price - exit_price) * CONTRACT_SIZE * POINT_VALUE

            result = 'Win' if pnl > 0 else 'Loss'
            trades.append({
                'Date': date,
                'Symbol': last_bar['symbol'],
                'Entry Time': entry_time,
                'Entry Price': entry_price,
                'Exit Time': exit_time,
                'Exit Price': exit_price,
                'PnL': pnl,
                'Result': result
            })

    return pd.DataFrame(trades)

def main():
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = 'glbx-mdp3-20250121-20260120.ohlcv-1m.csv'

    print(f"Using input file: {filepath}")

    try:
        df = load_and_stitch_data(filepath)
        results = run_backtest(df)

        if not results.empty:
            results.to_csv('my_trades.csv', index=False)
            print("Trades saved to my_trades.csv")

            # Summary
            total_trades = len(results)
            wins = len(results[results['PnL'] > 0])
            losses = len(results[results['PnL'] <= 0])
            win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
            net_profit = results['PnL'].sum()
            avg_trade = results['PnL'].mean()

            gross_profit = results[results['PnL'] > 0]['PnL'].sum()
            gross_loss = abs(results[results['PnL'] < 0]['PnL'].sum())
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

            # Max Drawdown
            results['Cumulative PnL'] = results['PnL'].cumsum()
            results['High Water Mark'] = results['Cumulative PnL'].cummax()
            results['Drawdown'] = results['High Water Mark'] - results['Cumulative PnL']
            max_drawdown = results['Drawdown'].max()

            print("\n--- Performance Summary ---")
            print(f"Total Trades: {total_trades}")
            print(f"Net Profit: ${net_profit:.2f}")
            print(f"Win Rate: {win_rate:.2f}%")
            print(f"Profit Factor: {profit_factor:.2f}")
            print(f"Max Drawdown: ${max_drawdown:.2f}")
            print("---------------------------")

        else:
            print("No trades generated.")

    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
