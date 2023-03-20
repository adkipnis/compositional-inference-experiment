#================================================#
#           Alteration Magic Analysis            #
#================================================#

rm(list = ls())
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
packages = c("dplyr", "tidyr", "data.table", "glue", "ggplot2", "ggridges")
lapply(packages, require, character.only=T)

# ==== Load data ===============================================================
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
    cols_to_remove = grep("duration_", names(tmp))
    tmp = tmp[, -cols_to_remove]
    meta = bind_rows(meta, tmp)
    
  # case: performance data
  } else {
    n = nrow(tmp)
    tmp = cbind(trialNum=seq(1, n), tmp)
    tmp = cbind(id=rep(id, nrow(tmp)), tmp)
    
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
testTrials = testTrials[,-grep("applicable", names(testTrials))]
cueTrials$resp_RT_sum = cueTrials$resp_RT_0 + cueTrials$resp_RT_1

# ==== Preprocessing ===========================================================
# discard participants without session 2

# discard outliers
cueTrials = na.omit(cueTrials[cueTrials$resp_RT_sum <= 15,])

# ==== Main analysis =======================================================
# Cue Learning
ggplot(cueTrials, aes(x=resp_RT_sum, y=id, fill=stat(x))) +
  geom_density_ridges_gradient(scale=1.3, rel_min_height=1e-05)+
  scale_fill_viridis_c(name="Total RT [s]", option="inferno", direction=-1, alpha=0.4)+
  geom_vline(xintercept = 2, linetype="dashed", color = "darkred")+
  facet_wrap(~cue_type)+
  scale_x_continuous(expand = c(0, 0), breaks = seq(0, 14, 2)) +
  scale_y_discrete(expand = c(0, 0)) +
  coord_cartesian(clip = "off") +
  theme_minimal(base_size = 14) +
  ylab("Subject ID") + xlab("Cue Memory RT [s]") +
  theme(
    axis.line = element_line(
      colour = "gray",
      linewidth = 0.5,
      linetype = "solid"
    ),
    axis.text = element_text(size = 10),
    axis.text.x = element_text(hjust = 1, angle = 0),
    axis.text.y = element_text(vjust = 0, angle = 45), 
    axis.title.x = element_text(margin = margin(t = 20)),
    axis.title.y = element_text(margin = margin(r = 20)),
    axis.title = element_text(size = 14, face = "bold"),
    strip.text.x = element_text(size = 14, face = "bold.italic", vjust = 4)
  ) + theme(legend.position = "none")

# bar plot (mean RT + SEM per Person (facet), depending on accuracy (col) and cue_type (x))

# response time distributions (per cue/test type)
# reduction of redundant spells 
