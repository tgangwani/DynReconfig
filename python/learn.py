#!/usr/bin/env python

import sys
import numpy as np
from sklearn import preprocessing
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
import MLmodels

# 5 labels in data
numlabels = 5
reductionMethod = "RF" # RF (random forest) or LDA (linear discriminant analysis)
RFThreshold = 0.9
std_scale = None
# list of objects of type ML model (e.g. softmax)
modelObjs = list()

# indices for important features in the feature vector
importantFeatureLocs = list()

# input data with features reduced using RF 
x_data_rf_reduced = None

# standardizing the columns - mean=0, variance=1
def standardize():
  global std_scale, x_data
  std_scale = preprocessing.StandardScaler().fit(x_data)
  x_data = std_scale.transform(x_data)

def reduceRF(label):
  global x_data_rf_reduced, importantFeatureLocs
  model = ExtraTreesClassifier()
  model.fit(x_data, y_data[:, label])

  # the relative importance of each attribute
  importance = model.feature_importances_
  weight = float(0)
  del importantFeatureLocs[:] # reset
  #print(importance)  

  for ele in np.sort(importance)[::-1]:
    weight += float(ele)
    featureIndex = np.where(importance==ele)
    for loc in featureIndex[0]:
      importantFeatureLocs.append(loc)
  
    if weight > RFThreshold :
      break
  
  # remove duplications
  importantFeatureLocs = list(set(importantFeatureLocs))

  # extracting relevant columns from input data. Note that importantFeatureLocs
  # may be unsorted (since python 'set' is unsorted), so features are extracted
  # in unorderd fashion. This info is stored in the softmax model class
  x_data_rf_reduced = x_data[:, importantFeatureLocs]

# remove duplicate featureVecs
def removeDuplicates():
  global x_data, y_data
  x_data = np.ascontiguousarray(x_data) 
  uniques = np.unique(x_data.view([('', x_data.dtype)]*x_data.shape[1]),
      return_index=True)[1]

  # the list of duplicates is calculated by subtracting the list of uniques
  # from the universe
  duplicates = list(set(list(range(x_data.shape[0]))) - set(uniques))

  print('Removing', len(duplicates), 'duplicates from (', x_data.shape[0], ') input data.')
  x_data = np.delete(x_data, duplicates, axis=0)
  y_data = np.delete(y_data, duplicates, axis=0)

def printModelParams():
  for modelObj in modelObjs:
    w, b = modelObj.getModelParams()
    print(w)
    print(b)
    print('\n')

def testUnseen():
  x_test = np.loadtxt(open('featuresTest.txt'), delimiter=",", skiprows=1, dtype=np.float64)
  # standardize the test
  x_test = std_scale.transform(x_test) 
  y_pred = np.zeros((x_test.shape[0], numlabels), dtype=np.int)

  # fill the prediction array by calling the model for each label separately
  for modelObj in modelObjs:
    index = modelObjs.index(modelObj)
    y_pred[:, index] = modelObj.getLabelPrediction(x_test)

  #np.set_printoptions(threshold=np.nan)
  print(y_pred)

if __name__=="__main__":
  all_data = np.loadtxt(open('features.txt'), delimiter=",", skiprows=1, dtype=np.float64)
  y_data = all_data[:, 0:numlabels]
  x_data = all_data[:, numlabels:]
  
  standardize()
  removeDuplicates()

  for label in range(numlabels):
    # feature reduction (done separately for each feature)
    if reductionMethod == "RF":
      reduceRF(label)
      m = MLmodels.softmax(importantFeatureLocs, label)
      m.train(x_data_rf_reduced, y_data[:, label])
      modelObjs.append(m)
    else:
      print("[LDA] To be implemented")
      sys.exit(1)
      reduceLDA(label)

  #printModelParams()

  # get predictions for unseen samples
  testUnseen()

  # close all TF sessions
  for modelObj in modelObjs:
    modelObj.closeSession()
