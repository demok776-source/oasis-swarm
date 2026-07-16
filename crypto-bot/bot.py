"""
OASIS Solana Trading Bot.

Was a pure simulation before: hardcoded `sentiment_score = 0.85` every loop,
fake tx signature string, no real market data. This version pulls REAL
price data from Jupiter's public quote API and drives a simple momentum
signal off it. Execution stays a DRY RUN by default -- flipping it to a
real swap requires an explicit env var AND a funded signing keypair, so
nobody accidentally fires a mainnet transaction by running this script.

Jupiter API note (as of the 2026 Jupiter Developer Platform migration):
the legacy free-tier grace period on the old portal ended 2026-06-30.
Set JUPITER_API_KEY (from https://portal.jup.ag) if you have one; the
public endpoint below still works unauthenticated but is rate-limited and
best-effort. See https://dev.jup.ag/api-reference/swap/quote

NOTE ON VERIFICATION: this file was written and syntax/unit-tested in a
sandboxed environment with no route to api.devnet.solana.com or
quote-api.jup.ag. The HTTP call shapes below match Jupiter's documented
v6 quote contract, but a live network round-trip has NOT been exercised
here -- test it against devnet before trusting it further.
"""
import asyncio
import logging
import os
from dataclasses import dataclass, field

import httpx
from solana.rpc.async_api import AsyncClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SolanaBot")

# --- config -------------------------------------------------------------
SOLANA_RPC_URL = os.environ.get("SOLANA_RPC_URL", "https://api.devnet.solana.com")
JUPITER_QUOTE_URL = os.environ.get("JUPITER_QUOTE_URL", "https://quote-api.jup.ag/v6/quote")
JUPITER_API_KEY = os.environ.get("JUPITER_API_KEY")  # optional; see docstring

SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# Real funds are never at risk unless BOTH the operator opts in via env var
# AND a signer/keypair is actually wired up (left as a deliberate TODO --
# see execute_swap() below). This is the load-bearing safety default.
DRY_RUN = os.environ.get("OASIS_BOT_DRY_RUN", "true").lower() != "false"

POLL_INTERVAL_S = float(os.environ.get("OASIS_BOT_POLL_INTERVAL_S", "15"))
QUOTE_AMOUNT_LAMPORTS = int(os.environ.get("OASIS_BOT_QUOTE_AMOUNT_LAMPORTS", "1000000000"))  # 1 SOL
MOMENTUM_BUY_THRESHOLD_PCT = float(os.environ.get("OASIS_BOT_MOMENTUM_BUY_PCT", "0.5"))  # % move
MAX_POSITION_SOL = float(os.environ.get("OASIS_BOT_MAX_POSITION_SOL", "1.0"))  # risk cap


@dataclass
class BotState:
    sol_balance: float = 10.5
    position_sol: float = 0.0
    last_price_usdc_per_sol: float | None = None
    price_history: list = field(default_factory=list)


async def fetch_sol_usdc_quote(client: httpx.AsyncClient) -> float | None:
    """Fetch a live SOL->USDC quote from Jupiter and return implied price
    (USDC per SOL). Returns None on any failure -- callers must treat that
    as "no signal this tick", never as a stand-in for a fake number."""
    params = {
        "inputMint": SOL_MINT,
        "outputMint": USDC_MINT,
        "amount": str(QUOTE_AMOUNT_LAMPORTS),
        "slippageBps": "50",
    }
    headers = {"x-api-key": JUPITER_API_KEY} if JUPITER_API_KEY else {}
    try:
        resp = await client.get(JUPITER_QUOTE_URL, params=params, headers=headers, timeout=8.0)
        resp.raise_for_status()
        data = resp.json()
        out_amount_usdc = int(data["outAmount"]) / 1_000_000  # USDC has 6 decimals
        in_amount_sol = QUOTE_AMOUNT_LAMPORTS / 1_000_000_000
        return out_amount_usdc / in_amount_sol
    except httpx.HTTPStatusError as e:
        logger.warning(f"Jupiter quote HTTP error: {e.response.status_code} {e.response.text[:200]}")
    except (httpx.HTTPError, KeyError, ValueError, ZeroDivisionError) as e:
        logger.warning(f"Jupiter quote fetch failed: {e}")
    return None


def compute_momentum_signal(state: BotState, price: float) -> float | None:
    """% price change vs the previous observed price. None until we have
    at least two data points. This replaces the old hardcoded
    `sentiment_score = 0.85` with an actual (if simplistic) market signal."""
    if state.last_price_usdc_per_sol is None:
        return None
    if state.last_price_usdc_per_sol == 0:
        return None
    pct_change = (price - state.last_price_usdc_per_sol) / state.last_price_usdc_per_sol * 100
    return pct_change


async def execute_swap(state: BotState, amount_sol: float) -> None:
    """Executes (or, in DRY_RUN mode, logs-only) a SOL->USDC swap.

    Real execution requires: a funded Keypair, a signed versioned
    transaction built from Jupiter's /swap endpoint response, and
    submission via `client.send_raw_transaction`. That signer wiring is
    deliberately NOT implemented here -- adding it means handling a real
    private key, which this bot should not do until you've reviewed and
    explicitly want that. DRY_RUN=false with no signer configured will
    intentionally do nothing but log a warning.
    """
    if DRY_RUN:
        logger.info(
            f"🟡 DRY RUN — would swap {amount_sol:.4f} SOL -> USDC via Jupiter. "
            f"Set OASIS_BOT_DRY_RUN=false + wire a signer in execute_swap() to go live."
        )
        return

    logger.warning(
        "OASIS_BOT_DRY_RUN=false but no signing keypair is wired up in execute_swap(). "
        "Refusing to submit a real transaction. This is intentional."
    )


async def trading_loop(state: BotState):
    async with httpx.AsyncClient() as http_client:
        while True:
            logger.info("📡 Fetching live SOL/USDC quote from Jupiter...")
            price = await fetch_sol_usdc_quote(http_client)

            if price is None:
                logger.warning("No price this tick (quote fetch failed) — skipping signal evaluation.")
            else:
                state.price_history.append(price)
                signal_pct = compute_momentum_signal(state, price)
                state.last_price_usdc_per_sol = price

                if signal_pct is None:
                    logger.info(f"💲 SOL/USDC = {price:.4f}. Building price history, no signal yet.")
                elif signal_pct > MOMENTUM_BUY_THRESHOLD_PCT:
                    logger.info(
                        f"🟢 BUY SIGNAL: SOL/USDC = {price:.4f} ({signal_pct:+.3f}% vs last tick, "
                        f"threshold {MOMENTUM_BUY_THRESHOLD_PCT}%)."
                    )
                    trade_size = min(0.5, MAX_POSITION_SOL - state.position_sol)
                    if trade_size > 0:
                        await execute_swap(state, trade_size)
                        state.position_sol += trade_size
                        state.sol_balance -= trade_size
                    else:
                        logger.info(f"Position cap reached ({MAX_POSITION_SOL} SOL) — skipping buy.")
                else:
                    logger.info(f"💲 SOL/USDC = {price:.4f} ({signal_pct:+.3f}% vs last tick). No signal.")

            await asyncio.sleep(POLL_INTERVAL_S)


async def main():
    logger.info(f"Initializing Solana Trading Bot ({'DRY RUN' if DRY_RUN else 'LIVE'}) on {SOLANA_RPC_URL}...")
    client = AsyncClient(SOLANA_RPC_URL)

    try:
        is_connected = await client.is_connected()
        if is_connected:
            logger.info("Successfully connected to Solana RPC.")
        else:
            logger.error("Failed to connect to Solana RPC.")
    except Exception as e:
        logger.error(f"Solana RPC connection check failed: {e}")

    state = BotState()
    logger.info("Listening for market data (Jupiter) and running momentum strategy...")

    try:
        await trading_loop(state)
    except KeyboardInterrupt:
        logger.info("Shutting down bot.")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
