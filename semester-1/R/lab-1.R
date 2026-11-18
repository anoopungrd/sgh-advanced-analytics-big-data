#Cleaning

rm(list = ls())

#Parameters
sample_size <- 10^3

#Data generation
example_sample <- rnorm(n = sample_size)

#Visualization
hist(x = example_sample, probability = TRUE, col="peachpuff",
     border = "peachpuff",
     breaks = "Scott", xlim = c(-4,4), ylab = "density",
     main = "Example Histogram")
lines(density(x = example_sample, adjust = 1.5),
      col = "steelblue", lwd = 2)
grid(col = "azure", lty = "solid")
