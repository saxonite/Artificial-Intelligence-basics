# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 13:20:13 2017

@author: Alex
"""

import numpy as np
import random

class Perceptron:
    
    def __init__(self, learn_speed, num_weights):
        
        self.speed = learn_speed
        
        self.weights = []
        for x in range(0, num_weights):
            self.weights.append(random.random()*2-1)
            
    def feed_forward(self, inputs):
        summ = 0
        for x in range(0, len(self.weights)):
            summ += self.weights[x] * inputs[x]
        return self.activate(summ)
        
    def activate(self, num):
        if num > 0:
            return 1
        else:
            return -1
            
    def train(self, inputs, desired_output):
        guess = self.feed_forward(inputs)
        error = desired_output - guess

        for x in range(0, len(self.weights)):
            self.weights[x] += error*inputs[x]*self.speed
            

#==============================================================================
def loadImages(filename):

    with open(filename) as f:
        training_data = f.readlines()
    
    array = []
    im = 0
    
    for count, line in enumerate(training_data):
        if line == '\n':
            if count < len(training_data)-20:
                for i in range(0, 20):
                    array = np.append(array, training_data[count+i+2].split())
                im = im + 1
    
    array = np.reshape(array, (im, 20, 20))
    print array
    return array

def loadFacit(filename):
    
    facit = np.genfromtxt(filename, dtype=None, delimiter= ' ', usecols=1)
    print facit
    return facit
    
    
def nonlin(x, deriv=False):  # Note: there is a typo on this line in the video
    if(deriv==True):
        return (x*(1-x))
    
    return 1/(1+np.exp(-x))  # Note: there is a typo on this line in the video

syn0 = 2*np.random.random((400,4)) - 1  # 3x4 matrix of weights ((2 inputs + 1 bias) x 4 nodes in the hidden layer)
syn1 = 2*np.random.random((4,1)) - 1  # 4x1 matrix of weights. (4 nodes x 1 output) - no bias term in the hidden layer.

    
#==============================================================================  

if __name__ == '__main__':
    
    images = loadImages('training.txt')
    facit = loadFacit('training-facit.txt')
    
    train_images = images[0:(len(images)/3*2)]
    test_images = images[(len(images)/3*2):len(images)]
    
    train_facit = facit[0:(len(facit)/3*2)]
    test_facit = facit[(len(facit)/3*2):len(facit)]
    
    for j in range(60000):  
    
        # Calculate forward through the network.
        l0 = train_images
        l1 = nonlin(np.dot(l0, syn0))
        l2 = nonlin(np.dot(l1, syn1))
        
        # Back propagation of errors using the chain rule. 
        l2_error = train_facit - l2
        if(j % 10000) == 0:   # Only print the error every 10000 steps, to save time and limit the amount of output. 
            print("Error: " + str(np.mean(np.abs(l2_error))))
            
        l2_delta = l2_error*nonlin(l2, deriv=True)
        
        l1_error = l2_delta.dot(syn1.T)
        
        l1_delta = l1_error * nonlin(l1,deriv=True)
        
        #update weights (no learning rate term)
        syn1 += l1.T.dot(l2_delta)
        syn0 += l0.T.dot(l1_delta)
    
    print("Output after training")
    print(l2)
    
    
    
    