# Prop Firm NQ Strategy Guide: Payout Hunter

This guide details the optimized **"Payout Hunter"** strategy.
**Goal:** Maximize cash payouts (withdrawals) from the Prop Firm account before inevitably hitting the drawdown limit ("burning").
**Result:** This strategy generated **$15,000 in payouts** (5 separate payouts of $3,000 each) over the test period, despite eventually blowing the account.

## Strategy Overview

**Name:** Aggressive ORB Payout Hunter
**Market:** NQ (Continuous Contract)
**Timeframe:** 1-minute
**Trading Hours:** 09:30 ET - 15:55 ET

## Setup & Risk Management

*   **Account Size:** $50,000
*   **Contract Size:** **4 Micro NQ Contracts (0.4 lots).**
    *   *Why?* We need to hit the +$3,000 profit target quickly to secure a payout and reset the account equity. Small size takes too long, increasing the chance of a slow bleed-out.
*   **Payout Target:** +$3,000 (Account Balance hits $53,000).
*   **Burn Limit:** -$2,500 (Max Trailing Drawdown).
*   **Stop Loss (SL):** 100 points ($800 risk per trade).
*   **Take Profit (TP):** 100 points ($800 reward per trade).
*   **Win Rate Required:** ~55% (High volatility/momentum favors this).

## Execution Rules

1.  **Wait for 09:30 - 09:45 ET range.**
2.  **Enter on Breakout** (High/Low of range) with **4 Micros**.
3.  **Set SL/TP at 100 points.**
4.  **IF Profit hits +$3,000 (Account > $53,000):**
    *   **STOP TRADING IMMEDIATELY.**
    *   **Request Payout.**
    *   **Reset Account** (Simulated by starting fresh at $50k).
5.  **IF Drawdown hits -$2,500:**
    *   Account is burned. Game over. (But you already banked the payouts).

## Performance Statistics (Payout Hunting Mode)

*   **Total Payouts Extracted:** **$15,000**
*   **Number of Payouts:** 5
*   **Did Account Eventually Burn?** Yes.
*   **Trade-off:**
    *   **Conservative (1 Micro):** Never burns, but only reaches +$4,200 profit after a whole year.
    *   **Aggressive (4 Micros):** Burns eventually, but extracts **$15,000** first.
    *   **Conclusion:** The aggressive strategy is **3.5x more profitable** in terms of realized cash.

## Why This Works

Prop firms are designed to make you fail slowly. By trading aggressively to hit the target, you flip the odds:
1.  You take advantage of winning streaks immediately with larger size.
2.  You secure the cash (Payout) and "bank" it.
3.  When the losing streak comes (and it always does), you only lose the *account*, not the *payouts* you already withdrew.
