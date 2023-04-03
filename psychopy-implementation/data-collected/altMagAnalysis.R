#================================================#
#           Alteration Magic Analysis            #
#================================================#

rm(list = ls())
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
packages = c("stringr", "dplyr", "tidyr", "forcats", "data.table", "glue",
             "ggplot2", "ggridges", "viridis", "ggnewscale")
lapply(packages, require, character.only=T)

# ==== Load data ===============================================================
fnames = list.files(pattern="data", recursive=T, full.names=T)
cueTrials = data.frame()
testTrials = data.frame()
meta = data.frame()
for (fname in fnames){
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
    # cols_to_remove = grep("duration_", names(tmp))
    # tmp = tmp[, -cols_to_remove]
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
tmp = NULL

# ==== Plotting functions ======================================================
raiseBars = function(df, xvar="", xlabel="", ylabel="", dropLegend=F){
  p = ggplot(df, aes(x=get(xvar), y=mean_rt, fill=factor(acc))) +
    geom_bar(stat="identity", position=position_dodge(), color = "white") +
    geom_errorbar(aes(ymin=mean_rt-sd, ymax=mean_rt+sd),
                  alpha=0.3, linewidth=0.5, width=0.5,
                  position=position_dodge(0.9))+
    geom_text(aes(label = n, y = 0.5),
              position=position_dodge(0.9),
              color="white",
              fontface = "bold") +
    facet_wrap(~id)+
    scale_fill_manual(values = c("darkred", "darkolivegreen4"))+
    scale_x_discrete(expand = c(0, 0)) +
    scale_y_continuous(expand = c(0, 0),
                       breaks = seq(0, 10, 2)) +
    theme_minimal()+
    guides(fill = guide_legend(title = "Accuracy"))+
    xlab(xlabel) +
    ylab(paste(ylabel, "RT [s]")) +
    theme(
      panel.border = element_rect(colour = "gray", fill=NA, size=1),
      axis.text = element_text(size = 10),
      axis.text.y = element_text(vjust = 0, angle = 0), 
      axis.title.x = element_text(margin = margin(t = 20)),
      axis.title.y = element_text(margin = margin(r = 20)),
      axis.title = element_text(size = 14, face = "bold"),
      strip.text.x = element_text(size = 14, face = "bold.italic"),
      panel.spacing = unit(2.5, "lines"),
      legend.margin = margin(0, 5, 0, 20)
    )
  
  if (dropLegend) {
    p = p + theme(legend.position = "none")
  }
  
  return(p)
}

makeWaves = function(dfLong, facetvar="", xlabel="", threshold=2.0){
  p = ggplot(dfLong, aes(y=id)) +
    geom_density_ridges(aes(x = rt, fill = factor(acc)),
                        alpha = .6, color = "white",
                        scale=1.2, rel_min_height=1e-05)+
    geom_vline(xintercept = threshold, linetype="dashed", color = "darkred")

  if (facetvar != "") {
    p = p + facet_wrap(~ get(facetvar))
  }

  p = p + scale_fill_manual(values=c("darkred", "darkolivegreen4"))+
    scale_x_continuous(expand = c(0, 0), breaks = seq(0, 14, 2)) +
    scale_y_discrete(expand = c(0, 0), limits = rev(unique(sort(dfLong$id)))) +
    coord_cartesian(clip = "off") +
    theme_minimal(base_size = 14) +
    ylab("Subject ID") +
    xlab(paste(xlabel, "RT [s]")) +
    theme(
      panel.border = element_rect(colour = "gray", fill=NA, size=1),
      axis.text = element_text(size = 10),
      axis.text.x = element_text(hjust = 1, angle = 0),
      axis.text.y = element_text(vjust = 0, angle = 45),
      axis.title.x = element_text(margin = margin(t = 20)),
      axis.title.y = element_text(margin = margin(r = 20)),
      axis.title = element_text(size = 14, face = "bold"),
      strip.text.x = element_text(size = 14, face = "bold.italic", vjust = 4,
                                  margin = margin(t = 20)),
      legend.position = "none"
    )
  return(p)
}

cookLasagne = function(dfLong, facetvar="", threshold=2.0){
  p = ggplot(dfLong, aes(x = trialNum, y = id)) +
    geom_raster(aes(fill = rt), data = subset(dfLong, acc == 1), alpha = 0.8) +
    scale_fill_gradientn("1-RT [s]",
                         colors = c("goldenrod", "white", "darkolivegreen4"), 
                         values = c(1.0, threshold/14 + 0.01, threshold/14 - 0.01, 0),
                         breaks = seq(0, 14, 2),
                         limits = c(0,14)) +
    new_scale("fill") +
    geom_raster(aes(fill = rt), data = subset(dfLong, acc == 0)) +
    scale_fill_gradient("0-RT [s]",
                        low = "thistle2", high = "darkred",
                        breaks = seq(0, 14, 2), 
                        limits = c(0,14))
  
  if (facetvar != "") {
    p = p + facet_wrap(~ get(facetvar), nrow = 3, scales = "free_y")
  }
  
  p = p + scale_x_continuous(expand = c(0, 0), breaks = seq(0, 140, 10)) +
    scale_y_discrete(expand = c(0, 0), limits = rev(unique(sort(dfLong$id)))) +
    coord_cartesian(clip = "off") +
    theme_minimal(base_size = 14) +
    xlab("Trial Number") +
    ylab("Subject ID") +
    theme(
      panel.border = element_rect(colour = "gray", fill=NA, size=1),
      axis.text = element_text(size = 10),
      axis.text.x = element_text(hjust = 0.5, angle = 0),
      axis.text.y = element_text(vjust = 0, angle = 45), 
      axis.title.x = element_text(margin = margin(t = 20)),
      axis.title.y = element_text(margin = margin(r = 20)),
      axis.title = element_text(size = 14, face = "bold"),
      legend.title = element_text(size = 14, face = "bold", vjust = 2),
      strip.text.x = element_text(size = 14, face = "bold.italic", vjust = 4,
                                  margin = margin(t = 20)),
    )
  return(p)
}

# ==== Cue Learning ============================================================
# Pre-processing
cueTrials = cueTrials %>% mutate(
  idk = as.integer(is.na(cueTrials$emp_resp_0) | is.na(cueTrials$emp_resp_1)),
  acc = ifelse(idk == 0, correct_resp_0 == emp_resp_0 & correct_resp_1 == emp_resp_1, 0),
  rt = ifelse(is.na(resp_RT_1), resp_RT_0, resp_RT_0 + resp_RT_1)) %>%
  filter(rt <= 15)
# firstModalities = cueTrials %>% filter(trialNum == 1) %>% group_by(id) %>% slice_min(start_time)

# Accuracy analysis
(dfCLAcc = cueTrials %>% group_by(id, cue_type) %>%
  summarize(mean_acc = mean(acc),
            mean_idk = mean(idk)))

#  Bar plot
dfCueLearning = cueTrials %>% group_by(id, acc, cue_type) %>%
  summarize(mean_rt = mean(rt), sd = sd(rt), n=n())
raiseBars(dfCueLearning, "cue_type", "Cue Type", "Mean Cue Memory")

# Ridge plot
makeWaves(cueTrials, "cue_type", "Cue Memory")


# ==== Test Learning ===========================================================
# Pre-processing
testTrials$applicable = NULL
testTrials = testTrials %>%
  mutate(idk = as.integer(is.na(emp_resp)),
         acc = ifelse(idk == 0, correct_resp == emp_resp, 0),
         rt = resp_RT) 

testPracticeTrials = testTrials %>% filter(trial_type == "test_practice") %>%
  mutate(rt = ifelse(rt <= 14.0, rt, NA))

# firstTest = testTrials %>% filter(trialNum == 1) %>%
# group_by(id) %>% slice_min(start_time)


# Accuracy analysis
dfTPAcc = testPracticeTrials %>% group_by(id, test_type) %>%
  summarize(mean_acc = mean(acc),
            mean_idk = mean(idk))


# Bar plot
dfTestPractice = testPracticeTrials %>% filter(!is.na(rt)) %>%
  group_by(id, acc, test_type) %>%
  summarize(mean_rt = mean(rt), sd = sd(rt), n=n())

raiseBars(dfTestPractice, "test_type", "Test Type", "Mean Test", dropLegend=T)


# Ridge plot
makeWaves(testPracticeTrials, "test_type", "Test")


# ==== Cue x Test ==============================================================
# Ridge Plots
testPracticeTrials %>%
  filter(test_type == "position") %>%
  makeWaves("cue_type", "Position Test")

testPracticeTrials %>%
  slice(1) %>% mutate(test_type = "count", id = "02", rt = NA) %>%
  bind_rows(testPracticeTrials) %>% # add row for Subject 02 for comparison
  filter(test_type == "count") %>%
  makeWaves("cue_type", "Count Test")


# Bar Plot
testPracticeTrials %>% filter(!is.na(rt)) %>%
  group_by(id, acc, cue_type) %>%
  summarize(mean_rt = mean(rt), sd = sd(rt), n=n()) %>%
  raiseBars("cue_type", "Cue Type", "Mean Test", dropLegend=T)


# ==== Longitudinal plots ======================================================
# --- Lasagne Plots for Session 1
cueTrials %>% filter(id != "04") %>%
  cookLasagne("cue_type")
cookLasagne(testPracticeTrials, "test_type")

# --- Lasagne Plots for Session 2
# testTrials %>% filter(trial_type == "prim_decoder") %>%
# mutate(rt = ifelse(rt <= 14.0, rt, NA)) %>%
# cookLasagne()

