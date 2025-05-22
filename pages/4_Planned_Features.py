import streamlit as st

st.title("🚧 Coming Soon: New Features")
st.markdown("Here's what's planned for the future — stay tuned! 💡")

future_features = [
    "👫 **Share recipes with your partner and get their feedback**",
    "🗂️ **Plan meals effortlessly with drag-and-drop functionality**",
    "🥬 **Create recipes using leftovers from your fridge**",
    "💬 **Brainstorm recipe ideas with an AI-powered chat**",
    "🌱 **Get suggestions for seasonal vegetables**",
    "💸 **Discover vegetables that are budget-friendly right now**",
    "📊 **Link recipes to your budget for smarter planning**",
    "⭐ **Rate recipes you’ve tried and mark your favorites**",
    "📈 **Track your eating habits over time (e.g. veggie distribution)**",
    "👥 **Collaborate by exploring recipes shared by others**",
]

for feature in future_features:
    st.markdown(f"- {feature}")