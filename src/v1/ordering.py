import kalshi_python

class OrderingModule():

    def __init__(self, api: kalshi_python.ApiInstance):
        self.api = api

    def place_order(self, order: dict) -> None:
        self.__safety_check(order)
        _ = self.api.create_order(order)

    def cancel_order(self, order_id: str) -> None:
        _ = self.api.cancel_order(order_id)

    def __safety_check(self, order: dict) -> None:
        if order['side'] == 'yes':
            try:
                assert order['yes_price'] < 100
            except AssertionError:
                raise Exception(f"Order {order} has an invalid price of {order['yes_price']}.")
        elif order['side'] == 'no':
            try:
                assert order['no_price'] >= 0
            except AssertionError:
                raise Exception(f"Order {order} has an invalid price of {order['no_price']}.")