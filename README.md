
# AgroReach MVP

**AgroReach** is a web-based, climate-smart agricultural decision-support prototype for smallholder farmers across Nigeria. The initial demonstration focuses on maize production in Zamfara State.

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the app:

```bash
streamlit run app.py
```

## MVP features

- Farmer farm-profile form (location, crop, farm size, soil information, spacing and planned inputs).
- NiMet seasonal outlook page that only displays uploaded, source-attributed records.
- Maize agronomy knowledge base and fertilizer calculator based on a verified rate per hectare.
- Harvest data collection form that calculates actual yield in tonnes/hectare.
- CSV templates for NiMet and agronomy records.
- Clear separation between operational climate information and ML training data.

## Important data requirements

### NiMet outlook

Use the latest applicable NiMet seasonal climate prediction/outlook. Populate `nimet_seasonal_outlook.csv` with verified information and preserve the source, publication date and validity period. The app intentionally contains no invented forecast values.

### Agronomy knowledge base

Extract crop-specific recommendations from the FAO/IITA/NAERLS source documents. Populate `maize_agronomy.csv` with source page references and rates expressed consistently in kg of fertilizer product per hectare. Do not mix nutrient rates (e.g. kg N/ha) with product rates (e.g. kg NPK/ha).

### Yield model

A trustworthy local yield model requires farm-level records with measured harvest quantities. The app records harvest weight and cultivated area and calculates:

`actual yield (tonnes/ha) = harvest weight (kg) / 1000 / cultivated area (ha)`

Collect data across farms and seasons. Include pre-planting features such as location, crop/variety, soil test properties, farm size, planting date, planned fertilizer and spacing. Capture actual fertilizer applied, observed weather and management information separately for later/in-season models. Prevent leakage by only using features available at the prediction time.

The included Kaggle AgroPredict experiment is not treated as a locally validated Zamfara model.

## Deployment on Streamlit Community Cloud

1. Create a GitHub repository and upload `app.py`, `requirements.txt`, `README.md`, `data/` and `models/`.
2. In Streamlit Community Cloud, deploy the repository and select `app.py`.
3. Do not commit private farmer data. For a public demo, use synthetic/demo records only, clearly labelled.
4. Note: the default Streamlit Cloud filesystem may not be persistent. For real multi-user data collection, connect a managed database (e.g. PostgreSQL/Supabase) and add authentication, consent and access controls.

## Current limitations

- Initial crop scope is maize; initial geography is Zamfara.
- No verified NiMet or agronomy values are bundled. Upload the official data before presenting location-specific forecast or fertilizer outputs.
- Yield prediction is not activated until representative, quality-controlled farm-level training data and a validated model are available.
- This is a prototype, not a replacement for extension officers, soil tests or official weather advisories.

## Suggested next development stages

1. Extract and load NiMet and maize agronomy records.
2. Conduct field validation with extension officers and farmers.
3. Collect farm-season records and measured harvest labels.
4. Train and validate a pre-planting yield model; evaluate by held-out farms/seasons.
5. Add secure database, user accounts, audit trail and multi-crop expansion.
