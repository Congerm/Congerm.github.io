main <- function(n, N, N_Exp) {
  results<-data.frame(n=factor(),
                      N=factor(),
                      exp=integer(),
                      p_vl=numeric(),
                      W=numeric()
                      )
#  sprintf("n=%i, N=%i, N_Exp=%i",n,N,N_Exp)
  for (exp in 1:N_Exp) {
    mean=c()
    for (i in 1:N){
      # Creates n random numbers then saves the mean of that
      mean[i] <- mean(rbinom(n,size,.5))
    }
    # Perform Shapiro test
    shapiro_result <- shapiro.test(mean)
    #saves result
    results<-rbind(results,data.frame(n=n,N=N,exp=exp,p_vl=shapiro_result$p.value,W=shapiro_result$statistic))
  }

  return(results)
}
