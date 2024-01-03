# imports
import numpy as np
from v1.util import normal_cdf, calculate_expected_value

class SpreadModule():

    def __init__(self, config: dict) -> None:
        self.__i_max = config['i_max']  # max allowed inventory adjustment to spread
        self.__i_a = config['i_a']  # inventory adjustment parameter
        self.__alpha = config['alpha']  # proportion of informed traders
        self.__eta = config['eta']  # base probability of a trade happening
        self.__sigma_W = config['sigma_W']  # standard deviation of the informed traders' signal noise
        self.pdf = None  # probability density function
        self.prices = np.arange(0, 101)  # possible prices
        self.reset_pdf(initial_true_value=config['initial_true_value'], std_dev=config['initial_std_dev'])

    def reset_pdf(self, initial_true_value: int, std_dev: int) -> None:
        """
        Initialize the probability vector for the market maker model.

        Args:
        initial_true_value (float): The initial estimate of the true value of the security.
        std_dev (float): The standard deviation around the initial true value.

        Returns:
        numpy.ndarray: A probability vector of size 101, representing probabilities for each price value from 0 to 100.
        """
        # Define the range of possible price values (0 to 100)
        price_values = self.prices

        # Calculate the probability of each price value based on a normal distribution centered around the initial true value
        probabilities = np.exp(-0.5 * ((price_values - initial_true_value) / std_dev) ** 2)
        probabilities /= probabilities.sum()

        # Store the probability vector
        self.pdf = probabilities

    def update_pdf(self, buy_order: bool, Pa=None, Pb=None) -> None:

        if buy_order:
            if Pa is None:
                raise Exception("Pa must be provided if buy_order is True")
            total_buy_probability = sum(self.__probability_buy_given_V(Vi, Pa) * self.pdf[Vi] 
                            for Vi in range(len(self.prices)))
            
            # Update the probability vector given a buy order
            updated_probability_vector = np.zeros(len(self.prices))
            for i in range(len(self.prices)):
                p_buy = self.__probability_buy_given_V(i, Pa)
                updated_probability_vector[i] = self.__probability_V_given_buy(i, self.pdf, p_buy, total_buy_probability)
            self.pdf = updated_probability_vector
        else:
            if Pb is None:
                raise Exception("Pb must be provided if buy_order is False")
            total_sell_probability = sum(self.__probability_sell_given_V(Vi, Pb) * self.pdf[Vi]
                                            for Vi in range(len(self.prices)))

            # update the probability vector given a sell order
            updated_probability_vector = np.zeros(len(self.prices))
            for i in range(len(self.prices)):
                p_sell = self.__probability_sell_given_V(i, Pb)
                updated_probability_vector[i] = self.__probability_V_given_sell(i, self.pdf, p_sell, total_sell_probability)

            self.pdf = updated_probability_vector
    
    def get_spread(self, cur_inv) -> tuple:
        bid = self.__calculate_bid()
        ask = self.__calculate_ask()
        adjustment = self.calculate_inventory_adjustment(cur_inv)
        if bid == ask:
            bid -= 1
            ask += 1

        # ensure the bid and asks with the adjustments are within 0 - 100
        bid = max(0, min(bid + adjustment, 100))
        ask = max(0, min(ask + adjustment, 100))
        return bid, ask

    def __calculate_bid(self) -> int:
        min_diff = float('inf')
        bid_price = 0
        expected_value = calculate_expected_value(self.pdf, self.prices)

        for price in reversed(self.prices):
            if price > expected_value:
                continue

            # Calculate the left and right hand sides of the equation
            left_hand_side = np.sum(self.pdf[self.prices <= price] * self.prices[self.prices <= price])
            right_hand_side = np.sum(self.pdf[self.prices > price] * self.prices[self.prices > price])

            # Calculate the difference between the two sides
            diff = abs(right_hand_side - left_hand_side)

            # Update the bid price if this is the smallest difference so far
            if diff < min_diff:
                min_diff = diff
                bid_price = price
            else:
                # Stop cycling down if the difference starts increasing
                break
        
        return min(max(bid_price, 0), 100)

    def __calculate_ask(self) -> int:
        min_diff = float('inf')
        ask_price = 0
        expected_value = calculate_expected_value(self.pdf, self.prices)

        for price in self.prices:
            if price < expected_value:
                continue

            # Calculate the left and right hand sides of the equation
            left_hand_side = np.sum(self.pdf[self.prices <= price] * self.prices[self.prices <= price])
            right_hand_side = np.sum(self.pdf[self.prices > price] * self.prices[self.prices > price])

            # Calculate the difference between the two sides
            diff = abs(right_hand_side - left_hand_side)

            # Update the ask price if this is the smallest difference so far
            if diff < min_diff:
                min_diff = diff
                ask_price = price
            else:
                # Stop cycling up if the difference starts increasing
                break

        return max(0, min(ask_price, 100))

    def calculate_inventory_adjustment(self, cur_inv) -> int:
        return int(self.__i_max * (1 - np.exp(-self.__i_a * np.abs(cur_inv))) * -np.sign(cur_inv))
    
    
    def __probability_buy_given_V(self, Vi, Pa) -> float:
        """
        Compute the probability of a buy order given the true value V = Vi.

        Args:
        Vi (float): The potential true value of the security.
        Pa (float): The current ask price set by the market maker.
        alpha (float): The proportion of informed traders in the market.
        eta (float): The base probability of a trade happening.
        sigma_W (float): The standard deviation of the informed traders' signal noise.

        Returns:
        float: The probability of observing a buy order given V = Vi.
        """
        if Vi <= Pa:
            # Calculate the probability for the case where Vi <= Pa
            return (1 - self.__alpha) * self.__eta + self.__alpha * (1 - normal_cdf(Pa - Vi, 0, self.__sigma_W))
        else:
            # Calculate the probability for the case where Vi > Pa
            return (1 - self.__alpha) * self.__eta + self.__alpha * normal_cdf(Vi - Pa, 0, self.__sigma_W)
            
    def __probability_sell_given_V(self, Vi, Pb):
        """
        Compute the probability of a sell order given the true value V = Vi.

        Args:
        Vi (float): The potential true value of the security.
        Pb (float): The current bid price set by the market maker.
        alpha (float): The proportion of informed traders in the market.
        eta (float): The base probability of a trade happening.
        sigma_W (float): The standard deviation of the informed traders' signal noise.

        Returns:
        float: The probability of observing a sell order given V = Vi.
        """
        if Vi >= Pb:
            # Calculate the probability for the case where Vi >= Pb
            return (1 - self.__alpha) * self.__eta + self.__alpha * (1 - normal_cdf(Vi - Pb, 0, self.__sigma_W))
        else:
            # Calculate the probability for the case where Vi < Pb
            return (1 - self.__alpha) * self.__eta + self.__alpha * normal_cdf(Pb - Vi, 0, self.__sigma_W)
        
    def __probability_V_given_buy(self, px, probability_vector, probability_buy, total_buy_probability):
        """
        Compute the posterior probability P(V=Vi | Buy).

        Args:
        px (float): The price level for the potential true value Vi.
        probability_vector (numpy.ndarray): The current probability vector for all possible values of V.
        probability_buy (float): The probability of a buy order given V = Vi.
        total_buy_probability (float): The total probability of observing a buy order, summed over all V.

        Returns:
        float: The posterior probability P(V=Vi | Buy).
        """
        prior_probability = probability_vector[px]
        return (probability_buy * prior_probability) / total_buy_probability
    
    def __probability_V_given_sell(self, px, probability_vector, probability_sell, total_sell_probability):
        """
        Compute the posterior probability P(V=Vi | Sell).

        Args:
        px: (float): The price level for the potential true value Vi.
        probability_vector (numpy.ndarray): The current probability vector for all possible values of V.
        probability_sell (float): The probability of a sell order given V = Vi.
        total_sell_probability (float): The total probability of observing a sell order, summed over all V.

        Returns:
        float: The posterior probability P(V=Vi | Sell).
        """
        prior_probability = probability_vector[px]
        return (probability_sell * prior_probability) / total_sell_probability