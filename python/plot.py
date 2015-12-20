#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np

pred_values = list()
base_values = list()
best_values = list()
pred_base_values = list()
pred_best_values = list()

def plot():

  ind = np.arange(len(pred_base_values))  # the x locations for the groups
  width = 0.25       # the width of the bars

  _, ax = plt.subplots()
  r1 = ax.bar(ind, pred_base_values, width, color='r')
  r2 = ax.bar(ind + width, pred_best_values, width, color='y')

  ax.set_ylim([0,1.4])
  # add some text for labels, title and axes ticks
  ax.set_ylabel('Efficiency Ratio')
  ax.set_title('predConf v. baseConf v. bestConf')
  ax.set_xticks(ind + width)
  labels = ['app'+str(i+1) for i in range(len(pred_values))]
  labels.append('Avg')
  ax.set_xticklabels(labels, rotation=45)
  ax.legend((r1[0], r2[0]), ('predConf/baseConf', 'predConf/bestConf'), loc =
      'best')
  #ax.legend((r1[0], r2[0]), ('predConf/baseConf', 'predConf/bestConf'))
  #autolabel(r1)
  #autolabel(r2)
  
  #_, ax2 = plt.subplots()
  #r3 = ax2.bar(ind, pred_values, width, color='r')
  #r4 = ax2.bar(ind + width, best_values, width, color='y')
  
  #ax2.set_ylabel('Efficiency')
  #ax2.set_title('Predicted v. Best configuration')
  #ax2.set_xticks(ind + width)
  #ax2.set_xticklabels(['app'+str(i+1) for i in range(len(pred_values))])
  #ax2.legend((r3[0], r4[0]), ('Predicted', 'Best'))
  #autolabel(r3)
  #autolabel(r4)

  #def autolabel(rects):
  #    # attach some text labels
  #    for rect in rects:
  #        height = rect.get_height()
  #        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
  #                '%d' % int(height),
  #                ha='center', va='bottom')

  plt.axhline(y=1)
  #plt.show()

def readData():
  all_vals = list()
  for line in open('results.txt'):
    vals = [float(x) for x in line.rstrip('\n').split(',')]
    all_vals.append(vals)

  pred_values.extend([x[0] for x in all_vals])
  base_values.extend([x[1] for x in all_vals])
  best_values.extend([x[2] for x in all_vals])
  pred_base_values.extend([x/y for x,y in zip(pred_values, base_values)])
  pred_best_values.extend([x/y for x,y in zip(pred_values, best_values)])

  print('pred>base:', sum([1 if pred_base_values[x] > 1 else 0 for x in range(len(pred_base_values))]))
  print('pred<base:', sum([1 if pred_base_values[x] < 1 else 0 for x in range(len(pred_base_values))]))
  print('pred=base:', sum([1 if pred_base_values[x] == 1 else 0 for x in range(len(pred_base_values))]))

  print('pred>best:', sum([1 if pred_best_values[x] > 1 else 0 for x in range(len(pred_best_values))]))
  print('pred<best:', sum([1 if pred_best_values[x] < 1 else 0 for x in range(len(pred_best_values))]))
  print('pred=best:', sum([1 if pred_best_values[x] == 1 else 0 for x in range(len(pred_best_values))]))

  print('max pred_base', max(pred_base_values))
  print('max pred_best', max(pred_best_values))

  # add averages to pred_base and pred_best
  pred_base_avg = sum(pred_base_values)/len(pred_base_values)
  pred_best_avg = sum(pred_best_values)/len(pred_best_values)
  pred_base_values.append(pred_base_avg)
  pred_best_values.append(pred_best_avg)
  print('pred_base_avg', pred_base_avg)
  print('pred_best_avg', pred_best_avg)

if __name__=="__main__":
  readData()
  plot()

