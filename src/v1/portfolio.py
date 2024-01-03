import kalshi_python

class PortfolioModule:

    def __init__(self, api: kalshi_python.ApiInstance):
        self.api = api

    def get_inventory(self, ticker: str) -> int:
        inventory_response = self.api.get_positions(ticker=ticker)
        position = 0
        for posn in inventory_response.market_positions:
            if posn.ticker == ticker:
                position += posn.position
        return position

    def get_open_orders(self, ticker: str) -> list:
        get_orders_response = self.api.get_orders(ticker=ticker)
        orders = []
        for order in get_orders_response.orders:
            if order['status'] == "resting":
                orders.append(order)
        return orders