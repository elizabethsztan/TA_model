#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 10:18:44 2022

v1.1 update: RC input can be of variable length
v1.2 update: this update runs with functions_v2.3.py. It has subclasses for different asset classes
v1.3 update: growth series is now external. This update runs with functions_v2.4.py and sandbox1.py
@author: liz
"""

current_year = 2022

#%%
class TA_model:
    
    def __init__(self, name = "Unnamed", fundtype = "Not yet inputted", vintage = 0, lifetime = 0, UC = 0, RC=0, bow = 0, YLD=0, NAV=0, last_dist = 0, CF =0, net_profit=0, FCC = 0.9):
        
        self._name = name
        self._fundtype = fundtype
        self._lifetime = lifetime
        self._vintage = vintage
        self.UC = UC #either committed cap or uncalled commitment
        self.FCC = FCC #final capital call as a % of committed cap or uncalled commitment
        #self.growth_rate=growth_rate
        self.RC = RC #array of rate of contributions
        self.bow = bow
        self.YLD = YLD
        self.NAV = NAV
        self.last_dist = last_dist
        self.CF = CF
        self.age = current_year - self._vintage
        self.net_profit = net_profit
        self.G = get_G_list(PE_growth_series, self._vintage, self._lifetime)
    
        if self._name == "Unnamed":
            raise Exception("Input fund name")
        if self._fundtype == "Not yet inputted":
            raise Exception("Input fund type")
        if self._vintage == 0:
            raise Exception ("Input vintage year")
        if self._lifetime ==0:
            raise Exception ("Input lifetime")
        if self.UC == 0:
            raise Exception("Input committed or uncalled capital")
        # if type(self.growth_rate) != list:
        #     raise Exception("Input an array of growth rates (must be in list format)")
        if type(self.RC) != list:
            raise Exception("Input an array of rates of contribution (must be in list format)")
        # if len(self.growth_rate)> self._lifetime-self.age:
        #     raise Exception("Data inputted for growth rates is for more years than the funds (remaining) lifetime")
        if len(self.RC)> self._lifetime-self.age:
            raise Exception("Data inputted for rate of contribution is for more years than the funds (remaining) lifetime")
        if self.bow == 0:
            raise Exception("Input bow factor")
        if NAV == 0 and self._vintage != current_year:
            raise Exception("Input current NAV and most recent distribution")
        

    
    def readinit(self):
        print (
            "Initial conditions for ", self._name,
            "\n Fund type: ", self._fundtype,
            "\n Vintage: ", self._vintage,
            "\n Lifetime: ", self._lifetime
            )
    
    def calc_CF(self, plot = True): #can toggle whether to plot graph or not
        self.CF=simulation(self, plot)
        
        count = 0 
        for i in range(len(self.CF["Net cash flow"])):
            count += self.CF["Net cash flow"][i]
        self.net_profit = count
        
        print("Net profit/loss is $", self.net_profit, "M")
            
        return self.CF #self.net_profit
    
    def set_growth_params (self, alpha, beta):
        self.alpha = alpha
        self.beta = beta
        return self.alpha, self.beta
    

class VentureCapital(TA_model):
    def __init__(self, name = "Unnamed", vintage = 0, lifetime = 0, UC = 0, RC=0, bow = 0, YLD=0, NAV=0, last_dist = 0, CF =0, net_profit=0, FCC = 0.9):
        self._name = name
        self._fundtype = "Venture Capital"
        self._lifetime = lifetime
        self._vintage = vintage
        self.UC = UC 
        self.FCC = FCC 
        self.RC = RC
        self.bow = bow
        self.YLD = YLD
        self.NAV = NAV
        self.last_dist = last_dist
        self.CF = CF
        self.age = current_year - self._vintage
        self.net_profit = net_profit
        self.G = get_G_list(VC_growth_series, self._vintage, self._lifetime)
    
        if self._name == "Unnamed":
            raise Exception("Input fund name")
        if self._vintage == 0:
            raise Exception ("Input vintage year")
        if self._lifetime ==0:
            raise Exception ("Input lifetime")
        if self.UC == 0:
            raise Exception("Input committed or uncalled capital")
        if type(self.RC) != list:
            raise Exception("Input an array of rates of contribution (must be in list format)")
        if len(self.RC)> self._lifetime-self.age:
            raise Exception("Data inputted for rate of contribution is for more years than the funds (remaining) lifetime")
        if self.bow == 0:
            raise Exception("Input bow factor")
        if NAV == 0 and self._vintage != current_year:
            raise Exception("Input current NAV and most recent distribution")
            
class RealEstate(TA_model):
    def __init__(self, name = "Unnamed", vintage = 0, lifetime = 0, UC = 0, RC=0, bow = 0, YLD=0.1, NAV=0, last_dist = 0, CF =0, net_profit=0, FCC = 0.9):
        self._name = name
        self._fundtype = "Real Estate"
        self._lifetime = lifetime
        self._vintage = vintage
        self.UC = UC 
        self.FCC = FCC 
        self.RC = RC
        self.bow = bow
        self.YLD = YLD
        self.NAV = NAV
        self.last_dist = last_dist
        self.CF = CF
        self.age = current_year - self._vintage
        self.net_profit = net_profit
        self.G = get_G_list(RE_growth_series, self._vintage, self._lifetime)
    
        if self._name == "Unnamed":
            raise Exception("Input fund name")
        if self._vintage == 0:
            raise Exception ("Input vintage year")
        if self._lifetime ==0:
            raise Exception ("Input lifetime")
        if self.UC == 0:
            raise Exception("Input committed or uncalled capital")
        if type(self.RC) != list:
            raise Exception("Input an array of rates of contribution (must be in list format)")
        if len(self.RC)> self._lifetime-self.age:
            raise Exception("Data inputted for rate of contribution is for more years than the funds (remaining) lifetime")
        if self.bow == 0:
            raise Exception("Input bow factor")
        if NAV == 0 and self._vintage != current_year:
            raise Exception("Input current NAV and most recent distribution")



