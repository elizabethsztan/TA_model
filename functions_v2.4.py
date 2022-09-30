#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thus Aug 25 10:46:13 2022

Functions required to run model

v2 update: allows for model to start in the middle of fund's lifetime
v2.1 update: function input allows for OOP
- the only different function is Simulation
- information stored in a dataframe
v2.2 update: 
- RC input can be of variable length
- includes a parameter to allow funds to call a specific % of committed/uncalled capital
- growth rate can now be different yearly
v2.3 update:
- yearly growth rates are now modelled with a Student's t-distribution
- (df = 3, daily mean = 0.08/250, daily std = 0.2/sqrt(250), then annual G multipled by 1.2 for PE returns)
v2.4 update:
- growth series is now external. This update runs with TA_model_classv1.3.py and sandbox1.py

@author: liz
"""
#import required libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#%%

"""
Rate of contribution (RC)

make_RC is for new funds (vintage year is present)
- it takes an input of RCs for the future years 
- if there is incomplete data, the remaining years RC assumed to be the last input value

make_RC_mid is for funds whose vintage year has passed (existing funds)

This function needs to be run before the simulation function.
(Written outside because it allows user to easily change RC values).

"""

def make_RC (L, RC_input):
    RC=[0]
    for i in range (L):
        if i<len(RC_input):
            RC.append(RC_input[i])
        else:
            RC.append(RC_input[len(RC_input)-1])
    return RC

def make_RC_mid (S, L, RC_input): #S is age of fund
    RC=[RC_input[0]]
    for i in range(1,L-S):
        if i<len(RC_input):
            RC.append(RC_input[i])
        else:
            RC.append(RC_input[len(RC_input)-1])
    return RC

"""
Growth (G) (v2.3 update)

make_G allows you to make an array of the growth parameter for each year using random distrbution

"""

#below function makes daily returns for public equity
#we assume 100% correlation (else must use bivariate dist)
#alpha and beta numbers are dependent on asset class

def get_annual_G (daily_mean = 0.08/250, daily_std = 0.2/np.sqrt(250), alpha = 0, beta = 1): #L is the number of years
    days = 250 #number of working days in one year 
    g = []
    
    #we are modelling the daily return with a Student's t distribution of df = 3
    for i in range(days):
        num = np.random.standard_t(3, size=None) * 0.01 #make a %
        #truncate the data at 5% on both tails of the distrubution. This corresponds to 3.18 for the chosen distribution
        if abs(num) > 3.18*0.01:
            if num > 3.18*0.01:
                g.append(3.18*0.01)
            else:
                g.append (-3.18*0.01)
        else:
            g.append(num)
    
    #new mean and std for public equity returns
    new_std = daily_std
    new_mu = daily_mean
    
    #shift and scale the returns to fit new mean and std
    scaler = new_std/np.std(g)
    g_scaled  = [i * scaler for i in g]
    shifter = new_mu - np.mean(g_scaled)
    g_shifted  = [i + shifter for i in g_scaled]
    
    g_spec = [i * beta + alpha/days for i in g_shifted] #adjust for specific asset class
    
    annual_G = 1
    
    for i in range (days):
        if g_spec[i] != 0:
            annual_G = annual_G * (g_spec[i]+1)
        else:
            annual_G = annual_G * 1
    
    annual_G = annual_G -1 #previous parameters are for public equity. Multiplier is to get private equity returns
    
    return annual_G

G = get_annual_G()

def make_G_df(L, alpha, beta, start_date):
    g = []
    years = []
    for i in range (L):
        temp = get_annual_G(alpha = alpha, beta = beta)
        g.append(temp)
        years.append(start_date)
        start_date+=1
    
    d = {"Years": years,
          "Growth rate": g}
    g_dataframe = pd.DataFrame(data=d)
    return g_dataframe

def get_G_list(g_dataframe, vintage, L):
    S = current_year - vintage 
    if S ==0:
        gs = g_dataframe.loc[(g_dataframe['Years'] >= current_year) & (g_dataframe['Years'] <= vintage+L)]
    if S!=0:
        gs = g_dataframe.loc[(g_dataframe['Years'] >= current_year) & (g_dataframe['Years'] <= vintage+L-S)]
    
    return gs['Growth rate'].tolist()


"""
Contribution (C)

Below functions are for  produces a list of contributions ($million) made to the fund yearly.
It also returns the outstanding contributions (OC) yearly. 
(Outstanding contributions are committed capital not yet paid in)

make_contributions is for new funds
make_contributions_mid is for existing funds

"""      

def make_contributions (L, CC, RC, FCC): #FCC is final capital call. ie. Fund will call 90% of capital
    C = []
    PIC =[0]
    OC = []
    count=0
    for i in range (0,L):
        x = RC[i]*(CC-PIC[i])
        count += x
        if count < FCC * CC:
            PIC.append(count) 
            OC.append(CC-PIC[i+1])
        else:
            PIC.append(FCC * CC)
            OC.append(CC - FCC * CC)
    for i in range (1,len(PIC)):
        C.append(PIC[i]-PIC[i-1])
    if PIC[-1]< FCC * CC:
        res = FCC * CC - PIC[-2]
        C[-1]=res
        PIC[-1]=FCC * CC
        OC[-1] = CC - FCC * CC
    
    return C, PIC

# rc = make_RC(8, [0.1, 0.2, 0.5])
# con = make_contributions(8, 100, rc, 0.9 )
#print (con)


#!! FCC in this function is a % of unpaid capital. NOT comitted capital, as that is not necessarily known
def make_contributions_mid (S, L, UC, RC, FCC): #UC is uncalled cap
    C = []
    PIC =[0]
    OC = []
    count=0
    for i in range (0,L-S):
        x = RC[i]*(UC-PIC[i])
        count += x
        if count < FCC * UC:
            PIC.append(count) 
            OC.append(UC-PIC[i+1])
        else:
            PIC.append(FCC * UC)
            OC.append(UC - FCC * UC)
    for i in range (1,len(PIC)):
        C.append(PIC[i]-PIC[i-1])
    if PIC[-1]< FCC * UC:
        res = FCC * UC - PIC[-2]
        C[-1]=res
        PIC[-1]=FCC * UC
        OC[-1] = UC - FCC * UC
    
    return C, PIC

"""
Distribution (D)

Produces a list of capital distributed back to the investors ($million) yearly.
Also outputs the net asset value (NAV) of the fund.
(NAV increases as fund grows, decreases as distrbutions paid out)

make_distributions is for new funds
make_distributions_mid is for existing funds 

"""

def make_distributions(YLD, L, B, G, C):
    NAV = [0]
    D = [0]
    RD = []
    CD = []
    
    for i in range (L): #loop determines if RD = YLD or a value depending on B
        x = (i/L)**B
        if YLD>x:
            RD.append(YLD)
        else:
            RD.append(x)
            
    for i in range (1,L): 
        D.append(RD[i]*NAV[i-1]*(1+G[i-1]))#D depends on RD, NAV and G by formula
        NAV.append(NAV[i-1]*(1+G[i-1])+C[i]-D[i])#NAV depends on G, C and D by formula
    
    count=0
    for i in range(len(D)):
        count+=D[i]
        CD.append(count)
        
    #print(len(NAV), len(D), len(RD), len(CD))
    
    return NAV, D, RD, CD

def make_distributions_mid(YLD, S, L, B, G, C, NAV_0, D_0):
    NAV = [NAV_0]
    D = [D_0]
    RD = []
    CD = []
    
    for i in range (S,L): 
        x = (i/L)**B
        if YLD>x:
            RD.append(YLD)
        else:
            RD.append(x)
    #print(RD)  
    for i in range (1,L-S): 
        D.append(RD[i]*NAV[i-1]*(1+G[i-1]))#D depends on RD, NAV and G by formula
        NAV.append(NAV[i-1]*(1+G[i-1])+C[i]-D[i])#NAV depends on G, C and D by formula

    count=0
    for i in range(len(D)):
        count+=D[i]
        CD.append(count)
    
    #print(len(NAV), len(D), len(RD), len(CD))
    
    return NAV, D, RD, CD


"""
Simulation

This function inputs the RC, CC, L, B, G and YLD. 
It gives six plots showing yearly RC, C, OC, NAV, D and CD.
Simulation incorporates functions to produce contributions and distributions.
But not rate of contribution. That is an external input (see above).

Simulation produced for ease of the user. 

"""

def simulation (fund, plot):
    
    if fund._vintage == current_year:
        RC = make_RC(fund._lifetime, fund.RC)
        G = fund.G
        C, OC = make_contributions (fund._lifetime, fund.UC, RC, fund.FCC)
        NAV, D, RD, CD = make_distributions(fund.YLD, fund._lifetime, fund.bow, G, C)
        
        timeseries = [] #time series is done w/o use of external libraries. Perhaps could update for quaterly/monthly data
        for i in range (fund._lifetime):
            timeseries.append(current_year+i)

    else:
        RC = make_RC_mid(fund.age, fund._lifetime, fund.RC)
        G = G = fund.G
        C, OC = make_contributions_mid (fund.age, fund._lifetime, fund.UC, RC, fund.FCC)
        NAV, D, RD, CD = make_distributions_mid(fund.YLD,fund.age, fund._lifetime, fund.bow, G, C, fund.NAV, fund.last_dist)
        
        timeseries = []
        for i in range (fund._lifetime-fund.age):
            timeseries.append(fund._vintage+i)

    net_CF = np.array(D)-np.array(C) #net cash flow 
    
    d = {"Years": timeseries,
          #"Rate of contribution": RC,
          #"Contributions": C,
          #"Outstanding contributions": OC,
          #"Net asset value": NAV, 
          #"Rate of distribution": RD,
          #"Distributions": D, 
          #"Cumulative distributions": CD,
          "Net cash flow": net_CF
          
          }
    CF_dataframe = pd.DataFrame(data=d) #construct dataframe
    
    if plot == True: #to plot cash flow
        CF_dataframe.plot(x="Years", y="Net cash flow")
        plt.grid()
        plt.ylabel("$ million")
        plt.title(fund._fundtype+ ": "+fund._name)
        plt.show()
    
    
    return CF_dataframe

"""
plot is used to easily plot many TA models on the same graph

"""

def plot(TA_model):
    df = TA_model.calc_CF(plot=False)
    years = df['Years'].tolist()
    cf = df['Net cash flow'].tolist()
    plt.plot(years, cf, label = TA_model._name)


    