import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

print("[*] Загрузка данных...")
data = pd.read_csv("data/csic_database.csv")

assert 'classification' in data.columns, "Ожидается колонка 'classification'"

data.fillna('', inplace=True)

y = data['classification']
data.drop(columns=['Unnamed: 0'], inplace=True)
X = data.drop(columns=['classification'])

label_encoders = {}
for column in X.columns:
    le = LabelEncoder()
    X[column] = le.fit_transform(X[column].astype(str))
    label_encoders[column] = le

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("[*] Classification Report:")
print(classification_report(y_test, y_pred))

print("[*] Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))


import matplotlib.pyplot as plt
import numpy as np

importances = model.feature_importances_
indices = np.argsort(importances)[::-1]
feature_names = X.columns

# Топ-10 признаков
plt.figure(figsize=(10, 6))
plt.title("Важность признаков")
plt.bar(range(10), importances[indices[:10]], align="center")
plt.xticks(range(10), feature_names[indices[:10]], rotation=45)
plt.tight_layout()
plt.show()