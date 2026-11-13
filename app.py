
import os
import io
import json
from datetime import date
import pandas as pd
import streamlit as st
import joblib

st.set_page_config(page_title="AgroReach | Farm Advisory", page_icon="🌱", layout="wide")

# ---------- Theme ----------
st.markdown("""
<style>
:root { --green:#176B45; --light:#EAF5EE; --ink:#18352A; }
.block-container {padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1250px;}
.hero {background:linear-gradient(110deg,#104B35,#21865A);padding:28px 30px;border-radius:18px;color:white;}
.hero h1 {font-size:2.2rem;margin:0 0 8px 0;color:white;}
.hero p {font-size:1rem;margin:0;color:#E7F5EC;}
.small-note {font-size:.83rem;color:#60766A;}
.metric-card {background:#F2F8F4;border:1px solid #DCECE1;padding:15px;border-radius:12px;}
.section-title {color:#176B45;font-weight:700;font-size:1.15rem;margin:10px 0;}
div[data-testid="stMetric"] {background:#F3F8F4;padding:12px;border-radius:12px;border:1px solid #E0EDE3;}
.stButton>button {background:#176B45;color:white;border-radius:9px;border:0;}
.stButton>button:hover {background:#105537;color:white;}
</style>
""", unsafe_allow_html=True)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
CLIMATE_FILE = os.path.join(DATA_DIR, "nimet_seasonal_outlook.csv")
AGR_FILE = os.path.join(DATA_DIR, "maize_agronomy.csv")
RECORD_FILE = os.path.join(DATA_DIR, "farmer_records.csv")
MODEL_FILE = os.path.join("models", "agroreach_yield_model.joblib")

LGAS = ["Anka","Bakura","Birnin Magaji/Kiyaw","Bukkuyum","Bungudu","Gummi","Gusau",
        "Kaura Namoda","Maradun","Maru","Shinkafi","Talata Mafara","Tsafe","Zurmi"]

def load_csv(path, cols):
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception:
            pass
    return pd.DataFrame(columns=cols)

climate_cols = ["LGA","Season_Year","Rainfall_Onset","Rainfall_Cessation","Season_Length_Days",
                "Seasonal_Rainfall_Outlook_mm","Temperature_Outlook_C","Dry_Spell_Risk",
                "Source","Published_Date","Valid_Period"]
agro_cols = ["Crop","Agroecological_Zone","Variety_or_Type","Spacing_Rows_cm","Spacing_Plants_cm",
             "Recommended_Fertilizer","Rate_kg_per_ha","Application_Guidance","Source","Source_Page"]
climate = load_csv(CLIMATE_FILE, climate_cols)
agro = load_csv(AGR_FILE, agro_cols)

st.markdown("""
<div class="hero">
  <h1>🌱 AgroReach</h1>
  <p>AI-powered, climate-smart agricultural decision support for smallholder farmers across Nigeria.</p>
</div>
""", unsafe_allow_html=True)
st.write("")
st.caption("MVP demonstration • Initial focus: maize production in Zamfara State • Web application")

with st.sidebar:
    st.image("https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800", use_container_width=True)
    st.title("AgroReach")
    st.caption("Farm advisory workspace")
    page = st.radio("Navigate", ["Farm assessment", "Climate outlook", "Maize advisory", "Yield model & farm records", "Data administration"])
    st.divider()
    st.caption("Prototype status: climate and agronomy datasets are replaceable using verified source data.")

if page == "Farm assessment":
    st.subheader("Farm assessment")
    st.write("Enter the farmer's planned farm details to generate a tailored advisory summary.")
    with st.form("farm_form"):
        c1,c2,c3 = st.columns(3)
        with c1:
            farmer_code = st.text_input("Farmer code (avoid personal identifiers)", placeholder="e.g. ZAM-F001")
            state = st.selectbox("State", ["Zamfara"])
            lga = st.selectbox("Local Government Area", LGAS)
            community = st.text_input("Community / ward", placeholder="Optional")
        with c2:
            crop = st.selectbox("Crop", ["Maize"])
            variety = st.text_input("Maize variety (if known)", placeholder="e.g. variety name")
            farm_size = st.number_input("Farm size (hectares)", min_value=0.01, value=1.0, step=0.1)
            planting_date = st.date_input("Planned planting date", value=date.today())
        with c3:
            soil_info = st.selectbox("Soil information", ["Not tested / unknown","Sandy","Loamy","Clayey","Silty","Other"])
            irrigation = st.selectbox("Water source", ["Rain-fed","Irrigated","Supplemental irrigation"])
            spacing_rows = st.number_input("Row spacing (cm)", min_value=0, value=75, step=1)
            spacing_plants = st.number_input("Plant spacing (cm)", min_value=0, value=25, step=1)
        st.markdown("**Planned fertilizer information**")
        f1,f2,f3 = st.columns(3)
        with f1:
            fertilizer = st.selectbox("Fertilizer product", ["Not decided","NPK 15:15:15","Urea","Other"])
        with f2:
            planned_qty = st.number_input("Planned quantity (kg)", min_value=0.0, value=0.0, step=5.0)
        with f3:
            applied_status = st.selectbox("Application status", ["Planned only","Already applied"])
        notes = st.text_area("Additional farm information", placeholder="Previous crop, soil test result, pest history, etc.")
        submitted = st.form_submit_button("Generate farm assessment", use_container_width=True)
    if submitted:
        st.session_state["farm"] = {
            "Farmer_Code": farmer_code.strip(), "State":state, "LGA":lga, "Community":community,
            "Crop":crop, "Variety":variety, "Farm_Size_ha":farm_size, "Planting_Date":str(planting_date),
            "Soil_Information":soil_info, "Water_Source":irrigation, "Row_Spacing_cm":spacing_rows,
            "Plant_Spacing_cm":spacing_plants, "Fertilizer_Product":fertilizer,
            "Fertilizer_Quantity_kg":planned_qty, "Fertilizer_Status":applied_status, "Notes":notes
        }
        st.success("Farm assessment captured for this session.")
    farm = st.session_state.get("farm")
    if farm:
        st.markdown("### Assessment summary")
        a,b,c = st.columns(3)
        a.metric("Farm size", f'{farm["Farm_Size_ha"]:.2f} ha')
        b.metric("Crop", farm["Crop"])
        c.metric("Location", farm["LGA"])
        st.info("Your farm profile is ready. Open the Climate outlook and Maize advisory pages for the next steps.")
        st.download_button("Download farm profile (CSV)", pd.DataFrame([farm]).to_csv(index=False), "agroreach_farm_profile.csv", "text/csv")

elif page == "Climate outlook":
    st.subheader("Climate outlook")
    st.write("AgroReach uses NiMet seasonal climate information as an operational input. It is not used as a substitute for historical farm-level training labels.")
    if climate.empty:
        st.warning("No verified NiMet outlook has been loaded yet. This prototype deliberately does not invent rainfall onset, rainfall totals or planting dates.")
        st.markdown("**To activate this section:** upload a NiMet-derived CSV in Data administration. Each row should identify the LGA or applicable climate zone, season year, validity period and source.")
    else:
        lga = st.selectbox("Select LGA", sorted(climate["LGA"].dropna().astype(str).unique()))
        rows = climate[climate["LGA"].astype(str).str.lower() == lga.lower()]
        if rows.empty:
            st.info("No climate record is available for this LGA.")
        else:
            r = rows.iloc[-1]
            st.markdown(f"### {lga} • Season {r.get('Season_Year','')}")
            m1,m2,m3 = st.columns(3)
            m1.metric("Seasonal rainfall outlook", f"{r.get('Seasonal_Rainfall_Outlook_mm','Not supplied')} mm" if pd.notna(r.get('Seasonal_Rainfall_Outlook_mm')) else "Not supplied")
            m2.metric("Season length", f"{r.get('Season_Length_Days','Not supplied')} days" if pd.notna(r.get('Season_Length_Days')) else "Not supplied")
            m3.metric("Dry-spell risk", str(r.get("Dry_Spell_Risk","Not supplied")))
            st.write(f"**Rainfall onset:** {r.get('Rainfall_Onset','Not supplied')}")
            st.write(f"**Rainfall cessation:** {r.get('Rainfall_Cessation','Not supplied')}")
            st.write(f"**Temperature outlook:** {r.get('Temperature_Outlook_C','Not supplied')}")
            st.caption(f"Source: {r.get('Source','Not supplied')} | Published: {r.get('Published_Date','Not supplied')} | Validity: {r.get('Valid_Period','Not supplied')}")
    st.divider()
    st.markdown("**Important:** A seasonal outlook is valid for its stated season and year. Always load the latest applicable NiMet outlook and communicate its validity period.")

elif page == "Maize advisory":
    st.subheader("Maize production advisory")
    farm = st.session_state.get("farm", {})
    lga = farm.get("LGA", LGAS[0])
    size = float(farm.get("Farm_Size_ha", 1.0))
    st.write("Practical guidance is organised around verified agronomic sources. The values below should be populated from the FAO/IITA/NAERLS material you have obtained.")
    if agro.empty:
        st.warning("The maize agronomy knowledge base is not yet populated with source-verified recommendations.")
        st.write("You can still use the assessment checklist below. Do not treat generic values as a locally validated prescription.")
    else:
        crop_rows = agro[agro["Crop"].astype(str).str.lower() == "maize"]
        if crop_rows.empty:
            st.info("No maize recommendation row found in the uploaded agronomy file.")
        else:
            selected = st.selectbox("Agronomy reference", crop_rows.index, format_func=lambda x: str(crop_rows.loc[x].get("Variety_or_Type","Maize recommendation")))
            r = crop_rows.loc[selected]
            st.markdown("### Source-based recommendation")
            st.write(f"**Variety/type:** {r.get('Variety_or_Type','Not supplied')}")
            st.write(f"**Spacing:** {r.get('Spacing_Rows_cm','—')} cm between rows × {r.get('Spacing_Plants_cm','—')} cm between plants")
            st.write(f"**Fertilizer:** {r.get('Recommended_Fertilizer','Not supplied')}")
            rate = pd.to_numeric(r.get("Rate_kg_per_ha"), errors="coerce")
            if pd.notna(rate) and rate > 0:
                st.metric("Calculated fertilizer quantity", f"{rate*size:.1f} kg", f"Based on {rate:g} kg/ha × {size:g} ha")
            else:
                st.info("No verified fertilizer rate is recorded for this recommendation. Quantity calculation is therefore unavailable.")
            st.write(f"**Application guidance:** {r.get('Application_Guidance','Not supplied')}")
            st.caption(f"Source: {r.get('Source','Not supplied')} | Page: {r.get('Source_Page','Not supplied')}")
    st.markdown("### Field management checklist")
    checklist = [
        "Confirm the variety is suitable for the local agroecological zone and season.",
        "Check the latest applicable NiMet seasonal outlook before finalising planting plans.",
        "Use a soil test where possible; soil appearance alone cannot establish nutrient requirements.",
        "Record planting date, seed rate, spacing and actual fertilizer applications.",
        "Scout regularly for weeds, fall armyworm and other crop health problems.",
        "Record harvested grain weight and actual cultivated area after harvest."
    ]
    for item in checklist:
        st.checkbox(item, key="check_"+str(checklist.index(item)))
    st.caption("This checklist is general educational guidance, not a substitute for locally verified extension advice.")

elif page == "Yield model & farm records":
    st.subheader("Yield estimation and farmer data collection")
    st.write("A reliable local yield model must be trained using farm-level inputs linked to measured harvest outcomes. Until those records are available, AgroReach does not claim a validated Zamfara yield prediction.")
    if os.path.exists(MODEL_FILE):
        st.success("A trained model file was found. Confirm that it was trained and evaluated on suitable farm-level data before using its predictions.")
        st.info("Prediction interface is intentionally gated until the model's feature schema and validation report are supplied. This prevents accidental use of an incompatible model.")
    else:
        st.warning("Local yield model: not yet trained. Collect farm records over multiple farms and seasons first.")
    st.markdown("### Record actual harvest after the season")
    farm = st.session_state.get("farm", {})
    with st.form("harvest_form"):
        c1,c2,c3 = st.columns(3)
        with c1:
            code = st.text_input("Farmer / farm code", value=farm.get("Farmer_Code",""))
            season = st.text_input("Season / year", value="2026")
            crop_name = st.text_input("Crop", value=farm.get("Crop","Maize"))
        with c2:
            area = st.number_input("Actual cultivated area (ha)", min_value=0.01, value=float(farm.get("Farm_Size_ha",1.0)))
            harvest_kg = st.number_input("Measured harvested grain (kg)", min_value=0.0, value=0.0, step=50.0)
            harvest_date = st.date_input("Harvest date", value=date.today())
        with c3:
            fertilizer_actual = st.text_input("Fertilizer actually applied", value=farm.get("Fertilizer_Product",""))
            fertilizer_kg = st.number_input("Total fertilizer actually applied (kg)", min_value=0.0, value=0.0, step=5.0)
            weather_notes = st.text_input("Season/weather notes", placeholder="e.g. dry spell, flood, irrigation")
        save = st.form_submit_button("Save harvest record", use_container_width=True)
    if save:
        if harvest_kg <= 0:
            st.error("Enter a measured harvest quantity greater than zero.")
        else:
            record = {
                "Farmer_Code":code,"Season":season,"Crop":crop_name,"Farm_Size_ha":area,
                "Harvest_Quantity_kg":harvest_kg,"Harvest_Date":str(harvest_date),
                "Actual_Yield_tonnes_per_hectare":(harvest_kg/1000)/area,
                "Fertilizer_Actually_Applied":fertilizer_actual,"Fertilizer_Actual_kg":fertilizer_kg,
                "Weather_Notes":weather_notes
            }
            existing = load_csv(RECORD_FILE, list(record.keys()))
            updated = pd.concat([existing, pd.DataFrame([record])], ignore_index=True)
            updated.to_csv(RECORD_FILE, index=False)
            st.success(f"Harvest record saved. Calculated yield: {record['Actual_Yield_tonnes_per_hectare']:.2f} tonnes/ha.")
    records = load_csv(RECORD_FILE, [])
    if not records.empty:
        st.markdown("### Collected harvest records")
        st.dataframe(records.tail(20), use_container_width=True)
        st.download_button("Download all harvest records", records.to_csv(index=False), "agroreach_harvest_records.csv", "text/csv")
    st.markdown("### Model development pathway")
    st.code("Actual_Yield_tonnes_per_hectare = (Harvest_Quantity_kg / 1000) / Farm_Size_ha", language="python")
    st.write("Recommended evaluation: hold out farms or seasons during validation; report MAE, RMSE and R²; compare predictions with actual measured harvests.")

elif page == "Data administration":
    st.subheader("Data administration")
    st.write("Upload structured data extracted from the official NiMet outlook and the FAO/IITA/NAERLS agronomy references. Keep the source and validity information with every record.")
    st.markdown("### 1. NiMet seasonal outlook CSV")
    st.caption("Required columns: " + ", ".join(climate_cols))
    climate_upload = st.file_uploader("Upload NiMet CSV", type=["csv"], key="climate_upload")
    if climate_upload is not None:
        try:
            df = pd.read_csv(climate_upload)
            missing = [c for c in climate_cols if c not in df.columns]
            if missing:
                st.error("Missing columns: " + ", ".join(missing))
            else:
                df.to_csv(CLIMATE_FILE, index=False)
                st.success(f"Loaded {len(df)} climate records.")
                climate = df
        except Exception as e:
            st.error(f"Could not read file: {e}")
    st.download_button("Download NiMet CSV template", pd.DataFrame(columns=climate_cols).to_csv(index=False), "nimet_seasonal_outlook_template.csv", "text/csv")
    st.divider()
    st.markdown("### 2. Verified maize agronomy CSV")
    st.caption("Required columns: " + ", ".join(agro_cols))
    agro_upload = st.file_uploader("Upload agronomy CSV", type=["csv"], key="agro_upload")
    if agro_upload is not None:
        try:
            df = pd.read_csv(agro_upload)
            missing = [c for c in agro_cols if c not in df.columns]
            if missing:
                st.error("Missing columns: " + ", ".join(missing))
            else:
                df.to_csv(AGR_FILE, index=False)
                st.success(f"Loaded {len(df)} agronomy records.")
                agro = df
        except Exception as e:
            st.error(f"Could not read file: {e}")
    st.download_button("Download agronomy CSV template", pd.DataFrame(columns=agro_cols).to_csv(index=False), "maize_agronomy_template.csv", "text/csv")
    st.divider()
    st.markdown("### Data quality and responsible use")
    st.write("- Do not fabricate NiMet values or agronomic rates.")
    st.write("- Keep source title, page number, publication date and validity period.")
    st.write("- SoilGrids values are estimates; soil testing is preferable for nutrient decisions.")
    st.write("- Obtain consent and use non-identifying farmer/farm codes.")
    st.write("- Keep planned fertilizer separate from fertilizer actually applied.")

st.divider()
st.caption("AgroReach MVP • Built for demonstration and iterative validation • No SMS or voice delivery")
