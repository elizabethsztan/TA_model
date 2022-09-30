#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 11:53:19 2022

TA Model Sandbox 

This file is to give an example of how the simulation will work
It works with functions_v2.4.py and TA_model_class_v1.3.py

@author: liz
"""
#Make external growth series for the different asset classes

time_horizon = 20 #20 year growth series. 
start_date = current_year

public_equity_series = make_G_df(time_horizon, 0, 1, start_date) #example of how to run the following
PE_growth_series = make_G_df(time_horizon, 0, 1.2, start_date)
VC_growth_series = make_G_df(time_horizon, 0.03, 1.7, start_date)
RE_growth_series = make_G_df(time_horizon, 0, 0.77, start_date)
#real estate fund CAPM are 79.6% R-square corr to market. This model may not be accurate.
#future updates should use bi/multivariate dist to produce growth values (currently only single-variable students t dist is used)


Lit_Ventures = VentureCapital(name ="Lit Ventures",
                    vintage=2022, 
                    lifetime =12, 
                    UC=150, 
                    RC=[0.25, 0.333, 0.5], 
                    bow=2.5
                    )

NPL_fund = TA_model(name ="Imma take ur home",
                    fundtype="NPL", 
                    vintage=2020, 
                    lifetime =12, 
                    UC=70, 
                    RC=[0.1, 0.2, 0.5], 
                    bow=3, 
                    NAV =50,
                    last_dist=10)

Real_Estate = RealEstate(name ="Big Houses",
                    vintage=2024, 
                    lifetime =12, 
                    UC=120, 
                    RC=[0.1, 0.2, 0.5], 
                    bow=3, 
                    NAV = 0.3,
                    last_dist=0.2)

plot(Lit_Ventures)
plot(NPL_fund)
plot(Real_Estate)
plt.grid()
plt.legend()
plt.xlabel("Years")
plt.ylabel("Net cash flow")



