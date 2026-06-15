import streamlit as st
import pandas as pd
from supabase import create_client
import requests

st.set_page_config(
    page_title="World Cup Predictions",
    page_icon="🇸🇦",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background: #f8fafc; }

    section[data-testid="stSidebar"] {
        background: #006C35;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label p {
        color: #111827 !important;
        font-weight: 700 !important;
    }

    section[data-testid="stSidebar"] label span {
        color: #111827 !important;
    }

    div[role="radiogroup"] {
        background: white;
        padding: 18px;
        border-radius: 18px;
        border: none;
        box-shadow: 0 6px 18px rgba(0,0,0,0.15);
    }

    div[role="radiogroup"] label {
        margin-bottom: 8px;
    }

    .hero-card {
        background: #006C35;
        padding: 34px;
        border-radius: 28px;
        box-shadow: 0 12px 30px rgba(0, 108, 53, 0.25);
        margin-bottom: 28px;
        color: white;
        border: 1px solid rgba(255,255,255,0.25);
    }

    .hero-logo {
        font-size: 80px;
        margin-bottom: 10px;
    }

    .hero-title {
        color: white;
        font-size: clamp(42px, 4vw, 58px);
        font-weight: 900;
        line-height: 1.1;
        white-space: nowrap;
    }

    .hero-subtitle {
        font-size: 17px;
        color: rgba(255,255,255,0.88);
        margin-bottom: 0;
    }

    h1, h2, h3 {
        color: #064e3b;
    }

    .section-title {
        background: white;
        padding: 20px 24px;
        border-radius: 20px;
        border-left: 8px solid #006C35;
        box-shadow: 0 8px 22px rgba(0,0,0,0.06);
        margin-bottom: 22px;
    }

    .section-title h2 {
        margin: 0;
        color: #064e3b;
    }

    .section-title p {
        margin: 6px 0 0 0;
        color: #6b7280;
    }

    .game-card {
        background: white;
        padding: 24px;
        border-radius: 22px;
        margin-top: 18px;
        margin-bottom: 10px;
        box-shadow: 0 8px 24px rgba(0, 108, 53, 0.10);
        border: 1px solid #d1fae5;
    }

    .match-title {
        font-size: 27px;
        font-weight: 900;
        color: #064e3b;
        margin-bottom: 10px;
    }

    div.stButton > button {
        background: #006C35;
        color: white;
        border-radius: 14px;
        border: none;
        padding: 11px 24px;
        font-weight: 800;
        box-shadow: 0 6px 14px rgba(0, 108, 53, 0.25);
    }

    div.stButton > button:hover {
        background: #006C35;
        color: white;
        border: none;
    }

    div[data-baseweb="select"] > div {
        border-radius: 14px;
        border-color: #a7f3d0;
    }

    div[data-baseweb="select"] {
        color: black !important;
    }

    [data-testid="stDataFrame"] {
        background: white;
        border-radius: 20px;
        padding: 10px;
        box-shadow: 0 8px 24px rgba(0, 108, 53, 0.10);
        border: 1px solid #d1fae5;
    }

    div[data-testid="stAlert"] {
        border-radius: 16px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

FLAGS = {
    "Mexico": "🇲🇽",
    "South Africa": "🇿🇦",
    "South Korea": "🇰🇷",
    "Czechia": "🇨🇿",
    "Canada": "🇨🇦",
    "Bosnia and Herzegovina": "🇧🇦",
    "Qatar": "🇶🇦",
    "Switzerland": "🇨🇭",
    "Brazil": "🇧🇷",
    "Morocco": "🇲🇦",
    "Haiti": "🇭🇹",
    "Scotland": "🏴",
    "United States": "🇺🇸",
    "Paraguay": "🇵🇾",
    "Australia": "🇦🇺",
    "Turkey": "🇹🇷",
    "Germany": "🇩🇪",
    "Curacao": "🇨🇼",
    "Ivory Coast": "🇨🇮",
    "Ecuador": "🇪🇨",
    "Netherlands": "🇳🇱",
    "Japan": "🇯🇵",
    "Sweden": "🇸🇪",
    "Tunisia": "🇹🇳",
    "Belgium": "🇧🇪",
    "Egypt": "🇪🇬",
    "Iran": "🇮🇷",
    "New Zealand": "🇳🇿",
    "Spain": "🇪🇸",
    "Cape Verde": "🇨🇻",
    "Cape Verde Islands": "🇨🇻",
    "Saudi Arabia": "🇸🇦",
    "Uruguay": "🇺🇾",
    "France": "🇫🇷",
    "Senegal": "🇸🇳",
    "Iraq": "🇮🇶",
    "Norway": "🇳🇴",
    "Argentina": "🇦🇷",
    "Algeria": "🇩🇿",
    "Austria": "🇦🇹",
    "Jordan": "🇯🇴",
    "Portugal": "🇵🇹",
    "DR Congo": "🇨🇩",
    "Uzbekistan": "🇺🇿",
    "Colombia": "🇨🇴",
    "England": "🏴",
    "Croatia": "🇭🇷",
    "Ghana": "🇬🇭",
    "Panama": "🇵🇦",
}


def country_with_flag(country):
    return f"{FLAGS.get(country, '🏳️')} {country}"


def prediction_label(value, match):
    if value == "HOME":
        return country_with_flag(match["home_team"])
    if value == "AWAY":
        return country_with_flag(match["away_team"])
    return "🤝 Draw"


def prediction_flag_only(value, home_team, away_team):
    if value == "HOME":
        return FLAGS.get(home_team, "🏳️")
    if value == "AWAY":
        return FLAGS.get(away_team, "🏳️")
    return "🤝"


def section_header(title, subtitle):
    st.markdown(f"""
    <div class="section-title">
        <h2>{title}</h2>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def get_match_result(home_goals, away_goals):
    if home_goals > away_goals:
        return "HOME"
    if home_goals < away_goals:
        return "AWAY"
    return "DRAW"


def fetch_world_cup_matches():
    api_key = st.secrets["FOOTBALL_DATA_API_KEY"]
    competition_code = st.secrets.get("FOOTBALL_COMPETITION_CODE", "WC")

    url = f"https://api.football-data.org/v4/competitions/{competition_code}/matches"

    headers = {
        "X-Auth-Token": api_key
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return []

        data = response.json()
        return data.get("matches", [])

    except requests.exceptions.RequestException:
        return []


def update_scores_from_api():
    api_matches = fetch_world_cup_matches()

    if not api_matches:
        return

    db_matches_res = supabase.table("matches").select("*").execute()
    db_matches = db_matches_res.data

    for db_match in db_matches:
        api_match_id = db_match.get("api_match_id")

        if api_match_id is None:
            continue

        api_match = next(
            (m for m in api_matches if str(m["id"]) == str(api_match_id)),
            None
        )

        if not api_match:
            continue

        status = api_match.get("status")
        full_time = api_match.get("score", {}).get("fullTime", {})
        home_goals = full_time.get("home")
        away_goals = full_time.get("away")

        if status == "FINISHED" and home_goals is not None and away_goals is not None:
            actual_result = get_match_result(home_goals, away_goals)

            supabase.table("matches").update({
                "home_goals": home_goals,
                "away_goals": away_goals,
                "status": status
            }).eq("id", db_match["id"]).execute()

            predictions_res = (
                supabase.table("match_predictions")
                .select("*")
                .eq("match_id", db_match["id"])
                .execute()
            )

            for prediction in predictions_res.data:
                points = 3 if prediction["predicted_result"] == actual_result else 0

                supabase.table("match_predictions").update({
                    "points": points
                }).eq("id", prediction["id"]).execute()


supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

st.markdown("""
<div class="hero-card">
    <div class="hero-logo">🇸🇦 🏆</div>
    <div class="hero-title">World Cup 2026 Prediction Game</div>
    <p class="hero-subtitle">Predict matches and choose your champion.</p>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Menu",
    [
        "Predict",
        "World Cup Winner",
        "Leaderboard",
        "All Match Predictions"
    ]
)

members_res = supabase.table("members").select("*").execute()
members = [m["name"] for m in members_res.data]

matches_res = (
    supabase.table("matches")
    .select("*")
    .eq("is_active", True)
    .execute()
)
matches = matches_res.data

update_scores_from_api()


if page == "Predict":
    section_header(
        "⚽ Predict Match Results",
        "Choose your name, then select the expected result for each match."
    )

    member_name = st.selectbox("Choose your name", members)

    for match in matches:
        home_team = match["home_team"]
        away_team = match["away_team"]

        st.markdown(f"""
        <div class="game-card">
            <div class="match-title">
                {FLAGS.get(home_team, '🏳️')} {home_team}
                <span style="color:#9ca3af;">vs</span>
                {FLAGS.get(away_team, '🏳️')} {away_team}
            </div>
        </div>
        """, unsafe_allow_html=True)

        prediction = st.radio(
            "Prediction",
            ["HOME", "DRAW", "AWAY"],
            format_func=lambda x, m=match: prediction_label(x, m),
            key=f"match_{match['id']}"
        )

        existing_prediction = (
            supabase.table("match_predictions")
            .select("*")
            .eq("member_name", member_name)
            .eq("match_id", match["id"])
            .limit(1)
            .execute()
        )

        if existing_prediction.data:
            saved = existing_prediction.data[0]["predicted_result"]
            st.info(f"Prediction already saved: {prediction_label(saved, match)}")
        else:
            if st.button("Save prediction", key=f"save_{match['id']}"):
                try:
                    supabase.table("match_predictions").insert({
                        "member_name": member_name,
                        "match_id": match["id"],
                        "predicted_result": prediction
                    }).execute()

                    st.success("Prediction saved! You cannot change it now.")
                    st.rerun()

                except Exception:
                    st.error("You already saved a prediction for this match.")


elif page == "World Cup Winner":
    section_header(
        "🌍 Predict World Cup Winner",
        "Choose the country you think will win the World Cup."
    )

    member_name = st.selectbox("Choose your name", members)

    teams = list(FLAGS.keys())

    predicted_winner_display = st.selectbox(
        "Choose winner",
        [country_with_flag(team) for team in teams]
    )

    predicted_winner = predicted_winner_display.split(" ", 1)[1]

    existing_winner = (
        supabase.table("winner_predictions")
        .select("*")
        .eq("member_name", member_name)
        .limit(1)
        .execute()
    )

    if existing_winner.data:
        saved_winner = existing_winner.data[0]["predicted_winner"]
        st.info(f"Winner prediction already saved: {country_with_flag(saved_winner)}")
    else:
        if st.button("Save winner prediction"):
            try:
                supabase.table("winner_predictions").insert({
                    "member_name": member_name,
                    "predicted_winner": predicted_winner
                }).execute()

                st.success("Winner prediction saved! You cannot change it now.")
                st.rerun()

            except Exception:
                st.error("You already saved a World Cup winner prediction.")


elif page == "Leaderboard":
    section_header(
        "🏆 Leaderboard",
        "Total match points and World Cup winner predictions."
    )

    predictions_res = supabase.table("match_predictions").select("*").execute()
    winner_res = supabase.table("winner_predictions").select("*").execute()

    predictions = predictions_res.data
    winner_predictions = winner_res.data

    members_df = pd.DataFrame({"Name": members})

    if predictions:
        predictions_df = pd.DataFrame(predictions)

        points_df = (
            predictions_df.groupby("member_name")["points"]
            .sum()
            .reset_index()
            .rename(columns={
                "member_name": "Name",
                "points": "Points"
            })
        )
    else:
        points_df = pd.DataFrame(columns=["Name", "Points"])

    if winner_predictions:
        winner_df = pd.DataFrame(winner_predictions)

        winner_df["Predicted Winner"] = winner_df["predicted_winner"].apply(
            country_with_flag
        )

        winner_df = winner_df[[
            "member_name",
            "Predicted Winner"
        ]].rename(columns={
            "member_name": "Name"
        })
    else:
        winner_df = pd.DataFrame(columns=["Name", "Predicted Winner"])

    leaderboard_df = (
        members_df
        .merge(points_df, on="Name", how="left")
        .merge(winner_df, on="Name", how="left")
    )

    leaderboard_df["Points"] = leaderboard_df["Points"].fillna(0).astype(int)
    leaderboard_df["Predicted Winner"] = leaderboard_df["Predicted Winner"].fillna("Not selected")

    leaderboard_df = leaderboard_df.sort_values("Points", ascending=False)

    st.dataframe(leaderboard_df, use_container_width=True)


elif page == "All Match Predictions":
    section_header(
        "📋 All Match Predictions",
        "See every member's prediction for every match."
    )

    predictions_res = (
        supabase.table("match_predictions")
        .select("member_name, predicted_result, points, matches(home_team, away_team)")
        .execute()
    )

    predictions = predictions_res.data

    if predictions:
        rows = []

        for p in predictions:
            home_team = p["matches"]["home_team"]
            away_team = p["matches"]["away_team"]

            match_name = (
                f"{FLAGS.get(home_team, '🏳️')} vs "
                f"{FLAGS.get(away_team, '🏳️')}"
            )

            prediction_text = prediction_flag_only(
                p["predicted_result"],
                home_team,
                away_team
            )

            rows.append({
                "Name": p["member_name"],
                "Match": match_name,
                "Prediction": prediction_text,
                "Points": p.get("points", 0)
            })

        df = pd.DataFrame(rows)

        table = df.pivot(
            index="Name",
            columns="Match",
            values="Prediction"
        ).reset_index()

        st.dataframe(table, use_container_width=True)
    else:
        st.info("No match predictions yet.")