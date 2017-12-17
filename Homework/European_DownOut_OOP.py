# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 18:19:27 2017

@author: Student
"""
import numpy as np
import time
import random
from scipy.stats import norm
from math import log2

class Option(object):
    """An abstract interface for plain vanilla options"""

    def __init__(self, strike, expiry):
        self.strike = strike
        self.expiry = expiry

    def payoff(self, spot):
        pass

class CallOption(Option):
    """A concrete class for vanilla call options"""

    def payoff(self, spot):
        return np.maximum(spot - self.strike, 0.0)

    
class PutOption(Option):
    """A concrete class for vanilla put options"""

    def payoff(self, spot):
        return np.maximum(self.strike - spot, 0.0)


class MarketData(object):
    
    def __init__(self, spot, rate, vol, div):
        self.spot = spot
        self.rate = rate
        self.vol = vol
        self.div = div

def WienerBridge(expiry, num_steps, endval):
    num_bisect = int(log2(num_steps))
    tjump = int(expiry)
    ijump = int(num_steps - 1)

    if endval == 0.0:
        endval = np.random.normal(scale = np.sqrt(expiry), size=1)

    z = np.random.normal(size=num_steps + 1)
    w = np.zeros(num_steps + 1)
    w[num_steps] = endval
    

    for k in range(num_bisect):
        left = 0
        i = ijump // 2 + 1    ## make sure this is integer division!
        right = ijump + 1
        limit = 2 ** k

        for j in range(limit):
            a = 0.5 * (w[left] + w[right])
            b = 0.5 * np.sqrt(tjump)
            w[i] = a + b * z[i]
            right += ijump + 1
            left += ijump + 1
            i += ijump + 1
        
        ijump //= 2    ## Again, make this is integer division!
        tjump /= 2

    return np.diff(w)  ## Recall the the Brownian motion is the first difference of the Wiener process

    
class Euro_Down_Out_Barrier(object):
    
    def __init__(self, option, data, barrier, steps = 8, simulations = 1000):
        
        self.barrier = barrier
        self.steps = steps
        self.simulations = simulations
        self.spot = data.spot
        self.expiry = option.expiry
        self.strike = option.strike
        self.dt = option.expiry / steps
        self.nudt = (data.rate - data.div - 0.5 * (data.vol ** 2)) * self.dt
        self.nu = (data.rate - data.div - 0.5)
        self.sigsdt = (data.vol * np.sqrt(self.dt))
        self.rate = data.rate
        
        
        
    def RegularMC(self):
        
        regular_time1 = time.time()
        
        sum_CT = 0
        sum_CT2 = 0
        
        St = np.zeros(self.steps)
        St[0] = self.spot

        
        for j in range(self.simulations):
            
            Barrier_Crossed = False
            for i in range(self.steps-1):
                epsilon = np.random.normal()
                St[i+1] = St[i] * np.exp(self.nudt + self.sigsdt * epsilon)
                if (St[i] <= self.barrier):
                    Barrier_Crossed = True
                    break
            if Barrier_Crossed:
                CT = 0
            else:
                CT = np.maximum(0, St - self.strike)
            sum_CT = sum_CT + CT
            sum_CT2 = sum_CT2 + CT*CT
        self.r_value = sum_CT / self.simulations * np.exp(-self.rate * self.expiry)
        SD = np.sqrt((sum_CT2 - sum_CT * sum_CT / self.simulations) * np.exp(-2 * self.rate * self.expiry) / (self.simulations - 1))
        self.r_SE = SD / np.sqrt(self.simulations)
        
        regular_time2 = time.time()
        self.r_time = regular_time2 - regular_time1
        return(self.r_value, self.r_SE, self.r_time)
            
            

        
    def StratifiedMC(self):
        
        strat_time1 = time.time()
        
        sum_CT = 0
        sum_CT2 = 0
        
        St = np.zeros(self.steps)
        St[0] = self.spot
        
        for i in range(self.simulations):
            
            unif = random.uniform(0,1)
            epsilon = norm.ppf(unif)
            
            z = WienerBridge(self.expiry, self.steps, epsilon)
            
            for j in range(1,(self.steps)):
                St[j] = St[j-1] * np.exp(self.nudt + self.sigsdt * z[j])
                if(St[j] < self.barrier):
                    St[j] = 0
                    
            Price = St[-1]        
                    
            CT = np.maximum(0, Price - self.strike)
            sum_CT = sum_CT + CT
            sum_CT2 = sum_CT2 + CT*CT
                        
        self.s_value = sum_CT/ self.simulations * np.exp(-self.rate * self.expiry)
        SD = np.sqrt((sum_CT2 - sum_CT * sum_CT / self.simulations) * np.exp(-2 * self.rate * self.expiry) / (self.simulations - 1))
        self.s_SE = SD / np.sqrt(self.simulations)
        
        strat_time2 = time.time()
        self.s_time = strat_time2 - strat_time1
        return(self.s_value, self.s_SE, self.s_time)
        

        

        
        
call = CallOption(100, 1)

data = MarketData(100, 0.06, 0.2, 0.03) 
                    
priceIt = Euro_Down_Out_Barrier(call, data, barrier = 99, steps = 8, simulations = 100)                  
                    
 
priceIt.RegularMC()  
print("\nThe Price using regular MC is: $", priceIt.r_value)         
print("The stardard error is: $", priceIt.r_SE)   
print("Time: ", priceIt.r_time)
              
priceIt.StratifiedMC()   

print("\nThe Price using Stratified Sampling is: $", priceIt.s_value)         
print("The stardard error is: $", priceIt.s_SE)   
print("Time: ", priceIt.s_time)        

                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
    
    

        
        
    