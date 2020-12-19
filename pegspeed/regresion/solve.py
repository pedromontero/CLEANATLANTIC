import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn import linear_model
import pandas as pd


data = pd.read_csv("./regresion/df_out.csv")  # load data set
X = data.iloc[:, 1].values.reshape(-1, 1)  # values converts it into a numpy array
y = data.iloc[:, 2].values.reshape(-1, 1)  # -1 means that calculate the dimension of rows, but have 1 column



clt = linear_model.LinearRegression()
clt.fit(X, y)
y_pred = clt.predict(X)

print(clt.coef_)
print(clt.intercept_)


plt.scatter(X[:, 0] ,y[:, 0], c='blue')

plt.plot(X[:, 0], y_pred[:, 0], color='blue', linewidth=3)

plt.xticks(())
plt.yticks(())



plt.show()