
"""
Starter training pipeline for AgroReach.
This script expects a CSV of real farm-season records with measured yield labels.
Do not train on demo/synthetic records or on the Kaggle AgroPredict data and describe
the resulting model as locally validated.
"""
import os
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit

DATA_PATH = "data/farm_season_training_data.csv"
MODEL_PATH = "models/agroreach_yield_model.joblib"
TARGET = "Actual_Yield_tonnes_per_hectare"
GROUP = "Farm_ID"

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Create {DATA_PATH} using real farm-season records first.")

df = pd.read_csv(DATA_PATH)
required = [TARGET, GROUP, "Crop", "LGA", "Farm_Size_ha", "Soil_pH",
            "Rainfall_Total_mm", "Temperature_Mean_C", "Fertilizer_Product",
            "Fertilizer_Rate_kg_per_ha", "Row_Spacing_cm", "Plant_Spacing_cm",
            "Irrigation"]
missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError("Missing required columns: " + ", ".join(missing))

df = df.dropna(subset=[TARGET, GROUP])
if len(df) < 50:
    raise ValueError("At least 50 usable records are required for this starter experiment; more diverse multi-season data is strongly preferred.")

features = [c for c in required if c not in [TARGET, GROUP]]
X, y, groups = df[features], df[TARGET], df[GROUP]

# Split by farm to reduce leakage from the same farm appearing in train and test.
splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(splitter.split(X, y, groups=groups))
X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

categorical = X.select_dtypes(include=["object", "bool"]).columns.tolist()
numeric = [c for c in features if c not in categorical]

numeric_pipe = Pipeline([("imputer", SimpleImputer(strategy="median")),
                         ("scale", StandardScaler())])
categorical_pipe = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                             ("encode", OneHotEncoder(handle_unknown="ignore"))])
preprocess = ColumnTransformer([("num", numeric_pipe, numeric),
                                ("cat", categorical_pipe, categorical)])

model = Pipeline([("preprocess", preprocess),
                  ("regressor", RandomForestRegressor(n_estimators=300, min_samples_leaf=2,
                                                       random_state=42, n_jobs=-1))])
model.fit(X_train, y_train)
pred = model.predict(X_test)

print("Held-out farm evaluation")
print(f"MAE:  {mean_absolute_error(y_test, pred):.3f} tonnes/ha")
print(f"RMSE: {mean_squared_error(y_test, pred)**0.5:.3f} tonnes/ha")
print(f"R2:   {r2_score(y_test, pred):.3f}")

os.makedirs("models", exist_ok=True)
joblib.dump({"pipeline": model, "features": features, "target": TARGET}, MODEL_PATH)
print(f"Saved model: {MODEL_PATH}")
