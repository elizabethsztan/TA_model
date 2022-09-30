# TA_model
Produces cash flows for funds of different asset classes that have a drawdown structure using the Takahashi-Alexander model.
To read more about maths behind the TA model, look at the ILLIQUID ALTERNATIVE ASSET FUND MODELING paper by D. Takahashi and S. Alexander (Yale).

Each TA_model is created as a class object. The code can currently model three asset classes: private equity, venture capital and real estate.
Each asset class is a subclass of the TA model class - the differences in the asset classes are the yearly growth parameters and the yield on the asset.

**Inputs:** <br /> 
Committed capital/uncalled capital (depending on whether the fund's vintage year has passsed)<br /> 
Rate of contribution <br /> 
Vintage year<br /> 
Lifetime of the fund<br /> 
Bow (a parameter which affects the distrbutions made by the fund)<br /> 
Yield<br /> 
Net asset value (=0 for new funds)<br /> 
Last distribution (=0 for new funds. If the fund's vintage year has passed, input last year's distribution)<br /> 
Final capital call (FCC) which the amount of capital the fund will call from its committed capital as a percentage<br /> 

Run functions first, then the TA_model_class then the sandbox. 

**Note on the growth series:**<br /> 
To calculate the yearly growth series, a Student's t-distribution is used with df=3. 250 values are produced (daily returns, because there are 250
working days in the year) this is then truncated at 5% on each tail. Then the returns are scaled to have a mean of 8% and a std of 0.2/sqrt(250) to 
model the public equity returns. We then scale the these values depending on the asset class: asset class return = beta * public equity return + alpha. 
Then we return a growth factor for the whole year. <br /> 
It would be good to use a multivariable distribution to model the growth parameters instead to take into account the correlation between asset classes, but this was not done in this programme.
