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
import json
import uuid
from typing import Optional

import pandas as pd
import requests
import streamlit as st
from streamlit.components.v1 import html
from streamlit_javascript import st_javascript

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


def parse_location_simple(location_str: str) -> dict:
    """Parse location string like 'Sao Paulo (SP)' into city and context."""
    parts = location_str.split(',')
    city_part = parts[0] if parts else ''
    city = city_part.replace('(', '').replace(')', '').strip()
    context = ', '.join(parts[1:]).strip() if len(parts) > 1 else ''
    return {'city': city, 'context': context}


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
# Location Autocomplete Component
# --------------------------------------------------------------------------- #
def location_autocomplete(api_base: str, key: str = None) -> str:
    """Render a modern location autocomplete input with search functionality."""
    component_id = key or str(uuid.uuid4())[:8]
    
    # Load all places for local filtering
    try:
        places_response = requests.get(f"{api_base}/api/recommend/places", timeout=3)
        all_places = places_response.json().get("places", [])
    except:
        all_places = []
    
    places_json = json.dumps(all_places)
    
    html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        * {{ box-sizing: border-box; }}
        .location-autocomplete {{
            position: relative;
            width: 100%;
            max-width: 500px;
        }}
        .location-input {{
            width: 100%;
            padding: 12px 40px 12px 44px;
            font-size: 16px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background: #ffffff;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }}
        .location-input:focus {{
            border-color: #1f77b4;
            box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.15);
        }}
        .location-icon {{
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            pointer-events: none;
            color: #666;
        }}
        .location-dropdown {{
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: #1e1e1e;
            border: 1px solid #444;
            border-top: none;
            border-radius: 0 0 8px 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            max-height: 0;
            overflow: hidden;
            z-index: 100;
        }}
        .location-dropdown.show {{
            max-height: 350px;
            transition: max-height 0.2s ease;
        }}
        .location-suggestion {{
            padding: 12px 16px;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            gap: 4px;
            transition: background 0.15s;
        }}
        .location-suggestion:hover,
        .location-suggestion.highlighted {{
            background: #f0f7ff;
        }}
        .location-suggestion.highlighted {{
            background: #e6f0ff;
        }}
        .location-name {{
            font-weight: 600;
            color: #333;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .location-name .location-icon-small {{
            color: #1f77b4;
        }}
        .location-context {{
            font-size: 13px;
            color: #666;
        }}
        .location-suggestions-container {{
            padding: 5px 0;
        }}
        .location-empty {{
            padding: 20px 16px;
            text-align: center;
            color: #666;
        }}
        .location-loading {{
            padding: 15px 16px;
            text-align: center;
            color: #1f77b4;
        }}
    </style>
</head>
<body>
    <div class="location-autocomplete" id="location-autocomplete-{component_id}">
        <input
            type="text"
            class="location-input"
            id="location-input-{component_id}"
            placeholder="Search for a location..."
            aria-label="Search for a location"
            aria-expanded="false"
            aria-autocomplete="list"
            aria-controls="location-dropdown-{component_id}"
            aria-activedescendant=""
        >
        <span class="location-icon">📍</span>
        
        <div class="location-dropdown" id="location-dropdown-{component_id}" aria-hidden="true">
            <div class="location-suggestions-container" id="location-suggestions-{component_id}"></div>
        </div>
    </div>

    <script>
    (function() {{
        const config = {{
            debounceDelay: 250,
            minQueryLength: 2,
            maxSuggestions: 5
        }};

        const container = document.getElementById('location-autocomplete-{component_id}');
        const input = document.getElementById('location-input-{component_id}');
        const dropdown = document.getElementById('location-dropdown-{component_id}');
        const suggestionsContainer = document.getElementById('location-suggestions-{component_id}');
        
        const allLocations = {places_json};
        let suggestions = [];
        let selectedIndex = -1;
        let isDropdownOpen = false;
        let debounceTimer = null;
        let currentRequestId = 0;

        function handleFocus() {{
            if (allLocations.length > 0) {{
                isDropdownOpen = true;
                dropdown.classList.add('show');
                dropdown.setAttribute('aria-hidden', 'false');
                input.setAttribute('aria-expanded', 'true');
                // Only show all locations if input is empty
                if (input.value.trim() === '') {{
                    showAllLocations();
                }} else {{
                    // Re-run search with current value
                    const query = input.value.trim();
                    if (query.length >= config.minQueryLength) {{
                        searchLocations(query);
                    }}
                }}
            }}
        }}

        function handleBlur() {{
            setTimeout(() => {{
                isDropdownOpen = false;
                dropdown.classList.remove('show');
                dropdown.setAttribute('aria-hidden', 'true');
                input.setAttribute('aria-expanded', 'false');
                input.setAttribute('aria-activedescendant', '');
                selectedIndex = -1;
            }}, 200);
        }}

        function handleClickOutside(e) {{
            if (!container.contains(e.target)) {{
                handleBlur();
            }}
        }}

        function showAllLocations() {{
            if (allLocations.length === 0) {{
                suggestionsContainer.innerHTML = '<div class="location-empty">No locations available</div>';
                return;
            }}
            suggestionsContainer.innerHTML = '';
            allLocations.forEach((loc, idx) => {{
                const item = createSuggestionItem(loc, idx);
                suggestionsContainer.appendChild(item);
            }});
        }}

        function createSuggestionItem(location, index) {{
            const item = document.createElement('div');
            item.className = 'location-suggestion';
            item.setAttribute('role', 'option');
            const itemId = 'location-suggestion-' + component_id + '-' + index;
            item.setAttribute('id', itemId);
            
            if (index === selectedIndex) {{
                item.classList.add('highlighted');
                input.setAttribute('aria-activedescendant', itemId);
            }}
            
            const parsed = parseLocation(location);
            const cityName = parsed.city || location;
            const context = (parsed.state ? parsed.state + ', ' : '') + (parsed.country || '');
            item.innerHTML = '<div class="location-name"><span class="location-icon-small">📍</span>' + cityName + '</div><div class="location-context">' + context + '</div>';
            
            item.addEventListener('click', () => selectSuggestion(index));
            return item;
        }}

        function parseLocation(locationStr) {{
            const parts = locationStr.split(',').map(p => p.trim());
            const cityPart = parts[0] || '';
            const city = cityPart.replace(/\\([^)]*\\)/g, '').trim();
            const state = (cityPart.match(/\\(([^)]+)\\)/) || [])[1] || '';
            const country = parts[1] || '';
            return {{ name: locationStr, city, state, country }};
        }}

        function handleInput() {{
            const query = input.value.trim();
            
            if (query.length < config.minQueryLength) {{
                if (query === '') showAllLocations();
                else suggestionsContainer.innerHTML = '<div class="location-empty">Type 2+ characters to search</div>';
                return;
            }}

            if (debounceTimer) clearTimeout(debounceTimer);
            
            debounceTimer = setTimeout(() => {{
                searchLocations(query);
            }}, config.debounceDelay);
        }}

        function searchLocations(query) {{
            currentRequestId++;
            const reqId = currentRequestId;
            
            const matches = allLocations.filter(loc => 
                loc.toLowerCase().includes(query.toLowerCase())
            );
            
            const sorted = rankByRelevance(matches, query);
            suggestions = sorted.slice(0, config.maxSuggestions);
            
            if (reqId === currentRequestId) {{
                renderSuggestions();
            }}
        }}

        function rankByRelevance(locations, query) {{
            const qLower = query.toLowerCase();
            const qWords = qLower.split(/\\s+/);
            return locations.sort((a, b) => {{
                const aL = a.toLowerCase();
                const bL = b.toLowerCase();
                
                if (aL === qLower) return -1;
                if (bL === qLower) return 1;
                
                if (aL.startsWith(qLower) && !bL.startsWith(qLower)) return -1;
                if (!aL.startsWith(qLower) && bL.startsWith(qLower)) return 1;
                
                const aW = qWords.every(w => aL.includes(w));
                const bW = qWords.every(w => bL.includes(w));
                if (aW && !bW) return -1;
                if (!aW && bW) return 1;
                
                if (a.length < b.length) return -1;
                if (a.length > b.length) return 1;
                return a.localeCompare(b);
            }});
        }}

        function renderSuggestions() {{
            if (suggestions.length === 0) {{
                dropdown.classList.remove('show');
                dropdown.setAttribute('aria-hidden', 'true');
                input.setAttribute('aria-expanded', 'false');
                isDropdownOpen = false;
                return;
            }}
            
            suggestionsContainer.innerHTML = '';
            suggestions.forEach((suggestion, index) => {{
                const item = createSuggestionItem(suggestion, index);
                suggestionsContainer.appendChild(item);
            }});
            
            dropdown.classList.add('show');
            dropdown.setAttribute('aria-hidden', 'false');
            input.setAttribute('aria-expanded', 'true');
            isDropdownOpen = true;
        }}

        function selectSuggestion(index) {{
            if (index >= 0 && index < suggestions.length) {{
                const selected = suggestions[index];
                input.value = selected;
                input.setAttribute('aria-activedescendant', '');
                
                input.dataset.selectedLocation = JSON.stringify({{
                    id: selected,
                    name: selected,
                    parsed: parseLocation(selected)
                }});
                
                // Store in window for Streamlit to read
                window.locationAutocompleteSelected = selected;
                
                handleBlur();
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
        }}

        function handleKeydown(e) {{
            if (!isDropdownOpen) {{
                if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {{
                    handleFocus();
                }}
                return;
            }}

            const suggestionElements = suggestionsContainer.querySelectorAll('.location-suggestion');
            
            switch (e.key) {{
                case 'ArrowDown':
                    e.preventDefault();
                    selectedIndex = Math.min(selectedIndex + 1, suggestionElements.length - 1);
                    updateHighlight();
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    selectedIndex = Math.max(selectedIndex - 1, 0);
                    updateHighlight();
                    break;
                case 'Enter':
                    e.preventDefault();
                    if (selectedIndex >= 0) selectSuggestion(selectedIndex);
                    break;
                case 'Escape':
                    handleBlur();
                    input.value = '';
                    break;
                case 'Tab':
                    handleBlur();
                    break;
            }}
        }}

        function updateHighlight() {{
            const items = suggestionsContainer.querySelectorAll('.location-suggestion');
            items.forEach((el, idx) => {{
                if (idx === selectedIndex) {{
                    el.classList.add('highlighted');
                    el.scrollIntoView({{ block: 'nearest' }});
                }} else {{
                    el.classList.remove('highlighted');
                }}
            }});
            if (selectedIndex >= 0) {{
                input.setAttribute('aria-activedescendant', 'location-suggestion-' + component_id + '-' + selectedIndex);
            }}
        }}

        handleFocus();
        input.addEventListener('blur', handleBlur);
        input.addEventListener('input', handleInput);
        input.addEventListener('keydown', handleKeydown);
        document.addEventListener('click', handleClickOutside);
    }})();
    </script>
</body>
</html>
    """
    
    # Execute the HTML component with auto-height to avoid white bar
    html(html_code, height=None, scrolling=False)
    
    # Streamlit will handle the form submission, so we don't need st_javascript here
    return component_id


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
    
    # Load all places from the database
    all_places = api_places() if api_ok() else []
    
    # Default values
    default_from = "Recife (PE)" if "Recife (PE)" in all_places else (all_places[0] if all_places else "")
    default_to = "Florianopolis (SC)" if "Florianopolis (SC)" in all_places else (all_places[1] if len(all_places) > 1 else "")
    
    with st.form("flight_form"):
        col1, col2 = st.columns(2)
        with col1:
            f_from = st.selectbox("From", all_places, index=all_places.index(default_from) if default_from in all_places else 0)
            f_type = st.selectbox("Flight type", ["firstClass", "economic", "premium"])
            f_time = st.number_input("Duration (hours)", 0.0, 24.0, 1.76)
            f_agency = st.text_input("Agency", "FlyingDrops")
        with col2:
            f_to = st.selectbox("To", all_places, index=all_places.index(default_to) if default_to in all_places else 1)
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
    
    # Place autocomplete with live search using standard Streamlit input
    all_places = api_places() if api_ok() else []
    
    r_place = None
    # Read selected place from session state if it exists
    if 'selected_place' in st.session_state:
        r_place = st.session_state.selected_place
    
    if api_ok() and all_places:
        # Use a text input with session state
        if 'place_search' not in st.session_state:
            st.session_state.place_search = ""
        
        # Show search input
        search_input = st.text_input(
            "Search for a location",
            value=st.session_state.place_search,
            key="place_search_input",
            help="Type to search for a location. Select from suggestions below."
        )
        
        # Filter places as user types
        if search_input and len(search_input) >= 2:
            # Use the backend search endpoint for fuzzy matching
            try:
                search_response = requests.get(
                    f"{API_BASE}/api/recommend/places/search",
                    params={"q": search_input},
                    timeout=3
                )
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    matches = search_data.get("matches", [])
            except:
                # Fallback to simple substring matching if API fails
                search_lower = search_input.lower()
                matches = [p for p in all_places if search_lower in p.lower()]
        else:
            matches = []
        
        # Show matching locations as clickable items
        if matches:
            for match in matches:
                parsed = parse_location_simple(match)
                if st.button(f"📍 {parsed['city']} — {parsed['context']}", key=f"loc_{match}"):
                    # Store the place in a dedicated session key for form submission
                    st.session_state.form_place = match
                    st.session_state.selected_place = match
                    st.session_state.place_search = match
                    st.rerun()
        elif search_input:
            st.warning(f"No locations found for '{search_input}'. Try 'Brasilia' instead of 'Brasillia'.")
        else:
            # Show all locations when input is empty
            st.write("Type to search locations...")
            st.write(f"Available: {', '.join(all_places[:5])}...")
    else:
        st.warning("API not reachable. Please start the backend server.")
    
    # Use the form_place from session state if it exists (set by location selection)
    if 'form_place' in st.session_state:
        r_place = st.session_state.form_place
        st.success(f"Selected: {r_place}")
    
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
        # Debug: Print session state value for troubleshooting
        st.write(f"Debug - form_place from session: {st.session_state.form_place if 'form_place' in st.session_state else 'NOT SET'}")
        
        payload = {}
        # Read place directly from session state to ensure we get the latest value
        if 'form_place' in st.session_state:
            payload["place"] = st.session_state.form_place
            st.write(f"Using place from session: {payload['place']}")
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
