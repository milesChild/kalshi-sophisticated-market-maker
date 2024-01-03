spread_module_config = {
    "i_max": 5,  # max inventory adjustment
    "i_a": 0.2,  # inventory control scaling factor
    "initial_true_value": None,  # assumption of initial true value
    "initial_std_dev": 10,  # assumption of initial true value standard deviation
    "alpha": None,  # assumption of proportion of informed traders
    "eta": None,  # assumption of probability of noise trader order
    "sigma_W": None  # assumption of standard deviation of informed trader noise
}
log_file_path = "log/"
trade_qty = 1