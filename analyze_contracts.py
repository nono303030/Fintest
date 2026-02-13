import pandas as pd

def analyze_contracts():
    filepath = 'glbx-mdp3-20250121-20260120.ohlcv-1m.csv'

    # Load raw dataframe
    print("Loading file...")
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"File {filepath} not found.")
        return

    df['ts_event'] = pd.to_datetime(df['ts_event'])

    # Filter for standard contracts (exclude spreads which have a '-')
    df = df[~df['symbol'].str.contains('-')]

    # Group by Symbol
    symbols = df['symbol'].unique()
    print(f"\nUnique Symbols Found: {symbols}")

    print("\nSymbol Stats:")
    for symbol in symbols:
        sub_df = df[df['symbol'] == symbol]
        start = sub_df['ts_event'].min()
        end = sub_df['ts_event'].max()
        count = len(sub_df)
        print(f"{symbol}: {start} -> {end} | Count: {count}")

    # Check overlaps - pick a date range where multiple symbols are active
    print("\nOverlap Check (Highest Volume):")
    # For NQH5 and NQM5 around mid-March 2025
    overlap_mask = (df['ts_event'] > '2025-03-10') & (df['ts_event'] < '2025-03-25')
    overlap_df = df[overlap_mask]

    if len(overlap_df) > 0:
        daily_vol = overlap_df.groupby(['ts_event', 'symbol'])['volume'].sum().reset_index()
        daily_vol['date'] = daily_vol['ts_event'].dt.date
        daily_vol_agg = daily_vol.groupby(['date', 'symbol'])['volume'].sum().unstack()
        print(daily_vol_agg.head(10))
    else:
        print("No overlap found in mid-March 2025.")

if __name__ == "__main__":
    analyze_contracts()
