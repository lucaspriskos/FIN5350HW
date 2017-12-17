# American Pricer
import numpy as np
from scipy.stats import binom

class VanillaOption(object):
    """An abstract interfact for plain vanilla options"""

    def __init__(self, strike, expiry):
        self.strike = strike
        self.expiry = expiry

    def payoff(self, spot):
        pass

class VanillaCallOption(VanillaOption):
    """A concrete class for vanilla call options"""

    def payoff(self, spot):
        return np.maximum(spot - self.strike, 0.0)

class VanillaPutOption(VanillaOption):
    """A concrete class for vanilla put options"""

    def payoff(self, spot):
        return np.maximum(self.strike - spot, 0.0)

def EuropeanBinomialPricer(option, spot, rate, vol, div, steps):
    h = option.expiry / steps
    nodes = steps + 1
    u = np.exp((rate - div) * h + vol * np.sqrt(h))
    d = np.exp((rate - div) * h - vol * np.sqrt(h))
    p = (np.exp((rate - div) * h) - d) / (u - d)
    S_t = np.zeros((nodes, nodes))
    C_t = np.zeros((nodes, nodes))

    for i in range(nodes):
        S_t[i, steps] = spot * (u ** (steps - i)) * (d ** i)

    C_t[:] = option.payoff(S_t[:])

    for i in range(steps - 1, -1, -1):
        for j in range(i + 1):
            S_t[j,i] = S_t[j + 1, i + 1] / d

    for i in range(steps -1, -1, -1):
        for j in range(i + 1):
            C_t[j,i] = np.maximum(np.exp(-rate * h) * (p * C_t[j, i + 1] + (1 - p) * C_t[j + 1, i + 1]), option.payoff(S_t[j,i]))

    return C_t[0,0]

thePut = VanillaPutOption(40, 1)
putPrice = EuropeanBinomialPricer(thePut, 41, 0.08, 0.30, 0.0, 3)
print(putPrice)

theCall = VanillaCallOption(100, 1)
callPrice = EuropeanBinomialPricer(theCall, 110.00, 0.05, 0.30, 0.035, 3)
print(callPrice)
