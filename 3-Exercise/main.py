#! /usr/bin/env python3
#-*- coding:utf-8 -*-
import random
import scipy.sparse as sp
import pandas as pd
import numpy as np
import math
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

vocab_size = 141144
class_count = 29
rows = 70703

def read_data():
    classes = []
    docs = []

    with open("BaseReuters-29", "r") as f:
        content = f.readlines()
        for line in content:
            dico = {}
            words = line.split(' ')
            words.pop() # remove '\n' at the end
            classes.append(int(words.pop(0))-1)
            for word in words:
                val = word.split(':')
                dico[int(val[0])-1] = int(val[1])
            docs.append(dico)
    return classes, docs


def count_documents(train_classes):
    return [train_classes.count(x) for x in range(class_count)]


def train_multinomial(values, classes):
    m = len(values)
    counts = count_documents(classes)

    D = np.zeros(class_count)
    Pi = np.zeros(class_count)
    tf = np.zeros((class_count, vocab_size))
    PC = np.zeros((class_count, vocab_size))

    for k in range(class_count):
        Pi[k] = counts[k]/m

    for k, doc in zip(classes, values):
        for i in doc:
            tf[k][i] += doc[i]
            D[k] += tf[k][i]

    for k in range(class_count):
        for i in range(vocab_size):
            PC[k][i] = (tf[k][i] + 1)/(D[k] + vocab_size)

    return Pi, PC


def test_multinomial():
    return



if __name__=="__main__":
    print("Reading data")
    classes, docs = read_data()

    # We randomly split the dataset using sklearn.train_test_split
    print("Splitting dataset")
    train_size = 52500
    test_size = 18203
    train_values, test_values, train_classes, test_classes = train_test_split(docs, classes, train_size = train_size, test_size = test_size, random_state = 1)

    #  class_term_frequency = [[[0, 0] for i in range(vocab_size)] for j in range(class_count)]
    #  class_doc_frequency = [0 for i in range(class_count)]

    # We store the number of documents in each class containing each term in [0]
    # We store the sum of term frequency for all documents in each class in [1]
    #  cx = train_values.tocoo()
    #  for i, j, v in zip(cx.row, cx.col, cx.data):
    #      class_term_frequency[classes[i] - 1][j][0] += 1
    #      class_term_frequency[classes[i] - 1][j][1] += v

    print("Size :", (rows, vocab_size))
    print("Number of documents per class :")
    
    i = 1
    for elt in count_documents(classes):
        print("Class", i, ":", elt, "documents")
        i += 1

    # computation of the class_doc_frequency (on the training set)
    #  class_doc_frequency = [train_classes.count(x) for x in range(1, class_count+1)]

    print("Training multinomial model")
    Pi, PC = train_multinomial(train_values, train_classes)
    exit()



    ##### TRAINING #####

    # theta_m[k][i] contains the theta of the term t_i in the class k
    theta_m = [[0 for i in range(vocab_size)] for j in range(class_count)]
    theta_b = [[0 for i in range(vocab_size)] for j in range(class_count)]

    for k in range(len(class_term_frequency)):
        # count the total number of words
        total = 0
        for elt in class_term_frequency[k]:
            total += elt[1]

        # compute the frequency of term i divided by the total, for this class k
        no_word_value_m = 1 / (total + vocab_size)
        no_word_value_b = 1 / (class_doc_frequency[k] + 2)
        for i in range(len(class_term_frequency[k])):
            val = class_term_frequency[k][i][1]
            if val == 0:
                theta_m[k][i] = no_word_value_m
                theta_b[k][i] = no_word_value_b
            else:
                theta_m[k][i] = (class_term_frequency[k][i][1] + 1) / (total + vocab_size)
                theta_b[k][i] = (class_term_frequency[k][i][0] + 1) / (class_doc_frequency[k] + 2)

    # computation of the pi_k
    pi_k = [c / train_size for c in class_doc_frequency]
    prediction = [0 for x in range(test_size)]
    pif = [0 for x in range(class_count)]


    ##### TESTING #####

    #  algo = "BERNOULLI"
    algo = "MULTINOMIAL"

    if algo == "BERNOULLI":

        for i in range(test_size):
            max_pif = [0, 0]
            for k in range(class_count):
                pif[k] = math.log1p(pi_k[k])
                for j in range(vocab_size):
                    if test_values[i, j] != 0.0:
                        pif[k] += math.log1p(theta_b[k][j])
                    else:
                        pif[k] += math.log1p(1 - theta_b[k][j])
                if max_pif[0] < pif[k]:
                    max_pif[0] = pif[k]
                    max_pif[1] = k + 1
            prediction[i] = max_pif[1]
            break

    elif algo == "MULTINOMIAL":

        for i in range(test_size):
            print(i)
            max_pif = [0, 0]
            pif = 0.0
            for k in range(class_count):
                pif = math.log1p(pi_k[k])
                m = test_values.getrow(i).tocoo()
                for j, v in zip(m.col, m.data):
                    pif += v * math.log1p(theta_m[k][i])

                if max_pif[0] < pif:
                    max_pif[0] = pif
                    max_pif[1] = k + 1
            prediction[i] = max_pif[1]



    print("Correctly classified samples : %.2f" % accuracy_score(prediction, test_classes))
