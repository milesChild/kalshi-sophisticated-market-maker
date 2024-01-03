import math
import numpy as np

def normal_cdf(x, mean, std_dev):
    """
    Compute the cumulative distribution function (CDF) for a normal distribution.

    Args:
    x (float): The point at which to evaluate the CDF.
    mean (float): The mean of the normal distribution.
    std_dev (float): The standard deviation of the normal distribution.

    Returns:
    float: The value of the CDF at x.
    """
    return 0.5 * (1 + math.erf((x - mean) / (std_dev * math.sqrt(2))))

# Function to calculate the expected value E[V]
def calculate_expected_value(pdf, possible_prices):
    return np.sum(pdf * possible_prices)