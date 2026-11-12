proj1<-function(n, N, N_Exp){

  proj1df<-data.frame(n=factor(),
                      N=factor(),
                      exp=integer(),
                      p_vl=numeric(),
                      W=numeric())

  for (i in N){
    for (x in n){
      value<-main(x,i,N_Exp)
      proj1df<-rbind(proj1df,value)
    }
  }
  #proj1mat<-proj1mat[-1,]


  #names(proj1df)<-c("n","N","Proportion")
  return(proj1df)
}
