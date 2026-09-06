from json import load
from pathlib import Path

import streamlit as st

from minsearch import Index


DATA_PATH = Path(__file__).resolve().parents[2] / "data/data.json"


def load_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        return load(f)


def build_index(documents):
    index = Index(
        text_fields=['name', 'measurements', 'type'],
        keyword_fields=['type','material'],
        numeric_fields=['price', 'quantity']
    )
    index.fit(documents)
    return index

@st.cache_resource
def get_index():
    documents = load_data()  # load data.json
    return build_index(documents)
