"""Voyage Analytics Streamlit dashboard.

Interactive front-end for the Voyage Analytics MLOps platform. It consumes the
Flask REST API (flight price, gender, hotel recommendations) and renders
insights from the underlying datasets.

Run the API first (python -m api.app), then:

    streamlit run dashboard/app.py

Configuration (via environment variables):
    API_BASE_URL   Base URL of the Flask API (default http://localhost:5000)
    HOTELS_DATA_PATH / USERS_DATA_PATH (optional) for richer local EDA
"""

import os
from typing import Optional

import pandas as pd
import requests
import streamlit as st

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
API_BASE = os.getenv("API_BASE_URL", "http://localhost:5000").rstrip("/")
HOTELS_PATH = os.getenv("HOTELS_DATA_PATH", "artifacts/data/hotels.csv")
USERS_PATH = os.getenv("USERS_DATA_PATH", "artifacts/data/users.csv")
CATALOG_PATH = os.getenv("HOTELS_CATALOG_PATH", "artifacts/hotel_catalog.json")

st.set_page_config(page_title="Voyage Analytics", layout="wide")


def api_ok() -> bool:
    try:
        r = requests.get(f"{API_BASE}/api/health", timeout=3)
        return r.status_code == 200
    except requests.RequestException:
        return False


@st.cache_data(show_spinner=False)
def api_predict_flight(payload: dict) -> dict:
    return requests.post(f"{API_BASE}/api/predict", json=payload, timeout=10).json()


@st.cache_data(show_spinner=False)
def api_predict_gender(payload: dict) -> dict:
    return requests.post(f"{API_BASE}/api/gender/predict", json=payload, timeout=10).json()


@st.cache_data(show_spinner=False)
def api_recommend(payload: dict) -> list:
    r = requests.post(
        f"{API_BASE}/api/recommend/recommendations", json=payload, timeout=10
    )
    return r.json().get("recommendations", [])


@st.cache_data(show_spinner=False)
def api_places() -> list:
    return requests.get(f"{API_BASE}/api/recommend/places", timeout=10).json().get("places", [])


def load_hotels() -> Optional[pd.DataFrame]:
    if os.path.exists(HOTELS_PATH):
        return pd.read_csv(HOTELS_PATH)
    return None


def load_users() -> Optional[pd.DataFrame]:
    if os.path.exists(USERS_PATH):
        return pd.read_csv(USERS_PATH)
    return None


# --------------------------------------------------------------------------- #
# UI Header
# --------------------------------------------------------------------------- #
st.title("Voyage Analytics")
st.caption("Integrating MLOps in Travel — Flight Price, Gender & Hotel Recommendation")

if api_ok():
    st.success(f"API reachable at {API_BASE}")
else:
    st.warning(f"API not reachable at {API_BASE}. Start it with `python -m api.app`.")

# --------------------------------------------------------------------------- #
# Sidebar
# --------------------------------------------------------------------------- #
page = st.sidebar.radio(
    "Navigate",
    ["Flight Price Predictor", "Gender Classifier", "Hotel Recommender", "Insights"],
)

# --------------------------------------------------------------------------- #
# Page 1: Flight Price Predictor
# --------------------------------------------------------------------------- #
if page == "Flight Price Predictor":
    st.header("Flight Price Predictor")
    with st.form("flight_form"):
        col1, col2 = st.columns(2)
        with col1:
            f_from = st.text_input("From", "Recife (PE)")
            f_type = st.selectbox("Flight type", ["firstClass", "economic", "premium"])
            f_time = st.number_input("Duration (hours)", 0.0, 24.0, 1.76)
            f_agency = st.text_input("Agency", "FlyingDrops")
        with col2:
            f_to = st.text_input("To", "Florianopolis (SC)")
            f_date = st.date_input("Flight date")
            f_distance = st.number_input("Distance (km)", 0.0, 20000.0, 676.53)
        submitted = st.form_submit_button("Predict price")

    if submitted:
        payload = {
            "from": f_from,
            "to": f_to,
            "flightType": f_type,
            "agency": f_agency,
            "time": float(f_time),
            "distance": float(f_distance),
            "flight_year": f_date.year,
            "flight_month": f_date.month,
            "flight_day": f_date.day,
            "flight_dayofweek": f_date.weekday(),
        }
        try:
            result = api_predict_flight(payload)
            price = result.get("predicted_price")
            if price is not None:
                st.metric("Predicted flight price", f"${price:,.2f}")
            else:
                st.error(result)
        except Exception as e:
            st.error(f"Prediction failed: {e}")

# --------------------------------------------------------------------------- #
# Page 2: Gender Classifier
# --------------------------------------------------------------------------- #
elif page == "Gender Classifier":
    st.header("Gender Classifier")
    with st.form("gender_form"):
        g_name = st.text_input("Full name", "Robert Braun")
        g_age = st.number_input("Age", 0, 120, 33)
        g_company = st.text_input("Company", "4You")
        submitted = st.form_submit_button("Classify gender")

    if submitted:
        try:
            result = api_predict_gender(
                {"user name": g_name, "age": int(g_age), "company": g_company}
            )
            gender = result.get("gender")
            prob = result.get("probability", 0)
            if gender:
                st.metric("Predicted gender", gender, delta=f"{prob:.1%}")
            else:
                st.error(result)
        except Exception as e:
            st.error(f"Classification failed: {e}")

# --------------------------------------------------------------------------- #
# Page 3: Hotel Recommender
# --------------------------------------------------------------------------- #
elif page == "Hotel Recommender":
    st.header("Hotel Recommender")
    
    # Place autocomplete with live search
    all_places = api_places() if api_ok() else []
    
    # Initialize session state for place input
    if 'place_input' not in st.session_state:
        st.session_state.place_input = ""
    
    # Display matches below the input box
    place_input = st.text_input("Place (type to search)", st.session_state.place_input, key="place_input_widget")
    
    # Update session state when input changes
    if place_input != st.session_state.place_input:
        st.session_state.place_input = place_input
        st.rerun()
    
    # Show matches as user types
    if place_input:
        matches = [p for p in all_places if place_input.lower() in p.lower()]
        if matches:
            st.info(f"Found {len(matches)} match(es):")
            for match in matches:
                st.write(f"• {match}")
        elif api_ok():
            st.warning("Place not in database")
    
    # Final selection after user confirms
    if len(matches) == 1:
        r_place = matches[0]
        st.success(f"Selected: {r_place}")
    elif len(matches) > 1:
        r_place = st.selectbox("Select a place:", matches, key="place_select")
    else:
        r_place = None
    
    with st.form("recommend_form"):
        col1, col2 = st.columns(2)
        with col1:
            r_budget = st.number_input("Max price / night", 0.0, 1000.0, 250.0)
        with col2:
            r_days = st.number_input("Nights (optional)", 0, 30, 3)
            r_company = st.text_input("Company (optional)", "4You")
        r_top = st.slider("Number of results", 1, 10, 5)
        submitted = st.form_submit_button("Get recommendations")

    if submitted:
        payload = {}
        if r_place:
            payload["place"] = r_place
        if r_budget > 0:
            payload["max_price_per_day"] = float(r_budget)
        if r_days > 0:
            payload["days"] = int(r_days)
        if r_company:
            payload["company"] = r_company
        payload["top_n"] = int(r_top)

        try:
            recs = api_recommend(payload)
            if recs:
                st.subheader("Recommended hotels")
                for r in recs:
                    total = f" · Total for stay: ${r['total_cost']:,.2f}" if r.get("total_cost") else ""
                    with st.container(border=True):
                        st.markdown(
                            f"**{r['hotel_name']}** — {r['place']} "
                            f"(${r['price_per_day']:,.2f}/night{total})"
                        )
                        st.progress(r["score"] / 100, text=f"Match score: {r['score']}/100")
                        st.caption(r["reason"])
            else:
                st.info("No recommendations returned.")
        except Exception as e:
            st.error(f"Recommendation failed: {e}")

# --------------------------------------------------------------------------- #
# Page 4: Insights
# --------------------------------------------------------------------------- #
else:
    st.header("Insights & Visualizations")

    hotel_df = load_hotels()
    user_df = load_users()

    if hotel_df is not None and user_df is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Gender distribution")
            st.bar_chart(user_df["gender"].value_counts())
        with col2:
            st.subheader("Bookings by place")
            st.bar_chart(hotel_df["place"].value_counts())

        st.subheader("Hotel price per night")
        price_table = (
            hotel_df.groupby("name")["price"]
            .first()
            .sort_values()
            .reset_index()
        )
        st.bar_chart(price_table.set_index("name"))
    else:
        st.info(
            "Rich local EDA requires the datasets. Set HOTELS_DATA_PATH and "
            "USERS_DATA_PATH (or place hotels.csv/users.csv under artifacts/data/)."
        )
        # Fall back to the tracked catalog for a minimal overview.
        import json

        if os.path.exists(CATALOG_PATH):
            with open(CATALOG_PATH, encoding="utf-8") as f:
                catalog = json.load(f)
            st.subheader("Hotel catalog (price per night)")
            rows = [
                {"hotel": k, "place": v["place"], "price": v["price_per_day"]}
                for k, v in catalog["hotels"].items()
            ]
            st.dataframe(pd.DataFrame(rows))
