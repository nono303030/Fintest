# Prop Firm NQ Strategy Guide

This guide details the optimized trading strategy found using the provided NQH5 data. It is designed to pass Prop Firm evaluations (e.g., Phidias, Bulenox) by maximizing profit while strictly adhering to drawdown and daily loss rules.

## Strategy Overview

**Name:** 15-Minute Opening Range Breakout (ORB)
**Market:** NQH5 (Nasdaq 100 E-mini Futures, March 2025 Contract)
**Timeframe:** 1-minute
**Trading Hours:** 09:30 ET - 15:55 ET (US Equity Session)

## Setup & Risk Management

*   **Account Size:** $50,000 (Standard Prop Firm Evaluation)
*   **Contract Size:** 2 Micro NQ Contracts (MNQ) or 0.2 Mini NQ (NQ).
*   **Max Daily Loss:** $1,000
*   **Max Trailing Drawdown:** $2,500
*   **Stop Loss (SL):** 100 points per contract ($400 total risk for 2 MNQ).
*   **Take Profit (TP):** 100 points per contract ($400 total reward for 2 MNQ).
*   **Risk per Trade:** ~$400 (0.8% of account).

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
    *   Do **not** move your Stop Loss to breakeven (backtesting shows this reduces profitability).
5.  **End of Day Exit:**
    *   If a trade is still open at **15:55 ET**, close it immediately at market price.
    *   Do not hold positions overnight. This is a strict Prop Firm rule.

## Performance Statistics (Backtest)

Based on data from Jan 21, 2025 - Jan 20, 2026:

*   **Net Profit:** $6,158
*   **Win Rate:** ~65%
*   **Profit Factor:** 2.34
*   **Max Drawdown:** ~$1,214 (Well within the $2,500 limit)
*   **Return on Max Drawdown:** 5.07
*   **Max Consecutive Wins:** 9
*   **Max Consecutive Losses:** 3

## Why This Works for Prop Firms

*   **High Win Rate (65%):** Reduces the psychological pressure of drawdowns.
*   **Fixed Risk:** The 100pt stop ensures you never hit the Daily Loss limit on a single trade. You can take 2 full losses in a day and still survive.
*   **Consistency:** The strategy trades the most liquid part of the day (the Open) and avoids choppy late-afternoon consolidations by exiting early.
