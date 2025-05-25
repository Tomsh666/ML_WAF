from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import pandas as pd

df = pd.read_csv("data/malicious_traffic.csv")

df.fillna('', inplace=True)
y = df['classification']
X = df.drop(columns=['classification'])

label_encoders = {}
for column in X.columns:
    le = LabelEncoder()
    X[column] = le.fit_transform(X[column].astype(str))
    label_encoders[column] = le

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


clf1 = RandomForestClassifier(n_estimators=100, random_state=42)
clf2 = DecisionTreeClassifier(random_state=42)

ensemble = VotingClassifier(estimators=[
    ('rf', clf1),
    ('dt', clf2),
], voting='soft')

ensemble.fit(X_train, y_train)
y_pred = ensemble.predict(X_test)

print("[*] VotingClassifier Ensemble:")
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))


import matplotlib.pyplot as plt
import numpy as np

importances = ensemble.estimators_[0].feature_importances_  # берем importance у RandomForest внутри ансамбля
indices = np.argsort(importances)[::-1]
feature_names = X.columns

plt.figure(figsize=(10, 6))
plt.title("Важность признаков (RandomForest в ансамбле)")
plt.bar(range(len(feature_names)), importances[indices], align="center")
plt.xticks(range(len(feature_names)), feature_names[indices], rotation=45)
plt.tight_layout()
plt.show()


import seaborn as sns
from sklearn.metrics import confusion_matrix

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=np.unique(y), yticklabels=np.unique(y))
plt.xlabel("Предсказанный класс")
plt.ylabel("Истинный класс")
plt.title("Confusion Matrix")
plt.show()


plt.figure(figsize=(10,4))

plt.subplot(1,2,1)
y_train.value_counts().sort_index().plot(kind='bar')
plt.title("Распределение классов в тренировочном наборе")
plt.xlabel("Класс")
plt.ylabel("Количество")

plt.subplot(1,2,2)
y_test.value_counts().sort_index().plot(kind='bar')
plt.title("Распределение классов в тестовом наборе")
plt.xlabel("Класс")
plt.ylabel("Количество")

plt.tight_layout()
plt.show()