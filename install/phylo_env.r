#!/usr/bin/env Rscript

options(repos = c(CRAN = "https://cloud.r-project.org"))

install.packages("remotes")
remotes::install_github("trevorld/r-optparse")
install.packages("phangorn")
install.packages("phytools")
install.packages('codetools')
