import pandas as pd
import numpy as np
import itertools

def load_data(filepath):
    # Load the CSV file
    df = pd.read_csv(filepath)

    # Filter for NQH5
    df = df[df['symbol'] == 'NQH5'].copy()

    # Convert ts_event to datetime
    df['ts_event'] = pd.to_datetime(df['ts_event'])

    # Set index
    df.set_index('ts_event', inplace=True)

    # Sort just in case
    df.sort_index(inplace=True)

    return df

class BacktestEngine:
    def __init__(self, initial_balance=50000, max_daily_loss=1000, max_trailing_drawdown=2500, contract_multiplier=0.1):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.equity = initial_balance
        self.high_water_mark = initial_balance

        self.max_daily_loss = max_daily_loss
        self.max_trailing_drawdown = max_trailing_drawdown
        self.contract_multiplier = contract_multiplier # 0.1 = MNQ (Micro NQ)

        self.position = 0  # 0: Flat, 1: Long, -1: Short
        self.entry_price = 0
        self.stop_loss = 0
        self.take_profit = 0

        self.current_day = None
        self.start_of_day_equity = initial_balance

        self.trades = []
        self.failed = False
        self.daily_loss_hit = False

        self.max_dd_reached = 0

    def new_day(self, timestamp):
        current_date = timestamp.date()
        if self.current_day != current_date:
            self.current_day = current_date
            self.start_of_day_equity = self.balance
            self.daily_loss_hit = False

    def update(self, timestamp, current_price):
        if self.failed:
            return

        # Update equity
        unrealized_pnl = 0
        if self.position != 0:
            unrealized_pnl = (current_price - self.entry_price) * self.position * 20 * self.contract_multiplier

        self.equity = self.balance + unrealized_pnl

        # Check Trailing Drawdown
        if self.equity > self.high_water_mark:
            self.high_water_mark = self.equity

        drawdown = self.high_water_mark - self.equity
        self.max_dd_reached = max(self.max_dd_reached, drawdown)

        if drawdown >= self.max_trailing_drawdown:
            self.failed = True
            self.close_position(timestamp, current_price, "Max Drawdown Hit")

        # Check Daily Loss
        daily_pnl = self.equity - self.start_of_day_equity
        if daily_pnl <= -self.max_daily_loss:
            self.daily_loss_hit = True
            if self.position != 0:
                self.close_position(timestamp, current_price, "Daily Loss Limit Hit")

    def check_sl_tp(self, timestamp, high, low):
        if self.position == 0:
            return

        # Long
        if self.position == 1:
            if low <= self.stop_loss:
                self.close_position(timestamp, self.stop_loss, "SL")
            elif high >= self.take_profit:
                self.close_position(timestamp, self.take_profit, "TP")

        # Short
        elif self.position == -1:
            if high >= self.stop_loss:
                self.close_position(timestamp, self.stop_loss, "SL")
            elif low <= self.take_profit:
                self.close_position(timestamp, self.take_profit, "TP")

    def close_position(self, timestamp, price, reason):
        if self.position == 0:
            return

        pnl = (price - self.entry_price) * self.position * 20 * self.contract_multiplier
        self.balance += pnl

        self.trades.append({
            'exit_time': timestamp,
            'exit_price': price,
            'pnl': pnl,
            'reason': reason,
            'balance': self.balance,
            'equity': self.equity
        })

        self.position = 0

    def enter_position(self, timestamp, side, price, sl, tp):
        if self.failed or self.daily_loss_hit or self.position != 0:
            return

        self.position = 1 if side == 'long' else -1
        self.entry_price = price
        self.stop_loss = sl
        self.take_profit = tp

def run_backtest(df, orb_minutes=15, sl_pts=20, tp_pts=40, max_daily_loss=1000, max_dd=2500):
    # Use 2 Micro contracts (0.2) or 5 Micros (0.5) or 1 Micro (0.1)?
    # Let's try 2 Micros (0.2 lots of NQ) to have meaningful PnL but safe risk.
    # Risk management: 50 pt stop on 2 micros = 50 * 20 * 0.2 = $200 risk per trade.
    # Daily loss $1000 = 5 trades allowed. Good.
    engine = BacktestEngine(max_daily_loss=max_daily_loss, max_trailing_drawdown=max_dd, contract_multiplier=0.2)

    current_date = None
    session_start_time = None
    session_end_time = None
    orb_high = -1
    orb_low = 999999
    orb_complete = False
    entry_taken = False

    # Pre-calculate UTC times for 09:30 ET and 16:00 ET (Assuming Standard Time for Jan: UTC-5)
    open_hour = 14
    open_minute = 30
    close_hour = 20
    close_minute = 55

    for timestamp, row in df.iterrows():
        # Check for new day
        day = timestamp.date()
        if day != current_date:
            current_date = day
            engine.new_day(timestamp)
            orb_high = -1
            orb_low = 999999
            orb_complete = False
            entry_taken = False

            session_start_time = timestamp.replace(hour=open_hour, minute=open_minute, second=0)
            session_end_time = timestamp.replace(hour=close_hour, minute=close_minute, second=0)

        # Check if we are in session
        if timestamp < session_start_time:
            continue

        if timestamp > session_end_time:
            if engine.position != 0:
                engine.close_position(timestamp, row['close'], "EOD")
            continue

        # Update Engine
        engine.update(timestamp, row['close'])
        if engine.failed:
            break

        if engine.daily_loss_hit:
            if engine.position != 0:
                engine.close_position(timestamp, row['close'], "Daily Loss Hit")
            continue

        # Check SL/TP (prior to entry logic)
        if engine.position != 0:
            engine.check_sl_tp(timestamp, row['high'], row['low'])

        # ORB Logic
        orb_end_time = session_start_time + pd.Timedelta(minutes=orb_minutes)

        if timestamp <= orb_end_time:
            orb_high = max(orb_high, row['high'])
            orb_low = min(orb_low, row['low'])
            if timestamp == orb_end_time:
                orb_complete = True

        # Check for Entry
        if orb_complete and not entry_taken and engine.position == 0 and not engine.daily_loss_hit:
            # Long Breakout
            if row['high'] > orb_high:
                entry_price = orb_high + 0.25
                sl = entry_price - sl_pts
                tp = entry_price + tp_pts
                engine.enter_position(timestamp, 'long', entry_price, sl, tp)
                entry_taken = True

                # Immediate check for SL/TP on the entry bar itself!
                # Assuming fill at High + 0.25. Low of this bar could trigger SL.
                # High of this bar is > entry_price, could trigger TP?
                # Let's assume conservatively: Check Low for SL first.
                if row['low'] <= sl:
                    engine.close_position(timestamp, sl, "SL (Same Bar)")
                elif row['high'] >= tp:
                     engine.close_position(timestamp, tp, "TP (Same Bar)")

            # Short Breakout
            elif row['low'] < orb_low:
                entry_price = orb_low - 0.25
                sl = entry_price + sl_pts
                tp = entry_price - tp_pts
                engine.enter_position(timestamp, 'short', entry_price, sl, tp)
                entry_taken = True

                # Immediate check
                if row['high'] >= sl:
                    engine.close_position(timestamp, sl, "SL (Same Bar)")
                elif row['low'] <= tp:
                    engine.close_position(timestamp, tp, "TP (Same Bar)")

    return engine

def optimize(df):
    orb_minutes_options = [5, 15, 30]
    sl_pts_options = [30, 50, 70, 100]
    tp_pts_options = [50, 100, 150, 200]

    best_score = -float('inf')
    best_params = {}
    best_result = {}

    combinations = list(itertools.product(orb_minutes_options, sl_pts_options, tp_pts_options))
    print(f"Testing {len(combinations)} combinations...")

    for orb, sl, tp in combinations:
        if tp < sl: # Skip low RR
            continue

        engine = run_backtest(df, orb_minutes=orb, sl_pts=sl, tp_pts=tp)

        total_pnl = engine.balance - engine.initial_balance
        max_dd = engine.max_dd_reached
        win_rate = 0
        if len(engine.trades) > 0:
            wins = len([t for t in engine.trades if t['pnl'] > 0])
            win_rate = wins / len(engine.trades)

        # Score Logic
        if engine.failed:
            score = -10000
        elif len(engine.trades) < 5:
            score = -100
        else:
            # Profit Factor * Win Rate? Or just Net Profit?
            # Prop Firm goal: Maximize Profit without failing.
            score = total_pnl

        if score > best_score:
            best_score = score
            best_params = {'orb': orb, 'sl': sl, 'tp': tp}
            best_result = {
                'pnl': total_pnl,
                'max_dd': max_dd,
                'win_rate': win_rate,
                'trades': len(engine.trades),
                'failed': engine.failed
            }

        # print(f"ORB={orb}, SL={sl}, TP={tp} -> PnL: {total_pnl:.2f}, Failed: {engine.failed}")

    return best_params, best_result

if __name__ == "__main__":
    filepath = 'glbx-mdp3-20250121-20260120.ohlcv-1m.csv'
    try:
        print("Loading data...")
        df = load_data(filepath)
        print("Starting optimization...")
        best_params, best_result = optimize(df)

        print("\n=== BEST STRATEGY FOUND ===")
        print(f"Parameters: {best_params}")
        print(f"Results: {best_result}")

        with open('strategy_results.txt', 'w') as f:
            f.write("=== BEST STRATEGY FOUND ===\n")
            f.write(f"Parameters: {best_params}\n")
            f.write(f"Results: {best_result}\n")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
