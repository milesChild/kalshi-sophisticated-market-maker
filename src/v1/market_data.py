import kalshi_python

class MarketDataModule:

    def __init__(self, api: kalshi_python.ApiInstance):
        self.api = api

    def get_last(self, ticker: str) -> int:
        market_response = self.api.get_market(ticker)
        return market_response.market.last_price

    def get_orderbook(self, ticker: str) -> dict:
        orderbook_response = self.api.get_market_orderbook(ticker)
        return orderbook_response.orderbook
    
    def get_bbo(self, ticker: str) -> tuple:

        orderbook = self.get_orderbook(ticker)
        if len(orderbook.yes) > 0:
            best_bid = max(orderbook.yes, key=lambda x: x[0])[0]
        else:
            best_bid = 0
        if len(orderbook.no) > 0:
            best_offer = 100 - max(orderbook.no, key=lambda x: x[0])[0]
        else:
            best_offer = 0
            
        return best_bid, best_offer
    
    def get_trades(self, ticker: str, limit=100) -> list:
        trades_response = self.api.get_trades(ticker=ticker, limit=limit)
        trades = trades_response.trades
        # reverse the order of the trades
        trades.reverse()
        return trades