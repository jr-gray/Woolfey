import numpy as np
import pandas as pd
import pickle
from collections import Counter
from sklearn import svm, cross_validation, neighbors, preprocessing
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.cluster import KMeans
import quandl, math
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.naive_bayes import GaussianNB
import datetime
import matplotlib.pyplot as plt
from matplotlib import style

style.use('ggplot')

df = quandl.get("BCHARTS/BITSTAMPUSD")
df['PCT_change'] = (df['Close'] - df['Open']) / df['Open'] * 100.0
df['HL_PCT'] = (df['High'] - df['Low']) / df['Close'] * 100.0

df = df[['Close', 'HL_PCT', 'PCT_change', 'Volume (BTC)']]
forecast_col = 'Close'
df.fillna(value=-99999, inplace=True)
forecast_out = int(math.ceil(0.01 * len(df)))
df['label'] = df[forecast_col].shift(-forecast_out)

X = np.array(df.drop(['label'], 1))
X = preprocessing.scale(X)
X_lately = X[-forecast_out:]
X = X[:-forecast_out]

df.dropna(inplace=True)

y = np.array(df['label'])

X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2)


clf = LinearRegression(n_jobs=-1)
clf.fit(X_train, y_train)

# pickle_in = open('testMachineLearn2.pickle','rb')
# clf = pickle.load(pickle_in)
confidence = clf.score(X_test, y_test)
print(confidence)

forecast_set = clf.predict(X_lately)

# print(forecast_set, confidence, forecast_out)

df['Forecast'] = np.nan
last_date = df.iloc[-1].name
last_unix = last_date.timestamp()
one_day = 86400
next_unix = last_unix + one_day

for i in forecast_set:
    next_date = datetime.datetime.fromtimestamp(next_unix)
    next_unix += 86400
    df.loc[next_date] = [np.nan for _ in range(len(df.columns) - 1)] + [i]

with open('testMachineLearn2.pickle', 'wb') as f:
    pickle.dump(clf, f)


df['Close'].plot()
df['Forecast'].plot()
plt.legend(loc=4)
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()