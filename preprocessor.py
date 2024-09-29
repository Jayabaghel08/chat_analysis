import re
import pandas as pd

def preprocess(data):
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}[\u202F\s][APM]+ - '

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    cleaned_dates = [date.replace('\u202f', ' ') for date in dates]

    df = pd.DataFrame({'user_message': messages, 'message_date': cleaned_dates})

    df['message_date'] = pd.to_datetime(df['message_date'].str.replace(' - ', ''), format='%m/%d/%y, %I:%M %p', errors='coerce')
    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Check if the date column is not datetime and convert it
    if df['date'].dtype != 'datetime64[ns]':
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Check for NaT values after conversion
    if df['date'].isnull().any():
        print("Warning: Some dates could not be parsed and will be removed.")
        df = df.dropna(subset=['date'])

    # Now you can safely use the .dt accessor
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.strftime('%I').astype(int)
    df['minute'] = df['date'].dt.strftime('%M')
    df['AM_PM'] = df['date'].dt.strftime('%p')
    df['only_date'] = df['date'].dt.date

    df['date'] = df['date'].dt.strftime('%Y-%m-%d %I:%M %p')

    # Create 'day_name' column
    df['day_name'] = pd.to_datetime(df['only_date']).dt.day_name()  # Convert 'only_date' to datetime for day_name

    df = df[['date', 'only_date', 'user', 'message', 'year', 'month', 'month_num', 'day', 'hour', 'minute', 'AM_PM', 'day_name']]

    period = []
    for index, row in df.iterrows():
        hour = int(row['hour'])
        if hour == 23:
            period.append(f"{hour}-{0:02d}")
        elif hour == 0:
            period.append(f"{0:02d}-{hour + 1}")
        else:
            period.append(f"{hour}-{hour + 1}")

    df['period'] = period
    return df
