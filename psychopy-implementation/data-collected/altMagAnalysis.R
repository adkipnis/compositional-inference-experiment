#================================================#
#           Alteration Magic Analysis            #
#================================================#

rm(list = ls())
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
packages = c("stringr", "dplyr", "tidyr", "data.table", "glue", "ggplot2", "ggridges")
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


# ==== Preprocessing ===========================================================
# discard participants without session 2

# add/remove variables
testTrials = testTrials[,-grep("applicable", names(testTrials))]
cueTrials$rt = cueTrials$resp_RT_0 + cueTrials$resp_RT_1
cueTrials$acc = factor(as.integer(cueTrials$correct_resp_0 == cueTrials$emp_resp_0 &
                             cueTrials$correct_resp_1 == cueTrials$emp_resp_1))
testTrials$acc = factor(as.integer(testTrials$correct_resp == testTrials$emp_resp))

# discard outliers
cueTrials = na.omit(cueTrials[cueTrials$rt <= 15,])


# ==== Main analysis =======================================================
# Cue Learning

ggplot(cueTrials, aes(y=id)) +
  geom_density_ridges(aes(x = rt, fill = acc),
                      alpha = .6, color = "white",
                      scale=1.3, rel_min_height=1e-05)+
  geom_vline(xintercept = 2, linetype="dashed", color = "darkred")+
  facet_wrap(~cue_type)+
  scale_fill_manual(values=c("darkred", "darkolivegreen4"))+
  scale_x_continuous(expand = c(0, 0), breaks = seq(0, 14, 2)) +
  scale_y_discrete(expand = c(0, 0), limits = rev(unique(sort(cueTrials$id)))) +
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
    strip.text.x = element_text(size = 14, face = "bold.italic", vjust = 4),
    legend.position = "none"
  )

dfCueLearning = cueTrials %>% group_by(id, acc, cue_type) %>%
  summarize(mean_rt = mean(rt), sd = sd(rt))

ggplot(dfCueLearning, aes(x=cue_type, y=mean_rt, fill=acc)) +
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(aes(ymin=mean_rt-sd, ymax=mean_rt+sd), alpha=0.3, linewidth=0.5, width=0.5, position=position_dodge(0.9))+
  facet_wrap(~id)+
  scale_fill_manual(values=c("darkred", "darkolivegreen4"))+
  scale_x_discrete(expand = c(0, 0)) +
  scale_y_continuous(expand = c(0, 0), breaks = seq(0, 10, 2)) +
  theme_minimal()+
  guides(fill = guide_legend(title = "Accuracy"))+
  xlab("Cue Type") +
  ylab("Mean Cue Memory RT [s]") +
  theme(
    axis.line = element_line(
      colour = "gray",
      linewidth = 0.5,
      linetype = "solid"
    ),
    axis.text = element_text(size = 10),
    axis.text.y = element_text(vjust = 0, angle = 0), 
    axis.title.x = element_text(margin = margin(t = 20)),
    axis.title.y = element_text(margin = margin(r = 20)),
    axis.title = element_text(size = 14, face = "bold"),
    strip.text.x = element_text(size = 14, face = "bold.italic"),
    panel.spacing = unit(2.5, "lines"),
    legend.position = c(0.9, 0.2),
    legend.justification = "right",
    legend.direction = "vertical",
  )

# Test Learning
testPracticeTrials = testTrials %>% filter(trial_type == "test_practice")
testPracticeTrials = testPracticeTrials[testPracticeTrials$resp_RT <= 15,]

ggplot(testPracticeTrials, aes(y=id)) +
  geom_density_ridges(aes(x = resp_RT, fill = acc),
                      alpha = .6, color = "white",
                      scale=1, rel_min_height=1e-05)+
  geom_vline(xintercept = 2, linetype="dashed", color = "darkred")+
  facet_wrap(~test_type)+
  scale_fill_manual(values=c("darkred", "darkolivegreen4"))+
  scale_x_continuous(expand = c(0, 0), breaks = seq(0, 14, 2)) +
  scale_y_discrete(expand = c(0, 0), limits = rev(unique(sort(cueTrials$id)))) +
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
    strip.text.x = element_text(size = 14, face = "bold.italic", vjust = 4),
    legend.position = "none"
  )

dfTestPractice = testPracticeTrials %>% group_by(id, acc, test_type) %>%
  summarize(mean_rt = mean(resp_RT), sd = sd(resp_RT))

ggplot(dfTestPractice, aes(x=test_type, y=mean_rt, fill=acc)) +
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(aes(ymin=mean_rt-sd, ymax=mean_rt+sd), alpha=0.3, linewidth=0.5, width=0.5, position=position_dodge(0.9))+
  facet_wrap(~id)+
  scale_fill_manual(values=c("darkred", "darkolivegreen4"))+
  scale_x_discrete(expand = c(0, 0)) +
  scale_y_continuous(expand = c(0, 0), breaks = seq(0, 10, 2)) +
  theme_minimal()+
  guides(fill = guide_legend(title = "Accuracy"))+
  xlab("Test Type") +
  ylab("Mean Test RT [s]") +
  theme(
    axis.line = element_line(
      colour = "gray",
      linewidth = 0.5,
      linetype = "solid"
    ),
    axis.text = element_text(size = 10),
    axis.text.y = element_text(vjust = 0, angle = 0), 
    axis.title.x = element_text(margin = margin(t = 20)),
    axis.title.y = element_text(margin = margin(r = 20)),
    axis.title = element_text(size = 14, face = "bold"),
    strip.text.x = element_text(size = 14, face = "bold.italic"),
    panel.spacing = unit(2.5, "lines"),
    legend.position = "none"
  )

# response time distributions (per cue/test type)
# reduction of redundant spells 
