from pathlib import Path
import json

import numpy as np
import pandas as pd
import phate
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="General Conference Talk Explorer", layout="wide")

DATA_PATH = Path("data/gc_talks.csv")
MONTH_LABELS = {"04": "April", "10": "October"}


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Normalize types for consistent filtering controls.
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["month"] = df["month"].astype(str).str.zfill(2)

    text_columns = ["title", "author", "role", "kicker", "text"]
    for column in text_columns:
        if column in df.columns:
            df[column] = df[column].fillna("")

    if "embedding" in df.columns:

        def parse_embedding(value):
            if pd.isna(value):
                return None
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    return None
                try:
                    parsed = json.loads(value)
                    return np.array(parsed, dtype=float)
                except (json.JSONDecodeError, ValueError, TypeError):
                    return None
            return None

        df["embedding"] = df["embedding"].apply(parse_embedding)

    return df


@st.cache_data(show_spinner=False)
def build_phate_figure(df: pd.DataFrame):
    emb_df = df[df["embedding"].notnull()].copy()
    if emb_df.empty:
        return None

    embeddings = np.stack(emb_df["embedding"].values)
    phate_op = phate.PHATE(n_components=2)
    phate_result = phate_op.fit_transform(embeddings)

    fig = px.scatter(
        x=phate_result[:, 0],
        y=phate_result[:, 1],
        color=emb_df["role"],
        hover_name=emb_df["title"],
        hover_data={
            "author": emb_df["author"],
            "role": emb_df["role"],
            "year": emb_df["year"],
            "month": emb_df["month"],
        },
    )
    fig.update_layout(legend_title_text="Role")
    return fig


st.title("General Conference Talk Explorer")
st.write(
    "Filter talks by year, month, phrase, and role. "
    "Phrase matching checks both title and full talk text."
)

if not DATA_PATH.exists():
    st.error("Could not find data/gc_talks.csv. Generate the dataset first, then rerun the app.")
    st.stop()

raw_df = load_data(DATA_PATH)

with st.sidebar:
    st.header("Filters")

    available_years = sorted(raw_df["year"].dropna().astype(int).unique().tolist())
    selected_years = st.multiselect(
        "Select year(s)",
        options=available_years,
        default=available_years,
    )

    month_options = ["04", "10"]
    selected_months = st.multiselect(
        "Select month(s)",
        options=month_options,
        default=month_options,
        format_func=lambda m: f"{m} ({MONTH_LABELS.get(m, m)})",
    )

    available_roles = sorted([role for role in raw_df["role"].dropna().unique().tolist() if role])
    selected_roles = st.multiselect(
        "Filter role(s)",
        options=available_roles,
        default=available_roles,
    )

    phrase = st.text_input(
        "Talk contains phrase",
        placeholder="faith in Jesus Christ",
    ).strip()

    sort_choice = st.selectbox(
        "Sort results by",
        options=[
            "Year (newest first)",
            "Year (oldest first)",
            "Role (A-Z)",
            "Title (A-Z)",
            "Author (A-Z)",
        ],
    )

    st.header("Graphic 2 Controls")
    exclude_sustaining = st.checkbox("Exclude titles containing 'Sustaining of'", value=True)
    exclude_auditing = st.checkbox("Exclude titles containing 'Church Auditing'", value=True)
    exclude_ward = st.checkbox("Exclude roles containing 'Ward'", value=True)

filtered_df = raw_df.copy()

if selected_years:
    filtered_df = filtered_df[filtered_df["year"].isin(selected_years)]
else:
    filtered_df = filtered_df.iloc[0:0]

if selected_months:
    filtered_df = filtered_df[filtered_df["month"].isin(selected_months)]
else:
    filtered_df = filtered_df.iloc[0:0]

if selected_roles:
    filtered_df = filtered_df[filtered_df["role"].isin(selected_roles)]
else:
    filtered_df = filtered_df.iloc[0:0]

if phrase:
    combined = filtered_df["title"].str.cat(filtered_df["text"], sep=" ")
    filtered_df = filtered_df[combined.str.contains(phrase, case=False, na=False)]

result_count = len(filtered_df)
st.subheader(f"Results: {result_count} talk(s)")

if result_count == 0:
    st.info("No talks matched the current filters.")
else:
    display_df = filtered_df[["year", "month", "title", "author", "role", "kicker"]].copy()

    if sort_choice == "Year (newest first)":
        display_df = display_df.sort_values(["year", "month", "title"], ascending=[False, True, True])
    elif sort_choice == "Year (oldest first)":
        display_df = display_df.sort_values(["year", "month", "title"], ascending=[True, True, True])
    elif sort_choice == "Role (A-Z)":
        display_df = display_df.sort_values(["role", "year", "month", "title"], ascending=[True, False, True, True])
    elif sort_choice == "Title (A-Z)":
        display_df = display_df.sort_values(["title", "year", "month"], ascending=[True, False, True])
    else:
        display_df = display_df.sort_values(["author", "year", "month", "title"], ascending=[True, False, True, True])

    display_df["month"] = display_df["month"].map(lambda m: MONTH_LABELS.get(m, m))
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    with st.expander("Show full text for selected talk"):
        talk_titles = filtered_df["title"].tolist()
        chosen_title = st.selectbox("Choose a talk", options=talk_titles)
        chosen_talk = filtered_df.loc[filtered_df["title"] == chosen_title].iloc[0]

        st.markdown(f"### {chosen_talk['title']}")
        st.write(f"**Author:** {chosen_talk['author']}")
        st.write(f"**Role:** {chosen_talk['role']}")
        st.write(f"**Conference:** {chosen_talk['year']} {MONTH_LABELS.get(chosen_talk['month'], chosen_talk['month'])}")
        if chosen_talk["kicker"]:
            st.caption(chosen_talk["kicker"])
        st.write(chosen_talk["text"])

st.divider()
st.header("PHATE Visualizations")
st.write("These two charts mirror the notebook graphics: one for the full filtered dataset and one with optional exclusions.")

chart_col_1, chart_col_2 = st.columns(2)

with chart_col_1:
    st.subheader("Graphic 1: Full Filtered Set")
    fig_all = build_phate_figure(filtered_df)
    if fig_all is None:
        st.info("No rows with embeddings are available for the current filters.")
    else:
        st.plotly_chart(fig_all, use_container_width=True)

with chart_col_2:
    st.subheader("Graphic 2: Configurable Subset")
    reduced_df = filtered_df.copy()
    if exclude_sustaining:
        reduced_df = reduced_df[~reduced_df["title"].str.contains("Sustaining of", case=False, na=False)]
    if exclude_auditing:
        reduced_df = reduced_df[~reduced_df["title"].str.contains("Church Auditing", case=False, na=False)]
    if exclude_ward:
        reduced_df = reduced_df[~reduced_df["role"].str.contains("Ward", case=False, na=False)]

    fig_reduced = build_phate_figure(reduced_df)
    if fig_reduced is None:
        st.info("No rows with embeddings remain after subset filters.")
    else:
        st.plotly_chart(fig_reduced, use_container_width=True)
