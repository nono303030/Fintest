# Quick Strategy Reference: Payout Hunter

**Market:** NQ (Nasdaq 100 E-mini)
**Timeframe:** 1-minute
**Contract Size:** **4 Micro NQ (0.4 lots)**

## Trading Hours
*   **09:30 ET:** Market Open.
*   **09:30 - 09:45 ET:** Wait (Do not trade).
*   **15:55 ET:** Hard Close (Exit all positions).

## Entry Rules
1.  Identify the **High** and **Low** of the first 15 minutes (09:30-09:45 range).
2.  Place **Buy Stop** at `High + 0.25 points`.
3.  Place **Sell Stop** at `Low - 0.25 points`.
4.  If one fills, cancel the other (OCO).
5.  **Limit:** Max 1 trade per day.

## Risk Management
*   **Stop Loss (SL):** 100 points ($800 risk).
*   **Take Profit (TP):** 100 points ($800 reward).
*   **Breakeven:** NEVER move SL to breakeven.

## Account Management (Critical)
*   **Payout Goal:** When account profit hits **+$3,000**, STOP TRADING. Request Payout. Reset Account.
*   **Burn Limit:** If drawdown hits **-$2,500**, STOP TRADING. Account is burned. Reset.

## Stats (1 Year Sim)
*   **Payout Success Rate:** ~44% per attempt.
*   **Net Profit:** ~$31,750 (after multiple burns/resets).
