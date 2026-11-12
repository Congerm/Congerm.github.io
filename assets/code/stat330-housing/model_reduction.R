
library(tidyverse)
#library(bestglm)
#library(multcomp)

housing <- drop_na(read_csv("housing2.csv"))

sapply(lapply(housing, unique), length)


full_mod <-lm(SalePrice~ ., data = housing)
base_mod <-lm(SalePrice~ Lot.Area + Full.Bath + Half.Bath + Garage.Cars + Pool.Area + Mo.Sold + Gr.Liv.Area + Bedroom.AbvGr, data = housing)

object <- full_mod
scope <- c(full_mod, base_mod)

reduced_mod <- step(object, scope, scale = 0,
     direction = "both" ,
     trace = 1, keep = NULL, steps = 1000, k = log(2928))

reduced_mod

#Selected by above code

reduced_mod <- lm(SalePrice ~ Lot.Area + Land.Slope + Bldg.Type + Overall.Qual +
    Overall.Cond + Year.Built + Bsmt.Unf.SF + Total.Bsmt.SF +
    X1st.Flr.SF + X2nd.Flr.SF + Bsmt.Full.Bath + Bedroom.AbvGr +
    TotRms.AbvGrd + Fireplaces + Garage.Cars + Garage.Area +
    Garage.Qual + Wood.Deck.SF + Screen.Porch + Misc.Val + Sale.Condition, data = housing)

reduced_mod
