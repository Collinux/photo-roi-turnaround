# analysis.r
# Analyzes image metadata from the "popular" section of 500px.com
#
# Collin Guarino
# The University of North Carolina Greensboro - Fall 2017
# License: MIT
#

# Import the data and remove elapsed days greater than 1 year
photos <- read.table("~/dev/py/photo-roi-turnaround/photos.dat", header=T)
photos <- photos[which(photos$Elapsed.Days <= 365),]

# Show a boxplot for the data without outliers
categories <- photos$Category
elapsed <- photos$Elapsed.Days
boxplot(elapsed~categories,
        names=c("Sport", "Journalism", "Landscapes", "Travel"),
        main="Photographs Taken", xlab="Image Category",
        ylab="Days Taken To Upload", outline = F)

# Separate each category into its own vector
sport <- photos[which(photos$Category == "Sport"),]$Elapsed.Days
journalism <- photos[which(photos$Category == "Journalism"),]$Elapsed.Days
landscapes <- photos[which(photos$Category == "Landscapes"),]$Elapsed.Days
travel <- photos[which(photos$Category == "Travel"),]$Elapsed.Days

# Remove outliers from each category
sport <- sport[!sport %in% boxplot.stats(sport)$out]
journalism <- journalism[!journalism %in% boxplot.stats(journalism)$out]
landscapes <- landscapes[!landscapes %in% boxplot.stats(landscapes)$out]
travel <- travel[!travel %in% boxplot.stats(travel)$out]

# Confidence Intervals
t.test(c(sport, journalism, landscapes,travel), conf.level = 1-0.5/4)$conf.int # Across all categories
intervals <- c(t.test(sport)$conf.int, t.test(journalism)$conf.int,
               t.test(landscapes)$conf.int, t.test(travel)$conf.int)
boxplot(intervals, xlab="Days Taken To Upload", horizontal = T)

# Test each hypothesis (4 choose 2 = 6)
wilcox.test(landscapes, sport, alternative = "less")
wilcox.test(landscapes, journalism, alternative = "less")
wilcox.test(landscapes, travel, alternative = "less")

wilcox.test(sport, journalism, alternative = "less")
wilcox.test(sport, travel, alternative = "less")

wilcox.test(journalism, travel, alternative = "less")
