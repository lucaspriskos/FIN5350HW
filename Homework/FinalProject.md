
## Final Project - European Barrier Option Pricer
### By: Brenan Stewart, Lucas Priskos

Based on our output generated, we can conclude that there was a definite tradeoff between precision and computational speed. Doing only 100 simulations, the program ran in under one second on each attempt. However, we sacrificed a large variation in price in order to achieve that speed.

When we increased that to 100,000 simulations, the program took between 2-6 minutes depending on the sampling techniques we applied to the code. Besides the increased computational time, we found that our variance and price were extremely uniform, although better precision is still bought with more time. What is better ultimately depends on the context of the situation. Perhaps faster results are needed in trading at the expense of precision. Maybe sometimes the opposite holds true. 


### 100 Simulations:
1. Regular MC
     - __Time:__ 0.0114
     - __Price:__ 2.2926
     - __Standard Error:__ .4006 
     
     
2. Using Stratified Sampling
     - __Time:__ 0.0345
     - __Price:__ 1.41163
     - __Standard Error:__ 0.3322
     
     
2. Using Antithetic Sampling
     - __Time:__ 0.0196
     - __Price:__ 2.2263
     - __Standard Error:__ 0.2805
     
     
2. Using Combined Antithetic and Stratified Sampling
     - __Time:__ 0.0609
     - __Price:__ 2.1986
     - __Standard Error:__ 0.2835

### 100,000 Simulations
1. Regular MC
     - __Time:__ 143.8357
     - __Price:__ 1.0619
     - __Standard Error:__ 0.0032 
     
     
2. Using Stratified Sampling
     - __Time:__ 163.4515
     - __Price:__ 1.0580
     - __Standard Error:__ 0.0032
     
     
2. Using Antithetic Sampling
     - __Time:__ 367.8914
     - __Price:__ 1.0594
     - __Standard Error:__ 0.0022
     
     
2. Using Combined Antithetic and Stratified Sampling
     - __Time:__ 408.3226
     - __Price:__ 1.0596
     - __Standard Error:__ 0.0022

### Code:


```python

import numpy as np
import time
import random
from scipy.stats import norm
from math import log2



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

    
class EuroDownAndOutBarrier(object):
  
    
    def __init__(self, strike, expiry, spot, rate, vol, div, barrier, steps, simulations):
        
        self.barrier = barrier
        self.steps = steps
        self.simulations = simulations
        self.spot = spot
        self.expiry = expiry
        self.strike = strike
        self.dt = expiry / steps
        self.nudt = (rate - div - 0.5 * (vol ** 2)) * self.dt
        self.nu = (rate - div - 0.5)
        self.sigsdt = (vol * np.sqrt(self.dt))
        self.rate = rate
        
        
        
        
    def Normal(self):
        
        
        
        sum_CT = 0
        sum_CT2 = 0
        
        St = np.zeros(self.steps)
        St[0] = self.spot
        
        for i in range(self.simulations):
            
            epsilon = np.random.normal(0,1)
            
            z = WienerBridge(self.expiry, self.steps, epsilon)
            
            for j in range(1,(self.steps)):
                St[j] = St[j-1] * np.exp(self.nudt + self.sigsdt * z[j])
                if(St[j] < self.barrier):
                    St[j] = 0
                    
            Price = St[-1]        
                    
            CT = np.maximum(0, Price - self.strike)
            sum_CT = sum_CT + CT
            sum_CT2 = sum_CT2 + CT*CT
                        
        self.regVal = sum_CT/ self.simulations * np.exp(-self.rate * self.expiry)
        SD = np.sqrt((sum_CT2 - sum_CT * sum_CT / self.simulations) * np.exp(-2 * self.rate * self.expiry) / (self.simulations - 1))
        self.regSE = SD / np.sqrt(self.simulations)
        
        
        return(self.regVal, self.regSE)
            
            

        
    def Stratified(self):
        
        
        
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
                        
        self.stratVal = sum_CT/ self.simulations * np.exp(-self.rate * self.expiry)
        SD = np.sqrt((sum_CT2 - sum_CT * sum_CT / self.simulations) * np.exp(-2 * self.rate * self.expiry) / (self.simulations - 1))
        self.stratSE = SD / np.sqrt(self.simulations)
        
        
        return(self.stratVal, self.stratSE)
        
        
        
        
    def Antithetic(self):
        
        
        sum_CT = 0
        sum_CT2 = 0
        
                
        St = np.zeros([2,self.steps])
        St[:,0] = self.spot
        
        for i in range(self.simulations):
            
            ep1 = np.random.normal(0,1)
            ep2 = -ep1
            
            z1 = WienerBridge(self.expiry, self.steps, ep1)
            z2 = WienerBridge(self.expiry, self.steps, ep2)
            
            z = np.array([z1, z2])
            
            for j in range(1,(self.steps)):
                St[:,j] = St[:,j-1] * np.exp(self.nudt + self.sigsdt * z[:,j])
                if(St[0,j] < self.barrier):
                    St[0,j] = 0
                if(St[1,j] < self.barrier):
                    St[1,j] = 0
                    
            Price1 = St[0,-1]
            Price2 = St[1,-1]
                    
            CT1 = np.maximum(0, Price1 - self.strike)
            CT2 = np.maximum(0, Price2 - self.strike)
            sum_CT = sum_CT + CT1 + CT2
            sum_CT2 = sum_CT2 + CT1*CT1 + CT2*CT2
                        
        self.antValue = sum_CT/ (self.simulations * 2) * np.exp(-self.rate * self.expiry)
        SD = np.sqrt((sum_CT2 - sum_CT * sum_CT / (self.simulations * 2)) * np.exp(-2 * self.rate * self.expiry) / ((self.simulations * 2) - 1))
        self.antSE = SD / np.sqrt((self.simulations * 2))
        
        return(self.antValue, self.antSE)
        
    
    
    
    
    def Combined(self):
       
        
        
               
        sum_CT = 0
        sum_CT2 = 0
        
        St = np.zeros([2,self.steps])
        St[:,0] = self.spot
        
        for i in range(self.simulations):
            
            u1 = np.random.uniform(0,1)
            u2 = 1 - u1
            
            ep1 = norm.ppf(u1)
            ep2 = norm.ppf(u2)
            
            z1 = WienerBridge(self.expiry, self.steps, ep1)
            z2 = WienerBridge(self.expiry, self.steps, ep2)
            
            z = np.array([z1, z2])
            
            for j in range(1,(self.steps)):
                St[:,j] = St[:,j-1] * np.exp(self.nudt + self.sigsdt * z[:,j])
                if(St[0,j] < self.barrier):
                    St[0,j] = 0
                if(St[1,j] < self.barrier):
                    St[1,j] = 0
                    
            Price1 = St[0,-1]
            Price2 = St[1,-1]
                    
            CT1 = np.maximum(0, Price1 - self.strike)
            CT2 = np.maximum(0, Price2 - self.strike)
            sum_CT = sum_CT + CT1 + CT2
            sum_CT2 = sum_CT2 + CT1*CT1 + CT2*CT2
                        
        self.combinedVal = sum_CT/ (self.simulations * 2) * np.exp(-self.rate * self.expiry)
        SD = np.sqrt((sum_CT2 - sum_CT * sum_CT / (self.simulations * 2)) * np.exp(-2 * self.rate * self.expiry) / ((self.simulations * 2) - 1))
        self.combinedSE = SD / np.sqrt((self.simulations * 2))
        
        
        return(self.combinedVal, self.combinedSE)
        

        
        

                    
option = EuroDownAndOutBarrier(strike = 100, expiry = 1, spot = 100, rate = .06, vol=.2, div=.03, barrier = 99, steps = 8, simulations = 100)                  
                    
time1 = time.time()
option.Normal() 
time2 = time.time() 
print("\nThe Price using regular MC is: $", option.regVal)         
print("The standard error is: $", option.regSE)   
print("Time:  ", (time2-time1))

time1 = time.time()              
option.Stratified() 
time2 = time.time()   
print("\nThe Price using Stratified Sampling is: $", option.stratVal)         
print("The standard error is: $", option.stratSE) 
print("Time:  ", (time2-time1))  
        
time1 = time.time()
option.Antithetic() 
time2 = time.time()   
print("\nThe Price using Antithetic Sampling is: $", option.antValue)         
print("The standard error is: $", option.antSE)
print("Time:  ", (time2-time1))   
       
time1 = time.time()
option.Combined()  
time2 = time.time()  
print("\nThe Price using Combined Antithetic and Stratified Sampling is: $", option.combinedVal)         
print("The standard error is: $", option.combinedSE) 
print("Time:  ", (time2-time1))  
```


    ---------------------------------------------------------------------------

    ModuleNotFoundError                       Traceback (most recent call last)

    <ipython-input-1-9f4405f94274> in <module>()
          1 
    ----> 2 import numpy as np
          3 import time
          4 import random
          5 from scipy.stats import norm
    

    ModuleNotFoundError: No module named 'numpy'

