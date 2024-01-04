spread_module_config = {
    "i_max": 5,  # max inventory adjustment
    "i_a": 0.2,  # inventory control scaling factor
    "initial_true_value": 12,  # assumption of initial true value
    "initial_std_dev": 10,  # assumption of initial true value standard deviation
    "alpha": 0.2,  # assumption of proportion of informed traders
    "eta": 0.2,  # assumption of probability of noise trader order
    "sigma_W": 3,  # assumption of standard deviation of informed trader noise
    "lot_size": 100,  # assumption of typical trade lot size
    "trade_qty": 1  # quantity this market maker posts bids and offers at
}
log_file_path = "log/"