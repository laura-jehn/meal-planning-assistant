import streamlit as st

st.title("🚧 Coming Soon: New Features")
st.markdown("Here's what's planned for the future — stay tuned! 💡")

future_features = [
    "✅ **User login and account management**",
    "✅ **Deployment including pwa**",
    "✅ **Add recipes directly from links (e.g., Instagram or websites)**",
    "✅ **Submit feature requests to improve the app**",
    "✅👥 Collaborate by exploring recipes shared by others",
    "🤝 **Link accounts with your partner (optional)**",
    "📋 Input nutritional info (carbs/protein/fat) and view weekly totals**",
    "📸 Option to insert a photo for each recipe",
    "🥬 Create recipes using leftovers from your fridge",
    "💬 Brainstorm recipe ideas with an AI-powered chat",
    "🌱 Get suggestions for seasonal vegetables",
    "💸 Discover vegetables that are budget-friendly right now",
    "📊 Link recipes to your budget for smarter planning",
    "⭐ Rate recipes you’ve tried and mark your favorites",
    "📈 Track your eating habits over time (e.g. veggie distribution)",
]

for feature in future_features:
    st.markdown(f"- {feature}")