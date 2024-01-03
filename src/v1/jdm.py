# imports
import numpy as np

class JumpDetector():

    def __init__(self, buy_ratio_threshold, ma_period) -> None:
        self.buy_ratio_threshold = buy_ratio_threshold
        self.ma_period = ma_period
        self.ma = np.array([])  # stores ma_period length moving average of buy ratios
        self.buy_ratios = np.array([])  # stores 2*ma_period length of buy ratios
    
    def update(self, trade: dict) -> bool:
        """Update the moving average and buy ratio arrays with the new buy ratio.
        
        Args:
            buy_ratio (float): The buy ratio to add to the arrays.
        
        Returns:
            bool: True if a jump is detected, False otherwise.
        """
        pass
        # add the new buy ratio to the array
        # self.buy_ratios = np.append(self.buy_ratios, buy_ratio)
        
        # # if the buy ratio array is longer than 2*ma_period, then remove the first element
        # if len(self.buy_ratios) > 2*self.ma_period:
        #     self.buy_ratios = np.delete(self.buy_ratios, 0)
        
        # # calculate the last ma_period length moving average of buy ratios
        # if len(self.buy_ratios) >= self.ma_period:
        #     self.ma = np.append(self.ma, np.mean(self.buy_ratios[-self.ma_period:]))
        # else:
        #     return False

        # # if the ma array is longer than ma_period, then remove the first element
        # if len(self.ma) > self.ma_period:
        #     self.ma = np.delete(self.ma, 0)
        
        # # if the last moving average is greater than the buy ratio threshold, then return True
        # if self.ma[-1] > self.buy_ratio_threshold:
        #     # reset the moving average
        #     return True
        # else:
        #     return False
    
    def reset(self) -> None:
        """Reset the moving average and buy ratio arrays."""
        self.ma = np.array([])
        self.buy_ratios = np.array([])