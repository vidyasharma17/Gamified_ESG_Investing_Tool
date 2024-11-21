import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Load Dataset
st.title("Gamified ESG Investing Tool")
st.markdown("""
Welcome to the **Gamified ESG Investing Tool**!  
This tool helps you build and analyze an ESG (Environmental, Social, and Governance) investment portfolio.  
Learn about ESG levels, customize your thresholds, and see how your portfolio stacks up against others.  
Let's create a sustainable portfolio while having fun!
""")

try:
    esg_data = pd.read_csv('/Users/vidyasharma/Downloads/data.csv')
except FileNotFoundError:
    st.error("Dataset not found. Please check the file path.")
    st.stop()

# Display only company names (scrollable)
st.header("Explore Companies")
st.markdown("Below is a list of companies you can explore for your portfolio.")
st.dataframe(esg_data[["name"]], height=300)

# User Inputs: Build Your ESG Portfolio
st.header("Build Your ESG Portfolio")
industries = esg_data['industry'].unique()
selected_industry = st.selectbox("Select Industry:", options=industries)

# Filter Companies Based on Selected Industry
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
    placeholder_path = "/Users/vidyasharma/Downloads/Dataset/Gamified ESG Tool/No_Logo_Available.png"

for _, row in portfolio_data.iterrows():
    # Check if the logo column is empty or invalid
    if pd.notna(row["logo"]) and str(row["logo"]).strip() != "":
        st.image(row["logo"], caption=row["name"], width=100, use_column_width=False)
    else:
        # Use the local placeholder image
        st.image(placeholder_path, caption=row["name"], width=100, use_column_width=False)

    # Calculate Average ESG Scores
    avg_environment = portfolio_data['environment_score'].mean()
    avg_social = portfolio_data['social_score'].mean()
    avg_governance = portfolio_data['governance_score'].mean()
    total_impact_score = portfolio_data['total_score'].mean()

    # Normalize Scores for Challenges Tracker
    normalized_environment = (avg_environment / 850) * 100
    normalized_social = (avg_social / 750) * 100
    normalized_governance = (avg_governance / 780) * 100
    normalized_total = (total_impact_score / 2380) * 100
    weighted_total = (
        (normalized_environment * 0.4) +
        (normalized_social * 0.3) +
        (normalized_governance * 0.3)
    )

    # Display Updated Portfolio Impact Scores with Benchmarks
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

    # Visualize ESG Breakdown with Pie Chart
    st.header("ESG Breakdown")
    st.markdown("This pie chart shows the distribution of Environmental, Social, and Governance scores.")
    labels = ["Environmental", "Social", "Governance"]
    values = [avg_environment, avg_social, avg_governance]
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    st.pyplot(fig)

    # Horizontal Bar Chart for ESG Contribution with Dynamic Storytelling
    st.header("Company-wise ESG Contribution")
    fig, ax = plt.subplots()
    contribution_data = portfolio_data.set_index("name")[["environment_score", "social_score", "governance_score"]]
    contribution_data.plot(kind='barh', ax=ax, color=["green", "blue", "orange"], figsize=(10, 6))
    ax.set_xlabel("Scores")
    ax.set_title("Company-wise ESG Contribution")
    st.pyplot(fig)

    # Dynamic Storytelling
    top_company = contribution_data.sum(axis=1).idxmax()
    low_company = contribution_data.sum(axis=1).idxmin()
    top_score = contribution_data.sum(axis=1).max()
    low_score = contribution_data.sum(axis=1).min()
    st.markdown(f"""
    ### What This Graph Tells You:
    - The top contributor in your portfolio is **{top_company}**, with a total ESG score of **{top_score:.2f}**.
    - The least contributor is **{low_company}**, with a total ESG score of only **{low_score:.2f}**.
    - Consider removing **{low_company}** or diversifying your portfolio to improve overall performance.
    """)

    # Challenges Tracker with Dynamic Coin Rewards
    st.header("Challenges Tracker")
    st.markdown("Earn coins by meeting these challenges. Scores are compared to industry benchmarks.")
    coins = 0
    challenges = {
        f"Environmental Leader (≥ 75%)": normalized_environment >= 75,
        f"Social Advocate (≥ 70%)": normalized_social >= 70,
        f"Governance Specialist (≥ 70%)": normalized_governance >= 70,
        f"Portfolio Expert (Weighted Score ≥ 80%)": weighted_total >= 80,
    }
    for challenge, completed in challenges.items():
        if completed:
            coins += 10
            st.success(f"✅ {challenge} - Earned 10 coins!")
        else:
            st.warning(f"❌ {challenge} - Not yet achieved.")
    st.markdown(f"### Total Coins Earned: **{coins} 🪙**")

    # Community Leaderboard with Weighted Scores and Coins
    st.header("Community Leaderboard")
    leaderboard_data = {
        "Name": ["Alice", "John", "Nita", "You"],
        "Weighted Score": [88, 85, 80, weighted_total],
        "Coins Earned": [50, 45, 40, coins],
    }
    leaderboard_df = pd.DataFrame(leaderboard_data).sort_values(by="Weighted Score", ascending=False)
    leaderboard_df["Rank"] = range(1, len(leaderboard_df) + 1)
    st.table(leaderboard_df)

    # Dynamic Messages Based on Rank
    user_rank = leaderboard_df[leaderboard_df["Name"] == "You"]["Rank"].values[0]
    if user_rank == 1:
        st.success(f"🎉 Congratulations! You're leading the leaderboard with a weighted score of {weighted_total:.2f}!")
    elif user_rank <= 3:
        st.info(f"👏 Great job! You're ranked #{user_rank} with a score of {weighted_total:.2f}. Keep pushing!")
    else:
        st.warning(f"⚠️ You're ranked #{user_rank}. Keep improving your portfolio to climb higher!")

    # FAQ Section
    with st.expander("FAQ: Understanding ESG Levels"):
        st.write("""
        - **AAA**: Exceptional ESG performance, industry leader.
        - **AA**: Strong ESG performance.
        - **A**: Above-average ESG performance.
        - **BBB**: Average ESG performance.
        - **BB/B/CCC**: Below-average performance with increasing risks.
        """)
else:
    st.warning("Please select at least one company to build your portfolio.")
