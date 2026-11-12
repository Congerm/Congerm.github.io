library(forecast)
d <- read.csv("DATA/CompanyGrowth.csv")
d <- d[order(d$Year, d$Qrtr), ]
cat("rows:", nrow(d), " years:", min(d$Year), "-", max(d$Year), "\n")
cat("2025 rows:", sum(d$Year >= 2025), "\n")

X <- model.matrix(~ Income + Production + Savings + Unemployment, data = d)[, -1]
tr <- d$Year < 2025
y_tr <- ts(d$PctGrowth[tr], frequency = 4, start = c(1976, 1))

# ---- Baseline MLR (trained through 2024) ----
lm_tr <- lm(PctGrowth ~ Income + Production + Savings + Unemployment, data = d[tr, ])
cat("\n== MLR ==\n")
cat("R2:", summary(lm_tr)$r.squared, " adjR2:", summary(lm_tr)$adj.r.squared,
    " sigma:", summary(lm_tr)$sigma, "\n")
print(round(confint(lm_tr), 3))
lm_2025 <- predict(lm_tr, newdata = d[!tr, ], interval = "prediction")
cat("2025 preds:"); print(round(lm_2025, 3))

# ---- Alt 1: regression with ARIMA errors ----
arima_x <- auto.arima(y = y_tr, xreg = X[tr, ])
cat("\n== ARIMA+xreg ==\n"); print(arima_x)
ax_2025 <- forecast(arima_x, xreg = X[!tr, ], level = 95)
cat("2025 preds:"); print(round(ax_2025$mean, 3))
cat("xreg coefs:"); print(round(coef(arima_x)[colnames(X)], 3))

# ---- Alt 2: pure (S)ARIMA on growth ----
arima_p <- auto.arima(y = y_tr)
cat("\n== pure ARIMA ==\n"); print(arima_p)
ap_2025 <- forecast(arima_p, h = 4, level = 95)
cat("2025 preds:"); print(round(ap_2025$mean, 3))

# ---- Holdout: train <=2022, test 2023-2024 ----
h <- d$Year < 2023
nh <- sum(!h)
lm_h <- lm(PctGrowth ~ Income + Production + Savings + Unemployment, data = d[h, ])
p_lm <- predict(lm_h, newdata = d[!h, ])
ax_h <- Arima(ts(d$PctGrowth[h], frequency = 4, start = c(1976, 1)),
              model = arima_x, xreg = X[h, ])
p_ax <- forecast(ax_h, xreg = X[!h, ])$mean
ap_h <- Arima(ts(d$PctGrowth[h], frequency = 4, start = c(1976, 1)),
              model = arima_p)
p_ap <- forecast(ap_h, h = nh)$mean
rmse <- function(a, p) sqrt(mean((a - p)^2))
cat("\n== holdout RMSE (2023-24, n=", nh, ") ==\n")
cat("MLR:", rmse(d$PctGrowth[!h], p_lm), " ARIMAx:", rmse(d$PctGrowth[!h], as.numeric(p_ax)),
    " pureAR:", rmse(d$PctGrowth[!h], as.numeric(p_ap)), "\n")

# ---- Diagnostics ----
cat("\n== diagnostics ==\n")
cat("MLR resid BP p:", lmtest::bptest(lm_tr)$p.value, "\n")
cat("MLR resid KS p:", ks.test(MASS::stdres(lm_tr), "pnorm")$p.value, "\n")
cat("ARIMAx resid Ljung-Box p:", Box.test(residuals(arima_x), lag = 8, type = "Ljung-Box", fitdf = 4)$p.value, "\n")
cat("pure resid Ljung-Box p:", Box.test(residuals(arima_p), lag = 8, type = "Ljung-Box", fitdf = 3)$p.value, "\n")
