# Prop Firm NQ Strategy Guide (Full Year Data)

This guide details the optimized trading strategy found using the **full year** of continuous NQ futures data (Jan 2025 - Jan 2026). It is designed to pass Prop Firm evaluations by maximizing profit while strictly adhering to drawdown and daily loss rules.

## Strategy Overview

**Name:** 15-Minute Opening Range Breakout (ORB)
**Market:** NQ (Nasdaq 100 E-mini Futures) - Continuous Contract (Front Month)
**Timeframe:** 1-minute
**Trading Hours:** 09:30 ET - 15:55 ET (US Equity Session)

## Setup & Risk Management

*   **Account Size:** $50,000 (Standard Prop Firm Evaluation)
*   **Contract Size:** **1 Micro NQ Contract (MNQ) or 0.1 Mini NQ.**
    *   *Note:* Backtesting showed that 2 Micros was too aggressive for the drawdown limit over a full year. 1 Micro is safer.
*   **Max Daily Loss:** $1,000
*   **Max Trailing Drawdown:** $2,500
*   **Stop Loss (SL):** 100 points per contract ($200 total risk for 1 MNQ).
*   **Take Profit (TP):** 100 points per contract ($200 total reward for 1 MNQ).
*   **Risk per Trade:** $200 (0.4% of account).

## Trading Rules

1.  **Wait for the Open:** Do not trade before 09:30 ET.
2.  **Identify the Range:**
    *   Observe the price action from **09:30 ET to 09:45 ET**.
    *   Mark the **High** and **Low** of this 15-minute period.
3.  **Place Entry Orders:**
    *   **Long Entry:** Place a Buy Stop order at `High + 0.25 points`.
    *   **Short Entry:** Place a Sell Stop order at `Low - 0.25 points`.
    *   *Note:* Cancel the opposite order once one is filled (One-Cancels-Other / OCO).
4.  **Manage the Trade:**
    *   Once filled, immediately place your **Stop Loss** 100 points away.
    *   Immediately place your **Take Profit** 100 points away.
    *   Do **not** move your Stop Loss to breakeven.
5.  **End of Day Exit:**
    *   If a trade is still open at **15:55 ET**, close it immediately at market price.
    *   Do not hold positions overnight.

## Performance Statistics (Jan 2025 - Jan 2026)

*   **Net Profit:** $4,207.50
*   **Total Trades:** 258 (~1 per trading day)
*   **Win Rate:** 54.65%
*   **Profit Factor:** 1.20
*   **Max Drawdown:** $2,179 (Close to the $2,500 limit, but passing)
*   **Return on Max Drawdown:** 1.93
*   **Max Consecutive Wins:** 9
*   **Max Consecutive Losses:** 8

## Why This Works for Prop Firms

*   **Passing the Test:** While the profit factor is lower over the full year (1.20) compared to the partial sample, it is *positive* and stays within the strict drawdown rules.
*   **Survivability:** Reducing the size to 1 Micro ensures that a streak of 8 losses (which happened in the backtest) only draws down $1600, keeping the account alive.
*   **Consistency:** Daily activity keeps you engaged without overtrading.
