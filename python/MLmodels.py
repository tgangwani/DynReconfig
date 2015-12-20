#!/usr/bin/env python

import os
import numpy as np
import tensorflow as tf

# options for each label - hardcoded!
labelOpts = 3
logDir = "/Users/tanmaygangwani/Desktop/CS446/Project/arch//code/scripts/tensorboardOut/"

class softmax():
  def __init__(self, importantFeatureLocs, identifier):
    self.identifier = identifier # [int] to identify model 
    self.importantFeatureLocs = importantFeatureLocs[:]  # copy (unordered) list
    self.inputVecSize = len(importantFeatureLocs)
    self.uniqueVals = list() # list of unique label values
    self.iterations = 5000 # for stochastic training
    self.batch_size = 500 # for stochastic training
    self.x = tf.placeholder(tf.float32, [None, self.inputVecSize])
    self.W = tf.Variable(tf.zeros([self.inputVecSize, labelOpts]))
    self.b = tf.Variable(tf.zeros([labelOpts]))
    self.y = tf.nn.softmax(tf.matmul(self.x, self.W) + self.b)
    self.y_ = tf.placeholder(tf.float32, [None, labelOpts])

    self.cross_entropy = -tf.reduce_sum(self.y_*tf.log(self.y))
    self.regularization = tf.nn.l2_loss(self.W)
    self.loss = self.cross_entropy + self.regularization 
    
    self.train_step = tf.train.GradientDescentOptimizer(0.001).minimize(self.loss)
    self.sess = tf.Session()

    # summary op
    self.ce_sum = tf.scalar_summary("loss", self.loss)
    #tf.histogram_summary("weights", self.W)
    #tf.histogram_summary("biases", self.b)
    
    # tensor-flow summary
    # we can't do a tf.merge_all_summaries() here because it will add summaries
    # from other softmax objects also. We just need the local summaries
    self.summary_op = self.ce_sum
    tensorboardOut = logDir + str(self.identifier)
    if not os.path.exists(tensorboardOut):
      os.makedirs(tensorboardOut)
    self.summary_writer = tf.train.SummaryWriter(tensorboardOut, graph_def=self.sess.graph_def)
    
    self.init = tf.initialize_all_variables()
    self.sess.run(self.init)

  def train(self, x_data, y_data):
    
    # y_data is a single column. It needs to be converted into a one-hot vector
    # (y_data_oh). A one-hot vector is a vector which is 0 in most dimensions, 
    # and 1 in a single dimension
    y_data_oh = list(list())
    self.uniqueVals = sorted(list(set(y_data)))
    assert len(self.uniqueVals) == labelOpts

    for data in y_data:
      one_hot_entry = [int(data == self.uniqueVals[i]) for i in range(labelOpts)]
      y_data_oh.append(one_hot_entry)

    # one-hot vector
    y_data_oh = np.asarray(y_data_oh)

    # checks
    # make sure we have enough input data to form a batch 
    assert y_data_oh.shape[0] >= self.batch_size
    assert y_data_oh.shape[0] == x_data.shape[0]

    # using small batches of random data - stochastic training
    for i in range(self.iterations):
      sampleIds = np.random.choice(np.arange(y_data_oh.shape[0]), self.batch_size, replace=False)
      x_sampled = np.take(x_data, sampleIds, axis=0)
      y_sampled = np.take(y_data_oh, sampleIds, axis=0)

      # periodic sampling (for stats)
      if (i % 10 == 0):
        # cross-entropy measurement on the whole training data
        summary_str = self.sess.run(self.summary_op, feed_dict={self.x: x_data,
          self.y_: y_data_oh})
        self.summary_writer.add_summary(summary_str, i) 
      else:
        self.sess.run(self.train_step, feed_dict={self.x: x_sampled, self.y_: y_sampled})

    # get a measure of how well we did on the training data. COLT tells us that
    # this is good for generalization
    correct_prediction = tf.equal(tf.argmax(self.y, 1), tf.argmax(self.y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
    print('Accuracy:', self.sess.run(accuracy, feed_dict={self.x: x_data,
      self.y_: y_data_oh}))

  def getLabelPrediction(self, x_test):
    # feature selection using previously saved important locations
    x_test_reduced = np.take(x_test, self.importantFeatureLocs, axis=1)

    # 'labelOpts' x '#samples' matrix
    labelWeights = self.sess.run(self.y, feed_dict={self.x: x_test_reduced})

    # find the corresponding label using the uniqueVals list and return values
    # for all samples
    maxLabelIndices = np.argmax(labelWeights, axis=1)
    maxLabels = [self.uniqueVals[i] for i in maxLabelIndices]
    return np.asarray(maxLabels)

  def getModelParams(self):
    return (self.sess.run(self.W), self.sess.run(self.b))

  def closeSession(self):
    self.sess.close()
