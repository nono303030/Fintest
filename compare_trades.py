import pandas as pd
import sys
import argparse

def compare_trades(file1, file2):
    print(f"Comparing {file1} vs {file2}")

    try:
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Normalize Date column
    df1['Date'] = pd.to_datetime(df1['Date']).dt.date
    df2['Date'] = pd.to_datetime(df2['Date']).dt.date

    # Sort by Date
    df1 = df1.sort_values('Date')
    df2 = df2.sort_values('Date')

    # Identify common dates
    dates1 = set(df1['Date'])
    dates2 = set(df2['Date'])

    common_dates = dates1.intersection(dates2)
    only_in_1 = dates1 - dates2
    only_in_2 = dates2 - dates1

    print(f"\n--- Comparison Summary ---")
    print(f"Trades in File 1: {len(df1)}")
    print(f"Trades in File 2: {len(df2)}")
    print(f"Common Dates: {len(common_dates)}")

    if only_in_1:
        print(f"Dates present only in {file1}: {len(only_in_1)}")
        print(sorted(list(only_in_1))[:5], "..." if len(only_in_1) > 5 else "")

    if only_in_2:
        print(f"Dates present only in {file2}: {len(only_in_2)}")
        print(sorted(list(only_in_2))[:5], "..." if len(only_in_2) > 5 else "")

    print("\n--- PnL Comparison (Common Dates) ---")

    # Merge on Date to compare daily PnL or specific trades
    # Assuming one trade per day as per strategy
    merged = pd.merge(df1, df2, on='Date', suffixes=('_1', '_2'), how='inner')

    matches = 0
    mismatches = 0

    print(f"{'Date':<12} {'PnL_1':<10} {'PnL_2':<10} {'Diff':<10}")
    print("-" * 45)

    for _, row in merged.iterrows():
        pnl1 = float(row['PnL_1'])
        pnl2 = float(row['PnL_2'])

        diff = abs(pnl1 - pnl2)

        if diff < 1.0: # Allow small floating point difference
            matches += 1
        else:
            mismatches += 1
            print(f"{row['Date']} {pnl1:<10.2f} {pnl2:<10.2f} {diff:<10.2f}")

    print("-" * 45)
    print(f"Matching PnL: {matches}")
    print(f"Mismatched PnL: {mismatches}")

    if mismatches == 0 and len(only_in_1) == 0 and len(only_in_2) == 0:
        print("\nSUCCESS: Files are identical (based on PnL per date).")
    else:
        print("\nWARNING: Discrepancies found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare two trade reports.")
    parser.add_argument("file1", help="First CSV file (e.g., my_trades.csv)")
    parser.add_argument("file2", help="Second CSV file (e.g., user_trades.csv)")

    args = parser.parse_args()

    compare_trades(args.file1, args.file2)
