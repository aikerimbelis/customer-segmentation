# -*- coding: utf-8 -*-
"""MMIS692_Customer_Segmentation_Example.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1-RPT7UuEh-5VdeyggYbtFf6QvP7wMsWn

# MMIS692 Customer Segmentation

Our goal is to classify customers into segments based on input features that represent customer characteristics.
1. We shall train and evaluate candidate classifers using the labeled training samples in the file "*customer_segmentation.train.csv*" through *5-fold cross-validation*, eliminating irrelevant input features if possible.
2. Choose a classifier that performs well, find a good set of hyper-parameters for the classifier through cross-validation, train our model with chosen hyper-parameters on the training examples, and evaluate its classification accuracy on the labeled validation samples in the file "*customer_segmentation.valid.csv*"
3. Use our trained model to classify customers in the file "*customer_segmentation.unlabeled.csv*" into segments, based on their characteristics.

## Import libraries

A list of available *Scikit-Learn* supervised learning classifiers is available at https://scikit-learn.org/stable/supervised_learning.html

Use any classifier that you are familiar with.
"""

import pandas as pd # for data handling
import matplotlib.pyplot as plt # for plotting
from time import time # to record time for training and cross-validation

# scikit-learn classifiers (import other classifiers if you want to)
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import RidgeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier

from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report, confusion_matrix # to evaluate models

from sklearn.model_selection import cross_val_score, GridSearchCV # for cross-validation and tuning hyper-parameters

import warnings
warnings.filterwarnings("ignore") # ignore warnings

from google.colab import drive
drive.mount('/content/drive')

"""## Get data

For this task, we are going to use data from 3 CSV files:
- '*customer_segmentation.train.csv*'
- '*customer_segmentation.valid.csv*'
- '*customer_segmentation.unlabeled.csv*'

"""

! unzip '/content/drive/MyDrive/Colab Notebooks/Data Analytics Project/data.MMIS692.Summer2023 (1).zip'
train = pd.read_csv('customer_segmentation.train.csv')
valid = pd.read_csv('customer_segmentation.valid.csv')
unlabeled = pd.read_csv('customer_segmentation.unlabeled.csv')
! rm *.csv

"""## Specify classifiers
We shall use the following *sklearn* classifiers with default hyper-parameters.

You can use any set of classifiers that you want.
"""

CLF = {} # dictionary of classifiers
CLF['GNB'] = GaussianNB()
CLF['DT'] = DecisionTreeClassifier()
CLF['RF'] = RandomForestClassifier()
CLF['ET'] = ExtraTreesClassifier()
CLF['AB'] =  AdaBoostClassifier()
CLF['SGD'] = SGDClassifier()
CLF['Ridge'] = RidgeClassifier()
CLF['LR'] = LogisticRegression(max_iter=1000)
CLF['Lin_SVC'] = LinearSVC()
CLF['SVC'] = SVC()
CLF['KNN'] = KNeighborsClassifier()
CLF['MLP'] = MLPClassifier()

print('Classifiers:')
for c in CLF:
    print(f'{c} : {CLF[c].__class__.__name__}')

"""## Evaluate classifiers
We shall train the classifiers on all available features using *5 fold cross-validation* on just the training data.
"""

features = list(train)[1:] # input features
res = [] # list with results
for c in CLF: # for each classifier
    model = CLF[c] # create classifier object with default hyper-parameters
    st = time() # start time for 5-fold cross-validation
    score = cross_val_score(model, train[features], train.y).mean() # mean crosss-validation accuracy
    t = time() - st # # time for 5-fold cross-validation
    print(c, round(score,4), round(t,2)) # show results for classifier
    res.append([c, score, t]) # append results for classifier
pd.DataFrame(res, columns=['model', 'score', 'time']).round(4) # show results as dataframe

"""## Eliminate irrelevant features

We shall use the '*feature_importances_*' attribute of a trained *ExtraTreesClassifier* model to estimate the importance of each feature, sort the features based on importance, and check if some of the features seem irrelevant for this classification task.
"""

ET = ExtraTreesClassifier().fit(train[features], train.y) # Train ExtraTreesClassifier
fi = sorted([(imp, f) for imp, f in zip(ET.feature_importances_, features)], reverse=True) # features sorted in descending order of importance
k = 20 # consider the k most important features (change as desired)
plt.figure(figsize=(10, 5)) # size of figure to be displayed
_ = plt.bar([v[1] for v in fi][:k], [v[0] for v in fi][:k]) # plot importance
pd.DataFrame(fi[:k], columns=['importance', 'feature']).round(3).T # show importance

"""We identify a list of *relevant_features* and then use only these relevant features to train models."""

k = 12
relevant_features = [v[1] for v in fi][:k]
print("Relevant features:", ', '.join(relevant_features))

"""## Evaluate models using relevant features"""

res = [] # list with results
for c in CLF: # for each classifier
    model = CLF[c] # create classifier object with default hyper-parameters
    st = time() # start time for 5-fold cross-validation
    score = cross_val_score(model, train[relevant_features], train.y).mean() # mean crosss-validation accuracy
    t = time() - st # # time for 5-fold cross-validation
    print(c, round(score,4), round(t,2)) # show results for classifier
    res.append([c, score, t]) # append results for classifier
res_df = pd.DataFrame(res, columns=['model', 'mean accuracy', 'time']).round(4) # show results as dataframe
res_df.to_csv('cross_validation_results.csv', index=False)
res_df

"""## Choose good model

Based on cross-validation results we shall create a short-list of the best performing models and then use Grid Search to find a good set of hyper-parameters for these models through cross-validation.
"""

# Commented out IPython magic to ensure Python compatibility.
para = {'C':[0.1, 1.0, 5.0, 10.0]}
clf = GridSearchCV(SVC(), para, scoring='accuracy',
                   n_jobs=-1, verbose=1) # grid search model

print(clf) # show model
print()

print("Tuning hyper-parameters ... " )
clf.fit(train[relevant_features], train.y) # tune using 5-fold cross-validation

print()
print("Accuracy: mean +/- 2*standard_dev") # show results
means = clf.cv_results_['mean_test_score']
stds = clf.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, clf.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r"
#             % (mean, std * 2, params))

print("Best parameters:", clf.best_params_)

# Commented out IPython magic to ensure Python compatibility.
para = {'n_neighbors': [3, 5, 7, 9, 11, 13]}
clf = GridSearchCV(KNeighborsClassifier(), para, scoring='accuracy',
                   n_jobs=-1, verbose=1) # grid search model

print(clf) # show model
print()

print("Tuning hyper-parameters ... " )
clf.fit(train[relevant_features], train.y) # tune using 5-fold cross-validation

print()
print("Accuracy: mean +/- 2*standard_dev") # show results
means = clf.cv_results_['mean_test_score']
stds = clf.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, clf.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r"
#             % (mean, std * 2, params))

print("Best parameters:", clf.best_params_)

"""Train the chosen model with desired hyper-parameter values and evaluate it."""

# Commented out IPython magic to ensure Python compatibility.
model = SVC(C=10.0)
print('Chosen classifier:')
print(model)
model.fit(train[relevant_features], train.y)
pred = model.predict(valid[relevant_features]) # predict labels
acc = accuracy_score(valid.y, pred)
print(f'Validation accuracy with chosen classifier = {acc: .4f}')
print()
print("Classification report with chosen classifier:")
print(classification_report(valid.y, pred, digits=3))
print()
print("Precision for class = %d = %4.3f"
#       %(0, precision_score(valid.y, pred, average=None)[0]))
print("Recall for class = %d = %4.3f"
#       %(2, recall_score(valid.y, pred, average=None)[2]))
print('\nConfusion matrix')
cm = pd.DataFrame(confusion_matrix(valid.y, pred))
cm.to_csv("confusion_matrix.csv")
cm

# Commented out IPython magic to ensure Python compatibility.
model = KNeighborsClassifier(n_neighbors=9)
print('Chosen classifier:')
print(model)
model.fit(train[relevant_features], train.y)
pred = model.predict(valid[relevant_features]) # predict labels
acc = accuracy_score(valid.y, pred)
print(f'Validation accuracy with chosen classifier = {acc: .4f}')
print()
print("Classification report with chosen classifier:")
print(classification_report(valid.y, pred, digits=3))
print()
print("Precision for class = %d = %4.3f"
#       %(0, precision_score(valid.y, pred, average=None)[0]))
print("Recall for class = %d = %4.3f"
#       %(2, recall_score(valid.y, pred, average=None)[2]))
print('\nConfusion matrix')
cm = pd.DataFrame(confusion_matrix(valid.y, pred))
cm.to_csv("confusion_matrix.csv")
cm

"""## Predict unlabeled samples"""

unlabeled.head()

predTest = model.predict(unlabeled[relevant_features]) # predict labels for val example
new = pd.DataFrame() # results data frame
new['ID'] = unlabeled.ID
new['predicted'] = predTest # predicted values
new.to_csv("unlabeled.results.csv", index=False) # save results
new

new.predicted.value_counts()