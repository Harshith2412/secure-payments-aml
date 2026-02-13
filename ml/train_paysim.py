import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import RandomForestClassifier

# Download PaySim from Kaggle (manual download) :contentReference[oaicite:5]{index=5}
# Put CSV at: data/paysim.csv

df = pd.read_csv("/Users/harshithmadhavaram/Desktop/secure-payments-aml/PS_20174392719_1491204439457_log.csv")

# Typical PaySim columns: type, amount, oldbalanceOrg, newbalanceOrig, oldbalanceDest, newbalanceDest, isFraud
df["type"] = df["type"].astype("category").cat.codes

y = df["isFraud"].astype(int)
X = df.drop(columns=[c for c in ["isFraud", "isFlaggedFraud"] if c in df.columns])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    n_jobs=-1,
    class_weight="balanced_subsample",
    random_state=42,
)
model.fit(X_train, y_train)

proba = model.predict_proba(X_test)[:, 1]
print("ROC-AUC:", roc_auc_score(y_test, proba))
