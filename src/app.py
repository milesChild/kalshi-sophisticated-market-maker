# imports
import kalshi_python
import sys
import logging
import datetime
import time
from v1.market_data import MarketDataModule
from v1.ordering import OrderingModule
from v1.portfolio import PortfolioModule
from v1.spread import SpreadModule
from v1.jdm import JumpDetector
from credentials import EMAIL, PW
from config import spread_module_config, log_file_path
from util import order_diff, JsonFormatter, trade_diff, yes_safety_check, no_safety_check
from v1.util import calculate_expected_value

# note: yes, ik this is poor implementation. this is not hft

def loop(mdp: MarketDataModule, oms: OrderingModule, pf: PortfolioModule, sm: SpreadModule, jdm: JumpDetector, ticker: str):

    global INVENTORY, BID, ASK, TRADES, LAST_TS
    
    # get new trades
    new_trades = mdp.get_trades(ticker)
    TRADES, LAST_TS = trade_diff(new_trades, LAST_TS)

    # update pdf
    for trade in TRADES:
        buy = True if trade['taker_side'] == 'yes' else False
        sm.update_pdf(buy_order=buy, Pa=trade['yes_price'], Pb=trade['yes_price'])
        # anomaly detection
        if jdm.update(trade):
            logging.info({"message_type": "ProgramInfo", "message_value": "JDM Anomaly Detected - Resetting PDF"})
            logging.info({"message_type": "PDF", "message_value": f"{sm.pdf}"})
            ev = calculate_expected_value(sm.pdf, sm.prices)
            sm.reset_pdf(initial_true_value=ev, std_dev=spread_module_config['initial_std_dev'])
        
    cur_inv = pf.get_inventory(ticker)
    open_orders = pf.get_open_orders(ticker)
    best_bid, best_offer = mdp.get_bbo(ticker)
    orderbook = mdp.get_orderbook(ticker)
    yes_check = yes_safety_check(orderbook, open_orders)
    no_check = no_safety_check(orderbook, open_orders)
    bid, ask = sm.get_spread(cur_inv)
    orders, cancels = order_diff(bid, ask, open_orders, best_bid, best_offer, ticker, spread_module_config['trade_qty'], yes_check, no_check)
    for cancel in cancels:
        logging.info({"message_type": "OrderCancel", "message_value": cancel})
        oms.cancel_order(cancel)

    for order in orders:
        oms.place_order(order)
        logging.debug({"message_type": "OrderPlace", "message_value": order})
    
    # logging
    if cur_inv != INVENTORY:
        logging.info({"message_type": "InventoryDelta", "message_value": int(cur_inv - INVENTORY)})
        INVENTORY = cur_inv
    if bid != BID:
        logging.info({"message_type": "BidDelta", "message_value": int(bid - BID)})
        BID = bid
    if ask != ASK:
        logging.info({"message_type": "AskDelta", "message_value": int(ask - ASK)})
        ASK = ask
    # debug log
    logging.debug({"message_type": "PDF", "message_value": f"{sm.pdf}"})
    
    time.sleep(2)  # sleeping is necessary because kalshi portfolio endpoint is slow to update after placing orders

if __name__ == "__main__":

    # set up logging
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    ticker = sys.argv[1]
    logfilepath = log_file_path+ticker+str(date)+".log"

    # Set up JSON logging
    logging.basicConfig(filename=logfilepath, level=logging.DEBUG)
    logger = logging.getLogger()
    handler = logger.handlers[0]
    handler.setFormatter(JsonFormatter())

    logging.info({"message_type": "ProgramInfo", "message_value": f"Initializing Sophisticated Naive Market Maker with ticker {ticker}..."})

    # initialize kalshi api
    config = kalshi_python.Configuration()
    config.host = "https://trading-api.kalshi.com/trade-api/v2"

    kalshi_api = kalshi_python.ApiInstance(
    email=EMAIL,
    password=PW,
    configuration=config,
    )

    logging.info({"message_type": "ProgramInfo", "message_value": f"Successfully logged in to Kalshi API. Beginning trading..."})

    # create modules
    mdp = MarketDataModule(kalshi_api)
    oms = OrderingModule(kalshi_api)
    pf = PortfolioModule(kalshi_api)
    sm = SpreadModule(spread_module_config)
    jdm = JumpDetector(0.6, 10)

    # initialize global variables
    global INVENTORY, BID, ASK, TRADES
    INVENTORY = 0
    BID = 0
    ASK = 0
    TRADES = []
    LAST_TS = None

    # warmup
    new_trades = mdp.get_trades(ticker, 1000)
    TRADES = new_trades

    historical_trade_prices = []

    # TODO: Temp (below)

    for trade in TRADES:
        historical_trade_prices.append(trade['yes_price'])
    
    if len(historical_trade_prices) != 0:
        median_trade_price = sorted(historical_trade_prices)[len(historical_trade_prices)//2]
        sm.reset_pdf(initial_true_value=median_trade_price, std_dev=spread_module_config['initial_std_dev'])
    else:
        logging.info({"message_type": "ProgramInfo", "message_value": "No historical trades found. Using default initial true value."})

    # TODO: Temp (above)

    # update pdf
    for trade in TRADES:
        historical_trade_prices.append(trade['yes_price'])
        buy = True if trade['taker_side'] == 'yes' else False
        sm.update_pdf(buy_order=buy, Pa=trade['yes_price'], Pb=trade['yes_price'])
        _ = jdm.update(trade)
        created_time = datetime.datetime.strptime(trade['created_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if LAST_TS == None or created_time > LAST_TS:
            LAST_TS = created_time
    
    # log initial pdf
    logging.info({"message_type": "PDF", "message_value": f"{sm.pdf}"})
    # log initial expected value
    ev = calculate_expected_value(sm.pdf, sm.prices)
    logging.info({"message_type": "ExpectedValue", "message_value": f"{ev}"})

    while True:

        # provide liquidity until your computer dies
        try:
            loop(mdp, oms, pf, sm, jdm, ticker)
        except Exception as e:
            logging.error({"message_type": "ProgramError", "message_value": f"Error: {e}"})