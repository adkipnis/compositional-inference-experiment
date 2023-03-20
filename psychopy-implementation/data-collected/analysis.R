#================================================#
#           Alteration Magic Analysis            #
#================================================#

rm(list = ls())
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
library(stringr)  
library(dplyr)
library(data.table)
library(tidyr)
library(glue)

# --- Load data
fnames = list.files(pattern="data",
                    recursive=T,
                    full.names=T)
cueTrials = data.frame()
testTrials = data.frame()
meta = data.frame()

for (fname in fnames) {
  # get ID
  idx = as.integer(str_locate_all(pattern = "id=", fname)[[1]][,2])
  id = substr(fname, start=idx+1, stop=idx+2)
  
  # read file
  tmp = read.csv(fname, header=T)
  
  
  # case: participant data
  if (grepl("meta", fname, fixed=T)){
    tmp = transpose(tmp)
    names(tmp) = tmp[1,]
    tmp = tmp[-1,]
    tmp = cbind(id=id, tmp)
    meta = bind_rows(meta, tmp)
    
  # case: performance data
  } else {
    n = nrow(tmp)
    tmp$id = rep(id, nrow(tmp))
    tmp$trialNum = seq(1, n)
    
    # case: cue memory data
    if (tmp["trial_type"][1,] == "cue_memory"){
      cueTrials = bind_rows(cueTrials, tmp)
      
    # case: test data
    } else {
      tmp$target = as.character(tmp$target)
      tmp$resp_options_0 = as.character(tmp$resp_options_0)
      tmp$resp_options_1 = as.character(tmp$resp_options_1)
      tmp$resp_options_2 = as.character(tmp$resp_options_2)
      tmp$resp_options_3 = as.character(tmp$resp_options_3)
      testTrials = bind_rows(testTrials, tmp)
    }
  }
}



