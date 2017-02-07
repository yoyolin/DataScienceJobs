setwd('E:/Codes/PycharmProjects/dataProject/result')
data <- read.csv('parsed_skills_all.csv')


##############################
#clean data
##############################
#re-phrase queries
data <- transform(data, query =  sub('[^[:alpha:]]', '', query))
data[which(data$query  == ''), 'query'] <- 'datascientist'
data[which(data$query == 'machinelearning'), 'query'] <- 'machinelearner'
data[which(data$query == 'analytics'), 'query'] <- 'dataanalyst'

###create valid dummy data
dummy <- data[,-(1:9)]

#combine 'ms'& 'master'
dummy$master <- apply(dummy[,c('master','ms')], 1, max)
dummy <- subset(dummy, select=-ms)

#combine maths
dummy$maths <- apply(dummy[,c('mathematics','math')], 1, max)
dummy <- subset(dummy, select=-c(math,mathematics))

#combine degree
dummy$degree <- abs(dummy$phd*2 - dummy$master)

###delete empty data
data<- data[-which(apply(dummy, 1, sum) < 5),]
dummy <- dummy[-which(apply(dummy, 1, sum) < 5),]

###assign idf value to each term (optional)
n <- sum(dummy)
cal_idf <- function(column){
  df <- sum(column)
  idf <- log10(n/df) + 1
  return(column*idf)
}
dummy <- as.data.frame(sapply(dummy, cal_idf))

###define categories
business <- c("econometrics", "b2b", "communication", "marketing", "project.management")
programming <- c("engineering","computer.science","java","c","software.engineering","ruby","perl","scala","javascript","python")
stat <- c("physics","statistics","maths","bioinformatics","quantitative","statistical","optimization","hypotheses")
statlang <- c("r","sas","matlab","spss", "python")
system <- c("unix","shell")
visualization <- c('tableau', 'visualization', 'web', 'd3', 'javascript')
bigdataskills <- c('distributed', 'big.data', 'spark','hadoop', 'hive', 'nosql','mapreduce', 'zookeeper', 'pig', 'hbase', 'cloud', 'scala', 'mahout')
database <- c('sql', 'database', 'hbase', 'nosql')
ml <- c('machine.learning', 'algorithm', 'predictive.modelling', 'data.mining', 'optimization', 'classification', 'natural.language', 'mahout')

#prepare data for clustering
cluster.data <- data.frame( business = apply (dummy[,business], 1, sum),
                              programming = apply (dummy[, programming], 1, sum),
                              stat = apply (dummy[,stat], 1, sum),
                              statlang = apply (dummy[,statlang], 1, sum),
                              system = apply (dummy[,system], 1, sum),
                              visualization = apply (dummy[,visualization], 1, sum),
                              bigdataskills = apply(dummy[,bigdataskills], 1, sum),
                              database = apply (dummy[,database], 1, sum),
                              ml = apply (dummy[,ml], 1, sum))
cluster.data <- scale(cluster.data)
##########################
#Perform Clustering
#########################

wss <- rep(NA, 15)
for(i in 2:15){
  result <- kmeans(cluster.data, center = i, iter.max = 500)
  wss[(i -1)] <- sum(result$withinss)
}
plot(1:15, wss, type="b", xlab="Num of Clusters", ylab="within groups sum of squares")
cluster <- kmeans(cluster.data, center = 5, iter.max = 500)


#prepare data for review
data.re <- data.frame(data[,1:9],dummy, cluster.data)
data.re$res <- cluster$cluster
write.csv(data.re, 'data.result.1.csv')

result <- data.frame(cluster$centers, size = cluster$size)
query <- unique(data$query)
for( i in query){
  clusterno <- 1:5
  temp = subset(data.re, query == i)
  result[,paste(i)] <- sapply(clusterno, function(x){nrow(subset(temp, temp$res == x))})
}
write.csv(result, 'cluster.summary.1.csv')
