library(data.table)

# Clean out tweets from .csv
system("cut -d',' -f1-3 sentiments.txt > sentiments2.txt")

# Read in .csv
dat <- fread('sentiments2.txt')
dat$TimeClean <- as.POSIXct(dat$Time, format="%Y-%m-%d %H:%M:%S")
dat <- subset(dat, nTweets > 5)
#dat <- dat[!is.na(dat$Sentiment),]

# Plot .csv to file
png('sentiments_by_day.png',height=400, width=1200)
plot(dat$TimeClean, dat$Sentiment, type='h', lwd=4, lend=1, cex=0.5, pch=20, ylim=c(-0.5,0.5), #ylim=c(1,1), 
	col=c('goldenrod','darkgrey')[as.numeric(month(dat$TimeClean) %% 2 != 0)+1], 
	main='#phdlife', xlab='Time', ylab='Sentiment')
abline(h=0,lty=2,col='grey')
dev.off()

# Plot sentiment by hour
png('sentiments_by_hour.png', height=600, width=800)
plot(dat$Sentiment ~ jitter(hour(dat$Time),1), pch=20, cex=0.8, main='#phdlife', xlab='Hour', ylab='Sentiment', ylim=c(-1,1))
lines(sort(unique(hour(dat$Time))), by(dat$Sentiment, hour(dat$Time), mean),col='red')
dev.off()

png('sentiments_by_hour_box.png', height=600, width=800)
boxplot(dat$Sentiment ~ hour(dat$Time), col='goldenrod', main='#phdlife', xlab='Hour', ylab='Sentiment', ylim=c(-1,1))
dev.off()
