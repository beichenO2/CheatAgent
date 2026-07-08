#!/usr/bin/env python3
"""Run MarketTruthAgent demo server."""
from market_truth_agent.api.app import create_app

if __name__ == "__main__":
    app = create_app("data/conversations.db")
    app.run(host="0.0.0.0", port=8765, debug=True)
