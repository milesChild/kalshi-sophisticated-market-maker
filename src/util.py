import logging
import json
import datetime
import uuid
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class JsonFormatter(logging.Formatter):
    def format(self, record):
        message = record.msg
        log_record = {
            "message_type": message.get("message_type", "Unknown"),
            "message_value": message.get("message_value", ""),
            "timestamp": datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        }
        return json.dumps(log_record)
    
def order_diff(bid: int, ask: int, orders: list, best_bid: int, best_offer: int, ticker: str, trade_qty: int) -> tuple:
    yes_price = bid
    no_price = 100 - ask
    to_cancel = [] # list of order ids to cancel
    to_order = [] # list of orders to place
    existing_yes = False
    existing_no = False

    # check for stale prices
    for order in orders:
        # yes checks
        if order["side"] == "yes":  # we already have an order out at this price
            if order["yes_price"] == yes_price:
                existing_yes = True
            elif order["yes_price"] != yes_price:  # stale price
                to_cancel.append(order["order_id"])
        # no checks
        elif order["side"] == "no":
            if order["no_price"] == no_price:
                existing_no = True
            elif order["no_price"] != no_price:
                to_cancel.append(order["order_id"])
    
    # generate orders
    if not existing_yes:
        if bid >= best_offer:
            to_order.append({'action': 'buy', 'type': 'limit', 'ticker': ticker, 'count': trade_qty, 'side': 'yes', 'yes_price': int(best_offer-1), 'client_order_id': str(uuid.uuid4())})
        else:
            to_order.append({'action': 'buy', 'type': 'limit', 'ticker': ticker, 'count': trade_qty, 'side': 'yes', 'yes_price': int(bid), 'client_order_id': str(uuid.uuid4())})
    if not existing_no:
        if ask <= best_bid:
            to_order.append({'action': 'buy', 'type': 'limit', 'ticker': ticker, 'count': trade_qty, 'side': 'no', 'no_price': int(100 - best_bid+1), 'client_order_id': str(uuid.uuid4())})
        else:
            to_order.append({'action': 'buy', 'type': 'limit', 'ticker': ticker, 'count': trade_qty, 'side': 'no', 'no_price': int(100 - ask), 'client_order_id': str(uuid.uuid4())})
    
    return to_order, to_cancel

# for log replays

def parse_log_file(log_file_path):
    inventory_history = []
    bid_history = []
    ask_history = []

    with open(log_file_path, 'r') as file:
        for line in file:
            try:
                log_entry = json.loads(line)
                message_type = log_entry.get("message_type")
                message_value = log_entry.get("message_value")
                timestamp = log_entry.get("timestamp")

                if message_type == "InventoryDelta":
                    inventory_history.append((timestamp, message_value))
                elif message_type == "BidDelta":
                    bid_history.append((timestamp, message_value))
                elif message_type == "AskDelta":
                    ask_history.append((timestamp, message_value))
            except json.JSONDecodeError:
                continue  # Skip lines that are not valid JSON

    return inventory_history, bid_history, ask_history

def plot_inventory_history(inventory_history):
    # Parse timestamps and inventory values
    timestamps = [datetime.strptime(record[0], '%Y-%m-%d %H:%M:%S') for record in inventory_history]
    inventory_values = [record[1] for record in inventory_history]

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, inventory_values, marker='o', linestyle='-')
    
    # Formatting the plot
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gcf().autofmt_xdate()  # Rotate date labels
    plt.xlabel('Time')
    plt.ylabel('Inventory Level')
    plt.title('Inventory History Over Time')
    plt.grid(True)
    
    # Show plot
    plt.show()

def plot_bid_ask_history(bid_history, ask_history):
    # Parse timestamps and values
    bid_timestamps = [datetime.strptime(record[0], '%Y-%m-%d %H:%M:%S') for record in bid_history]
    bid_values = [record[1] for record in bid_history]
    ask_timestamps = [datetime.strptime(record[0], '%Y-%m-%d %H:%M:%S') for record in ask_history]
    ask_values = [record[1] for record in ask_history]

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(bid_timestamps, bid_values, marker='o', linestyle='-', color='blue', label='Bid')
    plt.plot(ask_timestamps, ask_values, marker='x', linestyle='-', color='red', label='Ask')

    # Formatting the plot
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gcf().autofmt_xdate()  # Rotate date labels
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.title('Bid and Ask History Over Time')
    plt.legend()
    plt.grid(True)
    
    # Show plot
    plt.show()