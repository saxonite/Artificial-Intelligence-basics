# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 13:20:13 2017

@author: Alex
"""

import numpy as np           

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
#    print array
    return array

def loadFacit(filename):
    
    facit = np.genfromtxt(filename, dtype=None, delimiter= ' ', usecols=1)
#    print facit
    return facit
    
#calculate the sigmoid
def sigmoid(x):
    return 1/(1+np.exp(-x))

#np.random.seed(1)

#create a random matrix for all the weights
#the values are between 0 and 0.3
syn0 = np.random.random((400,4)) * 0.3  
#==============================================================================  

if __name__ == '__main__':
    
    learning_rate = 0.7
    
    images = loadImages('training.txt')
    facit = loadFacit('training-facit.txt')
    
    #convert to int
    images = images.astype(int)
    facit = facit.astype(int)
    
    #split in training and testing set
    train_images = images[0:(len(images)/3*2)]
    test_images = images[(len(images)/3*2):len(images)]
    
    train_facit = facit[0:(len(facit)/3*2)]
    test_facit = facit[(len(facit)/3*2):len(facit)]
    
    #initialize error
#    error = 0
    count = 0
#    circular_buffer = np.empty((10))
#    error_mean = 1
    #start the learning loop
    while True:
        try:
              
            #get the random seed
            rng_state = np.random.get_state()
            #shuffle the order of the train images
            np.random.shuffle(train_images)
            #set the random seed to the same seed as befor
            np.random.set_state(rng_state)
            #shuffle the train facit in the same way as the train images
            np.random.shuffle(train_facit)
        
            #go trough all the images
            for j in range(0, len(train_images)):  
            
                #flatten the first image
                l0 = train_images[j].flatten()
                l0 = np.divide(l0, float(32))
    #            l0 = np.append(l0, 1)
                        
                #calculate the activation, the sum of all the inputs times the weights
                acti = np.dot(l0, syn0)
    #            print acti
                #put the activation in the sigmoid
                l1 = sigmoid(acti)
    #            print l1
                
                #reshape the arrays so numpy knows how to handle them
                l1 = l1.reshape(1, 4)
                l0 = l0.reshape(1, 400)
                
                #get the expected output and put into an array
                if train_facit[j] == 1:
                    y = np.array([[1],
                                  [0],
                                  [0],
                                  [0]])
                if train_facit[j] == 2:
                    y = np.array([[0],
                                  [1],
                                  [0],
                                  [0]])
                if train_facit[j] == 3:
                    y = np.array([[0],
                                  [0],
                                  [1],
                                  [0]])
                if train_facit[j] == 4:
                    y = np.array([[0],
                                  [0],
                                  [0],
                                  [1]])
                
                #calculate the error             
                l1_error = y.T - l1
    #            print l1_error
                
                #initialize l1_delta
                l1_delta = np.zeros([400, 4])   
                
                #calculate the update values, input * error * learning rate
#                for l in range(0, 4):
#                    for r in range(0, 400):
#                        l1_delta[r, l] = l0[0, r] * l1_error[0, l] * learning_rate 
                        
                l1_delta = np.matmul(l0, l1_error) * learning_rate
                print l1_delta
                
                #add the opdate values to the current weights
                syn0 += l1_delta
                
#                error = np.sum(np.abs(l1_error))
                #print the error every 90 images
#                if(j % 100) == 0:   # Only print the error every 50th image, to save time and limit the amount of output.                 
#                    print 'Error: ', error
    #                print syn0
                count += 1

            test_error = np.empty((1, len(test_images)))
            #go trough all the images
            for r in range(0, len(test_images)):  
            
                #flatten the first image
                l0 = test_images[r].flatten()
                l0 = np.divide(l0, float(32))
        #            l0 = np.append(l0, 1)
                        
                #calculate the activation, the sum of all the inputs times the weights
                acti = np.dot(l0, syn0)
        #            print acti
                #put the activation in the sigmoid
                l1 = sigmoid(acti)
        #            print l1
                
                #reshape the arrays so numpy knows how to handle them
                l1 = l1.reshape(1, 4)
                l0 = l0.reshape(1, 400)
                
                #get the expected output and put into an array
                if test_facit[r] == 1:
                    y = np.array([[1],
                                  [0],
                                  [0],
                                  [0]])
                if test_facit[r] == 2:
                    y = np.array([[0],
                                  [1],
                                  [0],
                                  [0]])
                if test_facit[r] == 3:
                    y = np.array([[0],
                                  [0],
                                  [1],
                                  [0]])
                if test_facit[r] == 4:
                    y = np.array([[0],
                                  [0],
                                  [0],
                                  [1]])
                
                #calculate the error             
                l1_error = y.T - l1
        #            print l1_error
                
                test_error[0, r] = np.sum(np.abs(l1_error))
                
            test_error_mean = np.mean(test_error)
            print test_error_mean
            if test_error_mean < 0.35:
                print test_error_mean
                raise Exception 
                        
        except Exception:
            break
        
    print 'end test'
    print test_error
    print test_error_mean 
    print 'ended training'
    print 'number of iterations: ', count
                    
    
    
    
    