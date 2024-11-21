import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import random

# Constants
PLACEHOLDER_IMAGE_PATH = "/Users/vidyasharma/Downloads/Dataset/Gamified ESG Tool/No_Logo_Available.png"
Coins_initial = 0

# App Title and Introduction
st.title("Gamified ESG Investing Tool")
st.markdown("""
Welcome to the **Gamified ESG Investing Tool**!  
This tool helps you build and analyze an ESG (Environmental, Social, and Governance) investment portfolio. Learn about ESG levels, customize your thresholds, and see how your portfolio stacks up against others.  
🎮 **Compete, Learn, and Earn Coins!** 🎉  
Let's create a sustainable portfolio while having fun!
""")

# Load Dataset
try:
    esg_data = pd.read_csv('data.csv')
except FileNotFoundError:
    st.error("Dataset not found. Please check the file path.")
    st.stop()

# Display the database for users
st.header("Explore Companies")
st.markdown("""
Below is a list of companies along with their ESG details.  
You can use this information to make informed decisions when building your portfolio.
""")
columns_to_display = [
    "name", "exchange", "environment_grade", "social_grade",
    "governance_grade", "environment_score", "social_score",
    "governance_score", "total_score"
]
st.dataframe(esg_data[columns_to_display], height=300)


# User Inputs: Build Your ESG Portfolio
st.header("Build Your ESG Portfolio")
industries = esg_data['industry'].unique().tolist()  # Get unique industries
industries.insert(0, "All")  # Add "All" as the first option
selected_industry = st.selectbox("Select Industry:", options=industries)

# Filter Companies Based on Selected Industry
if selected_industry == "All":
    filtered_data = esg_data  # No filtering applied
else:
    filtered_data = esg_data[esg_data["industry"] == selected_industry]

portfolio_size = st.slider("How many companies would you like to select?", 1, 10, value=3)
selected_companies = st.multiselect(
    "Select Companies for your portfolio:",
    options=filtered_data["name"].unique(),
    default=filtered_data["name"].head(portfolio_size),
)

# Filter the Portfolio Data Based on User Selection
portfolio_data = filtered_data[filtered_data["name"].isin(selected_companies)]

if not portfolio_data.empty:
    # Display Selected Portfolio
    st.subheader("Your Selected Portfolio")
    st.markdown("Here are the details of the companies in your portfolio.")
    st.dataframe(
        portfolio_data[["name", "industry", "environment_grade", "social_grade", 
                        "governance_grade", "total_grade", "currency"]].style.set_properties(
            **{'font-weight': 'bold'}, subset=['name']
        )
    )

    # Display Company Logos with Placeholder for Missing Logos
    st.header("Company Logos")
    st.markdown("Logos of the companies in your portfolio. Missing logos are replaced with a placeholder.")
    for _, row in portfolio_data.iterrows():
        if pd.notna(row["logo"]) and str(row["logo"]).strip() != "":
            st.image(row["logo"], caption=row["name"], width=100, use_container_width=False)
        else:
            st.image(PLACEHOLDER_IMAGE_PATH, caption=row["name"], width=100, uuse_container_width=False)

    # Calculate ESG Scores
    avg_environment = portfolio_data['environment_score'].mean()
    avg_social = portfolio_data['social_score'].mean()
    avg_governance = portfolio_data['governance_score'].mean()
    total_impact_score = portfolio_data['total_score'].mean()

    # Normalize Scores
    normalized_environment = (avg_environment / 850) * 100
    normalized_social = (avg_social / 750) * 100
    normalized_governance = (avg_governance / 780) * 100
    normalized_total = (total_impact_score / 2380) * 100
    weighted_total = (
        (normalized_environment * 0.4) +
        (normalized_social * 0.3) +
        (normalized_governance * 0.3)
    )

    # Portfolio Impact Scores with Benchmarks
    st.header("Portfolio Impact Scores")
    st.markdown("This table summarizes the ESG scores for your portfolio with industry benchmarks.")
    impact_scores = pd.DataFrame({
        "Metric": ["Environmental Impact", "Social Impact", "Governance Impact", "Overall Impact Score"],
        "Score": [avg_environment, avg_social, avg_governance, total_impact_score],
        "Best Score": [850, 750, 780, 2380],
        "Industry Benchmark": ["≥ 70%", "≥ 70%", "≥ 70%", "≥ 70%"],
        "Performance": [
            "Below Average" if avg_environment < 595 else "Good",
            "Below Average" if avg_social < 525 else "Good",
            "Below Average" if avg_governance < 546 else "Good",
            "Below Average" if total_impact_score < 1666 else "Good",
        ],
    })
    st.table(impact_scores)

    # ESG Breakdown with Pie Chart
    st.header("ESG Breakdown")
    st.markdown("This pie chart shows the distribution of Environmental, Social, and Governance scores.")
    labels = ["Environmental", "Social", "Governance"]
    values = [avg_environment, avg_social, avg_governance]
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    st.pyplot(fig)

    # Dynamic Storytelling for Pie Chart
    dominant_area = labels[values.index(max(values))]
    weak_area = labels[values.index(min(values))]
    dominant_percentage = max(values) / sum(values) * 100
    weak_percentage = min(values) / sum(values) * 100

    st.markdown(f"""
    ### Insights from ESG Breakdown:
    - Your portfolio has the strongest focus on **{dominant_area}**, comprising **{dominant_percentage:.2f}%** of the total scores.
    - The weakest area is **{weak_area}**, contributing only **{weak_percentage:.2f}%**.
    - Consider adding companies with higher **{weak_area}** scores to improve overall balance.
    """)

    # Horizontal Bar Chart for ESG Contribution with Dynamic Storytelling
    st.header("Company-wise ESG Contribution")
    contribution_data = portfolio_data.set_index("name")[["environment_score", "social_score", "governance_score"]]
    fig, ax = plt.subplots()
    contribution_data.plot(kind='barh', ax=ax, color=["green", "blue", "orange"], figsize=(10, 6))
    ax.set_xlabel("Scores")
    ax.set_title("Company-wise ESG Contribution")
    st.pyplot(fig)

    # Dynamic Storytelling for Bar Chart
    top_company = contribution_data.sum(axis=1).idxmax()
    low_company = contribution_data.sum(axis=1).idxmin()
    top_score = contribution_data.sum(axis=1).max()
    low_score = contribution_data.sum(axis=1).min()
    st.markdown(f"""
    ### Insights from ESG Contribution:
    - The top contributor is **{top_company}** with a total ESG score of **{top_score:.2f}**.
    - The least contributor is **{low_company}** with a total ESG score of **{low_score:.2f}**.
    - Diversify or replace low-performing companies like **{low_company}** to improve your portfolio.
    """)

    # Gamification: Daily Challenge
    st.header("🎯 Daily Challenge")
    Coins = Coins_initial

    # Adjust target score range based on the metric
    metric_ranges = {
    "Environmental Impact": (500, 800),  # Easier to achieve higher scores
    "Social Impact": (300, 600),         # Moderate difficulty
    "Governance Impact": (300, 600)      # Moderate difficulty
    }

    # Randomly select a metric and a target score
    random_metric = random.choice(list(metric_ranges.keys()))
    target_score = random.randint(*metric_ranges[random_metric])

    # Display the daily challenge
    st.markdown(f"""
    Today's challenge: Select a portfolio with **{random_metric} ≥ {target_score}**.  
    Earn **20 bonus coins** if you achieve this target!
    """)

    # Evaluate if the challenge is met
    if random_metric == "Environmental Impact" and avg_environment >= target_score:
        challenge_met = True
    elif random_metric == "Social Impact" and avg_social >= target_score:
        challenge_met = True
    elif random_metric == "Governance Impact" and avg_governance >= target_score:
        challenge_met = True
    else:
        challenge_met = False

    if challenge_met:
        st.balloons()
        st.success(f"🎉 Congratulations! You've met the daily challenge and earned **20 bonus coins!**")
        Coins += 20  # Increment coins for meeting the challenge
    else:
        st.warning(f"❌ Keep trying to meet today's challenge for bonus rewards!")

    # Challenges Tracker with Dynamic Coins
    st.header("Challenges Tracker")
    st.markdown("Earn coins by meeting these challenges! Compare your scores with industry benchmarks.")

    # Initialize coin counter
    challenges = {
    "Environmental Leader (≥ 75%)": normalized_environment >= 75,
    "Social Advocate (≥ 70%)": normalized_social >= 70,
    "Governance Specialist (≥ 70%)": normalized_governance >= 70,
    "Portfolio Expert (Weighted Score ≥ 80%)": weighted_total >= 80,
    }

    for challenge, completed in challenges.items():
        if completed:
            Coins += 10  # Add 10 coins for each completed challenge
            st.success(f"✅ {challenge} - Earned 10 coins!")
        else:
            st.warning(f"❌ {challenge} - Not yet achieved.")

    # Display total coins
    st.markdown(f"### Total Coins Earned: **{Coins} 🪙**")


    # Enhanced Leaderboard
    st.header("Community Leaderboard")
    leaderboard_data = {
        "Name": ["Alice", "John", "Nita", "You"],
        "Weighted Score": [88, 85, 80, weighted_total],
        "Coins Earned": [50, 45, 40, Coins],
    }
    leaderboard_df = pd.DataFrame(leaderboard_data).sort_values(by="Weighted Score", ascending=False)
    leaderboard_df["Rank"] = range(1, len(leaderboard_df) + 1)
    st.table(leaderboard_df)

    # Feedback Based on Rank
    user_rank = leaderboard_df[leaderboard_df["Name"] == "You"]["Rank"].values[0]
    if user_rank == 1:
        st.success(f"🎉 Congratulations! You're leading the leaderboard with a weighted score of {weighted_total:.2f}!")
    elif user_rank <= 3:
        st.info(f"👏 Great job! You're ranked #{user_rank}. Aim for the top spot by earning more coins!")
    else:
        st.warning(f"⚠️ You're ranked #{user_rank}. Improve your portfolio to climb higher!")

    # Bonus Coins for Improvement
    st.header("Bonus Rewards")
    if "previous_scores" not in st.session_state:
        st.session_state["previous_scores"] = {"environment": 0, "social": 0, "governance": 0, "total": 0}
    prev_scores = st.session_state["previous_scores"]
    bonus_coins = 0

    if avg_environment > prev_scores["environment"]:
        bonus_coins += 5
        st.success("🌱 Environmental Score Improved: +5 bonus coins!")
    if avg_social > prev_scores["social"]:
        bonus_coins += 5
        st.success("🤝 Social Score Improved: +5 bonus coins!")
    if avg_governance > prev_scores["governance"]:
        bonus_coins += 5
        st.success("🏛️ Governance Score Improved: +5 bonus coins!")
    if total_impact_score > prev_scores["total"]:
        bonus_coins += 10
        st.success("✨ Total Impact Score Improved: +10 bonus coins!")

    # Update and Display Total Coins
    total_coins = Coins + bonus_coins
    st.markdown(f"### Total Coins (Including Bonuses): **{total_coins} 🪙**")

    # Update Previous Scores in Session State
    st.session_state["previous_scores"] = {
        "environment": avg_environment,
        "social": avg_social,
        "governance": avg_governance,
        "total": total_impact_score,
    }

    # FAQs Section
    st.header("FAQs: Understanding ESG Investing")
    with st.expander("What is ESG Investing?"):
        st.write("""
        ESG Investing stands for Environmental, Social, and Governance Investing. It involves considering these three factors when evaluating companies for investment to align with sustainability and ethical practices.
        """)

    with st.expander("How are ESG Scores Calculated?"):
        st.write("""
        ESG scores are typically calculated using a combination of company disclosures, third-party research, and analytics.
        - **Environmental**: Includes carbon emissions, energy use, and waste management.
        - **Social**: Focuses on labor practices, community relations, and customer satisfaction.
        - **Governance**: Measures corporate governance, board diversity, and ethical practices.
        """)

    with st.expander("What do ESG Levels (AAA, AA, etc.) Mean?"):
        st.write("""
        ESG levels are ratings assigned to companies based on their ESG performance:
        - **AAA**: Exceptional performance; industry leader.
        - **AA**: Strong performance.
        - **A**: Above-average performance.
        - **BBB**: Average performance.
        - **BB/B/CCC**: Below-average performance with increasing risks.
        """)

    with st.expander("How Can I Improve My Portfolio?"):
        st.write("""
        - Diversify your portfolio across industries.
        - Focus on companies with higher scores in areas where your portfolio is weak (Environmental, Social, or Governance).
        - Experiment with different portfolio combinations and use the insights from the tool.
        - Aim to balance all three ESG factors for a strong weighted score.
        """)

    with st.expander("What Are Coins and How Do I Earn Them?"):
        st.write("""
        Coins are rewards for meeting ESG challenges, improving your portfolio, and achieving milestones.  
        - **Challenges**: Earn 10 coins for each challenge completed.
        - **Improvements**: Earn bonus coins for improving your scores.
        - **Daily Challenges**: Earn 20 bonus coins by meeting daily targets.
        Use coins to track your progress and compete on the leaderboard!
        """)

else:
    st.warning("Please select at least one company to build your portfolio.")

# Add disclaimer in the sidebar
st.sidebar.title("Disclaimer")
st.sidebar.markdown("""
This tool uses publicly available data sourced from Kaggle's "Public Company ESG Ratings" dataset by Alistair King. 
The dataset is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). 

The data may not reflect the most accurate or up-to-date ESG information.  
This app is for **educational and exploratory purposes only** and does not provide financial or investment advice.
""")


# Add License Information with Expandable Button
with st.expander("📜 License Information"):
    st.markdown("""
    ### Gamified ESG Investing Tool
    Copyright (c) 2024 Vidya Venugopal Sharma.  
    Licensed under **CC BY-NC-SA 4.0**.  
    Unauthorized commercial use or distribution is prohibited.  
    [Learn More About the License](https://creativecommons.org/licenses/by-nc-sa/4.0/)
    """)

