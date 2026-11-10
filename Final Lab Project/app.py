import pandas as pd
import streamlit as st

st.set_page_config(page_title="SmartBasket Recommender", page_icon="🛒", layout="wide")
st.title("🛒 SmartBasket: Market Basket Recommender")

@st.cache_data
def load_rules():
    df = pd.read_csv("mined_association_rules.csv")
    df["ante"] = df["antecedents_str"].str.split(" + ", regex=False).apply(frozenset)
    df["cons"] = df["consequents_str"].str.split(" + ", regex=False).apply(frozenset)
    return df

rules_df = load_rules()

st.sidebar.header("Filter rules")
min_conf = st.sidebar.slider("Minimum confidence", 0.10, 1.00, 0.20, 0.05)
min_lift = st.sidebar.slider("Minimum lift", 1.0, 4.0, 1.1, 0.1)
top_n    = st.sidebar.slider("Recommendations to show", 1, 10, 3)

rules_f = rules_df[(rules_df["confidence"] >= min_conf) & (rules_df["lift"] >= min_lift)]
st.sidebar.metric("Rules after filter", len(rules_f))

items = sorted(set().union(*rules_df["ante"]) | set().union(*rules_df["cons"]))

st.subheader("Simulate a customer cart")
cart = set(st.multiselect("Items in the basket:", items, default=[items[0]]))

if cart:
    hits = []
    for _, r in rules_f.iterrows():
        if r["ante"] <= cart:
            for item in r["cons"] - cart:
                hits.append({"Recommended item": item, "Triggered by": r["antecedents_str"],
                             "Confidence": round(r["confidence"], 3), "Lift": round(r["lift"], 3)})
    if hits:
        out = (pd.DataFrame(hits).sort_values(["Lift", "Confidence"], ascending=False)
                 .drop_duplicates("Recommended item").head(top_n))
        st.success("Frequently bought together:")
        st.dataframe(out, hide_index=True, use_container_width=True)
    else:
        st.warning("No rule matches this cart with the current filters.")

st.subheader("All mined rules")
st.dataframe(rules_f[["antecedents_str", "consequents_str", "support", "confidence", "lift"]],
             hide_index=True, use_container_width=True)
