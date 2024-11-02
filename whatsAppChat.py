import regex
import pandas as pd
from collections import Counter
import numpy as np
from datetime import datetime
import plotly.express as px
import emoji

def date_time(s):
    pattern = r'^\[([0-9]{4}-[0-9]{2}-[0-9]{2}), ([0-9]{2}:[0-9]{2}:[0-9]{2})\]'
    result = regex.match(pattern, s) #match is function use to match the pattern with the string
    return bool(result) #return true if the pattern is matched

def get_date_time_author_message(line):
    pattern = r'^\[([0-9]{4}-[0-9]{2}-[0-9]{2}), ([0-9]{2}:[0-9]{2}:[0-9]{2})\] (.+?): (.*)'
    match = regex.match(pattern, line)
    #if match is not None then it will return the groups of the matched pattern
    if match:
        date, time, author, message = match.groups() #groups is function use to get the groups of the matched pattern 
        return date, time, author, message
    return None, None, None, line

data = []
conversation = 'whatsappChatMessage.txt'
with open(conversation, encoding="utf-8") as fp: #open the file in read mode with encoding utf-8
    fp.readline() #read the first line of the file
    message_buffer = []
    date, time, author = None, None, None
    for line in fp:
        line = line.strip() #remove the leading and trailing spaces
        if date_time(line): #check if the line is a date and time
            if message_buffer:
                data.append([date, time, author, ' '.join(message_buffer)]) #append function is used to add the elements in the list
                message_buffer.clear()
            date, time, author, message = get_date_time_author_message(line) #get the date, time, author and message from the line
            if author:
                message_buffer.append(message) #append the message in the message_buffer
        else:
            message_buffer.append(line) #append the line in the message_buffer
    if message_buffer:
        data.append([date, time, author, ' '.join(message_buffer)])

df = pd.DataFrame(data, columns=["Date", "Time", "Author", "Message"]) #create a dataframe from the data and dataframe is table with columns and rows
print(df.tail(20)) #print the last 20 rows of the dataframe
print(df.info()) #print the information of the dataframe
print(df["Author"].unique()) #print the unique authors in the dataframe

total_messages = df.shape[0] #shape is attribute of the dataframe which gives the number of rows and columns
print(total_messages)
print("\n")

# Filter out media messages
media_messages_df = df[df['Message'] == '<Media omitted>']
messages_df = df.drop(media_messages_df.index)

# Calculate letter and word counts
messages_df['Letter_Count'] = messages_df['Message'].apply(len)
messages_df['Word_Count'] = messages_df['Message'].apply(lambda s: len(s.split(' ')))
messages_df['MessageCount'] = 1

# Extract emojis from messages and create 'emoji' column
messages_df['emoji'] = messages_df['Message'].apply(lambda x: [char for char in x if char in emoji.EMOJI_DATA])

# Flatten list of emojis across messages and count them
total_emojis_list = [e for emoji_list in messages_df['emoji'] for e in emoji_list]
emoji_counts = Counter(total_emojis_list)

# Create DataFrame for emoji frequency and visualize
print("Emoji Distribution in WhatsApp Messages")
print("Displaying graph in browser...")
emoji_df = pd.DataFrame(emoji_counts.items(), columns=['emoji', 'count']).sort_values(by='count', ascending=False)
fig = px.pie(emoji_df, values='count', names='emoji', title="Emoji Distribution in WhatsApp Messages")
fig.update_traces(textposition='inside', textinfo='percent+label')
fig.show()