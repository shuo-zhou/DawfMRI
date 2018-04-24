# Tasks Cognitive Atlas
# =========
# Build a dataframe with 3 columns:
# 1. Task label
# 2. Task ID
# 3. Functions, based on CognitiveAtlas
#
# Chris Cox 18/11/2017

task01_labels <- rep('balloon analogue risk task', 13)
task01_id <- rep(1, 13)
task01_functions <- c(
  'risk',
  'punishment processing',
  'loss anticipation',
  'reward anticipation',
  'risk seeking',
  'risk aversion',
  'feedback processing',
  'response execution',
  'pumps average',
  'response selection',
  'pumps average',
  'visual object detection',
  'task difficulty'
)

task02_labels <- rep('Probabilistic classification task', 9)
task02_id <- rep(2, 9)
task02_functions <- c(
  'negative feedback processing',
  'positive feedback processing',
  'reinforcement learning',
  'error detection',
  'visual word recognition',
  'categorization',
  'response execution',
  'response selection',
  'visual form recognition'
)

task03_labels <- rep('deterministic classification', 7)
task03_id <- rep(3, 7)
task03_functions <- c(
  'categorization',
  'response selection',
  'visual word recognition',
  'error detection',
  'response execution',
  'reinforcement learning',
  'visual form recognition'
)

task04_labels <- rep('Mixed event related probe', 1)
task04_id <- rep(4, 1)
task04_functions <- NA

task05_labels <- rep('rhyme verification task', 6)
task05_id <- rep(5, 6)
task05_functions <- c(
  'phonological working memory',
  'visual pseudoword recognition',
  'phonological assembly',
  'lexical retrieval',
  'phonological comparison',
  'visual word recognition'
)

task06_labels <- rep('mixed gambles task', 10)
task06_id <- rep(6, 10)
task06_functions <- c(
  'numerical scale judgment',
  'confidence judgment',
  'risk processing',
  'economic value processing',
  'response execution',
  'response selection',
  'visual number recognition',
  'decision certainty',
  'potential monetary loss',
  'potential monetary reward'
)

task07_labels <- rep('stop signal task with letter naming', 5)
task07_id <- rep(8, 5)
task07_functions <- c(
  'visual letter recognition',
  'response selection',
  'vocal response execution',
  'proactive control',
  'response inhibition'
)
  
task08_labels <- rep('stop signal task with pseudo word naming', 5)
task08_id <- rep(9, 5)
task08_functions <- c(
  'response selection',
  'vocal response execution',
  'proactive control',
  'visual pseudoword recognition',
  'response inhibition'
)
  
task09_labels <- rep('stop signal task', 8)
task09_id <- rep(10, 8)
task09_functions <- c(
  'error detection',
  'auditory tone detection',
  'oddball detection',
  'proactive control',
  'response selection',
  'response execution',
  'visual form recognition',
  'response inhibition'
)
  
task10_labels <- rep('Simon task', 5)
task10_id <- rep(21, 5)
task10_functions <- c(
  'response selection',
  'response execution',
  'visual color discrimination',
  'response conflict',
  'error detection'
)
  
task11_labels <- rep('Eriksen flanker task', 7)
task11_id <- rep(22, 7)
task11_functions <- c(
  'spatial selective attention',
  'response execution',
  'response selection',
  'visual form recognition',
  'error detection',
  'resistance to distractor inference',
  'response conflict'
)

tasks <- data.frame(
  label=c(
    task01_labels,
    task02_labels,
    task03_labels,
    task04_labels,
    task05_labels,
    task06_labels,
    task07_labels,
    task08_labels,
    task09_labels,
    task10_labels,
    task11_labels
  ),
  id=c(
    task01_id,
    task02_id,
    task03_id,
    task04_id,
    task05_id,
    task06_id,
    task07_id,
    task08_id,
    task09_id,
    task10_id,
    task11_id
  ),
  func=c(
    task01_functions,
    task02_functions,
    task03_functions,
    task04_functions,
    task05_functions,
    task06_functions,
    task07_functions,
    task08_functions,
    task09_functions,
    task10_functions,
    task11_functions
  )
)
save('tasks',file = 'tasks_cognitiveatlas.Rdata')
