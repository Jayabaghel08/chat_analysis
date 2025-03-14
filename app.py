import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8", errors='ignore')

    df = preprocessor.preprocess(data)
    df['sentiment'] = df['message'].apply(helper.get_sentiment)
    
    # Fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):
        
        # If a specific user is selected, filter the DataFrame
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]

        # ---- Top Statistics ----
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # ---- Monthly Timeline ----
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # ---- Daily Timeline ----
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # ---- Activity Map ----
        st.title('Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, ax=ax)
        st.pyplot(fig)

        # ---- Most Busy Users (Group Level) ----
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                # Pie Chart
                ax.pie(x.values, labels=x.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        # ---- WordCloud ----
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # ---- Most Common Words ----
        st.title("Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1], color='lightgreen')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # ---- Emoji Analysis ----
        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)

        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.bar(emoji_df['emoji'], emoji_df['count'], color='coral')
            ax.set_xlabel('Emoji')
            ax.set_ylabel('Count')
            ax.set_title('Emoji Frequency')
            plt.xticks(rotation=90)
            st.pyplot(fig)

        # ---- Sentiment Analysis ----
        st.title("Sentiment Analysis")
        sentiment_mean = df['sentiment'].mean()
        if sentiment_mean > 0:
            st.write(f"Overall sentiment is Positive with a score of {sentiment_mean:.2f}")
        elif sentiment_mean < 0:
            st.write(f"Overall sentiment is Negative with a score of {sentiment_mean:.2f}")
        else:
            st.write("Overall sentiment is Neutral")

        # Sentiment Distribution
        st.title("Sentiment Distribution")
        fig, ax = plt.subplots()
        sns.histplot(df['sentiment'], kde=False, bins=20, color='blue', ax=ax)
        ax.set_title("Sentiment Distribution")
        ax.set_xlabel("Sentiment Polarity")
        ax.set_ylabel("Message Count")
        st.pyplot(fig)
