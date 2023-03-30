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


# ==== Cue Learning ============================================================
# Preprocessing
cueTrials$idk = as.integer(is.na(cueTrials$emp_resp_0) | is.na(cueTrials$emp_resp_1))
cueTrials = cueTrials %>% 
  mutate(acc = ifelse(idk == 0, correct_resp_0 == emp_resp_0 & correct_resp_1 == emp_resp_1, 0),
         rt = ifelse(is.na(resp_RT_1), resp_RT_0, resp_RT_0 + resp_RT_1)) %>%
  filter(rt <= 15)

# Ridge plot
ggplot(cueTrials, aes(y=id)) +
  geom_density_ridges(aes(x = rt, fill = factor(acc)),
                      alpha = .6, color = "white",
                      scale=1.2, rel_min_height=1e-05)+
  geom_vline(xintercept = 2, linetype="dashed", color = "darkred")+
  facet_wrap(~cue_type)+
  scale_fill_manual(values=c("darkred", "darkolivegreen4"))+
  scale_x_continuous(expand = c(0, 0), breaks = seq(0, 14, 2)) +
  scale_y_discrete(expand = c(0, 0), limits = rev(unique(sort(cueTrials$id)))) +
  coord_cartesian(clip = "off") +
  theme_minimal(base_size = 14) +
  ylab("Subject ID") + xlab("Cue Memory RT [s]") +
  theme(
    panel.border = element_rect(colour = "gray", fill=NA, size=1),
    axis.text = element_text(size = 10),
    axis.text.x = element_text(hjust = 1, angle = 0),
    axis.text.y = element_text(vjust = 0, angle = 45), 
    axis.title.x = element_text(margin = margin(t = 20)),
    axis.title.y = element_text(margin = margin(r = 20)),
    axis.title = element_text(size = 14, face = "bold"),
    strip.text.x = element_text(size = 14, face = "bold.italic", vjust = 4),
    legend.position = "none"
  )

# Accuracy analysis
dfCLAcc = cueTrials %>% group_by(id, cue_type) %>%
  summarize(mean_acc = mean(acc),
            mean_idk = mean(idk))

# Bar plot
dfCueLearning = cueTrials %>% group_by(id, acc, cue_type) %>%
  summarize(mean_rt = mean(rt), sd = sd(rt), n=n())

ggplot(dfCueLearning, aes(x=cue_type, y=mean_rt, fill=factor(acc))) +
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
  xlab("Cue Type") +
  ylab("Mean Cue Memory RT [s]") +
  theme(
    panel.border = element_rect(colour = "gray", fill=NA, size=1),
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



# ==== Test Learning ===========================================================
testTrials$applicable = NULL
testTrials$idk = as.integer(is.na(testTrials$emp_resp))
testTrials = testTrials %>%
  mutate(acc = ifelse(idk == 0, correct_resp == emp_resp, 0),
         rt = resp_RT) 

testPracticeTrials = testTrials %>% filter(trial_type == "test_practice", rt <= 15)

ggplot(testPracticeTrials, aes(y=id)) +
  geom_density_ridges(aes(x = resp_RT, fill = factor(acc)),
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
    panel.border = element_rect(colour = "gray", fill=NA, size=1),
    axis.text = element_text(size = 10),
    axis.text.x = element_text(hjust = 1, angle = 0),
    axis.text.y = element_text(vjust = 0, angle = 45), 
    axis.title.x = element_text(margin = margin(t = 20)),
    axis.title.y = element_text(margin = margin(r = 20)),
    axis.title = element_text(size = 14, face = "bold"),
    strip.text.x = element_text(size = 14, face = "bold.italic", vjust = 4),
    legend.position = "none"
  )


# Accuracy analysis
dfTPAcc = testPracticeTrials %>% group_by(id, test_type) %>%
  summarize(mean_acc = mean(acc),
            mean_idk = mean(idk))

# Bar plot
dfTestPractice = testPracticeTrials %>% group_by(id, acc, test_type) %>%
  summarize(mean_rt = mean(resp_RT), sd = sd(resp_RT), n=n())

ggplot(dfTestPractice, aes(x=test_type, y=mean_rt, fill=factor(acc))) +
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(aes(ymin=mean_rt-sd, ymax=mean_rt+sd), alpha=0.2, linewidth=0.5, width=0.5, position=position_dodge(0.9))+
  geom_text(aes(label = n, y = 0.5),
            position=position_dodge(0.9),
            color="white",
            fontface = "bold") +
  facet_wrap(~id)+
  scale_fill_manual(values=c("darkred", "darkolivegreen4"))+
  scale_x_discrete(expand = c(0, 0)) +
  scale_y_continuous(expand = c(0, 0), breaks = seq(0, 10, 2)) +
  theme_minimal()+
  guides(fill = guide_legend(title = "Accuracy"))+
  xlab("Test Type") +
  ylab("Mean Test RT [s]") +
  theme(
    panel.border = element_rect(colour = "gray", fill=NA, size=1),
    axis.text = element_text(size = 10),
    axis.text.y = element_text(vjust = 0, angle = 0), 
    axis.title.x = element_text(margin = margin(t = 20)),
    axis.title.y = element_text(margin = margin(r = 20)),
    axis.title = element_text(size = 14, face = "bold"),
    strip.text.x = element_text(size = 14, face = "bold.italic"),
    panel.spacing = unit(2.5, "lines"),
    legend.position = "none"
  )

# Effect of Cues
testPracticeTrials %>% filter(test_type == "count") %>%
  ggplot(aes(y=id)) +
  geom_density_ridges(aes(x = resp_RT, fill = factor(acc)),
                      alpha = .6, color = "white",
                      scale=1, rel_min_height=1e-05)+
  geom_vline(xintercept = 2, linetype="dashed", color = "darkred")+
  facet_wrap(~cue_type)+
  scale_fill_manual(values=c("darkred", "darkolivegreen4"))+
  scale_x_continuous(expand = c(0, 0), breaks = seq(0, 14, 2)) +
  scale_y_discrete(expand = c(0, 0), limits = rev(unique(sort(cueTrials$id)))) +
  coord_cartesian(clip = "off") +
  theme_minimal(base_size = 14) +
  ylab("Subject ID") + xlab("Test RT for Count trials [s]") +
  theme(
    panel.border = element_rect(colour = "gray", fill=NA, size=1),
    axis.text = element_text(size = 10),
    axis.text.x = element_text(hjust = 1, angle = 0),
    axis.text.y = element_text(vjust = 0, angle = 45), 
    axis.title.x = element_text(margin = margin(t = 20)),
    axis.title.y = element_text(margin = margin(r = 20)),
    axis.title = element_text(size = 14, face = "bold"),
    strip.text.x = element_text(size = 14, face = "bold.italic", vjust = 4),
    legend.position = "none"
  )

testPracticeTrials %>% filter(test_type == "position") %>%
  ggplot(aes(y=id)) +
  geom_density_ridges(aes(x = resp_RT, fill = factor(acc)),
                      alpha = .6, color = "white",
                      scale=1, rel_min_height=1e-05)+
  geom_vline(xintercept = 2, linetype="dashed", color = "darkred")+
  facet_wrap(~cue_type)+
  scale_fill_manual(values=c("darkred", "darkolivegreen4"))+
  scale_x_continuous(expand = c(0, 0), breaks = seq(0, 14, 2)) +
  scale_y_discrete(expand = c(0, 0), limits = rev(unique(sort(cueTrials$id)))) +
  coord_cartesian(clip = "off") +
  theme_minimal(base_size = 14) +
  ylab("Subject ID") + xlab("Test RT for Position trials [s]") +
  theme(
    panel.border = element_rect(colour = "gray", fill=NA, size=1),
    axis.text = element_text(size = 10),
    axis.text.x = element_text(hjust = 1, angle = 0),
    axis.text.y = element_text(vjust = 0, angle = 45), 
    axis.title.x = element_text(margin = margin(t = 20)),
    axis.title.y = element_text(margin = margin(r = 20)),
    axis.title = element_text(size = 14, face = "bold"),
    strip.text.x = element_text(size = 14, face = "bold.italic", vjust = 4),
    legend.position = "none"
  )

# ==== Longitudinal plots ======================================================


# Lasagna Plot
cueTrialsLong = cueTrials %>% filter(id != "04") 
  # mutate(id = fct_reorder(.f = id, .x = trialNum, .fun = max)) %>%
  
ggplot(cueTrialsLong, aes(x = trialNum, y = id)) +
geom_raster(aes(fill = rt), data = subset(cueTrialsLong, acc == 1), alpha = 0.8) +
# scale_fill_gradient("1-RT [s]", breaks = seq(0, 14, 2), 
                       # low = "darkolivegreen4", high = "white") +
scale_fill_gradientn("1-RT [s]",
                     colors = c("goldenrod", "white", "darkolivegreen4"), 
                     values = c(1.0, 2/18 + 0.01, 2/18 - 0.01, 0),
                     breaks = seq(0, 14, 2)) +
new_scale("fill") +
geom_raster(aes(fill = rt), data = subset(cueTrialsLong, acc == 0)) +
scale_fill_gradient("0-RT [s]", breaks = seq(0, 14, 2), 
                       low = "thistle", high = "darkred")+
facet_wrap(~cue_type, nrow = 3, scales = "free_y") +
scale_x_continuous(expand = c(0, 0), breaks = seq(0, 140, 10)) +
scale_y_discrete(expand = c(0, 0), limits = rev(unique(sort(cueTrialsLong$id)))) +
coord_cartesian(clip = "off") +
theme_minimal(base_size = 14) +
ylab("Subject ID") + xlab("Trial Number") +
labs(fill = "RT [s]") +
theme(
  panel.border = element_rect(colour = "gray", fill=NA, size=1),
  axis.text = element_text(size = 10),
  axis.text.x = element_text(hjust = 0.5, angle = 0),
  axis.text.y = element_text(vjust = 0, angle = 45), 
  axis.title.x = element_text(margin = margin(t = 20)),
  axis.title.y = element_text(margin = margin(r = 20)),
  axis.title = element_text(size = 14, face = "bold"),
  legend.title = element_text(size = 14, face = "bold"),
  strip.text.x = element_text(size = 14, face = "bold.italic",
                              vjust = 4, margin = margin(t = 20)),
)

# ==== Session 2 ===============================================================
