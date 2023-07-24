import pandas as pd
import requests

import mysql.connector

locations = ['London', 'Manchester']
df = pd.read_csv("gb_latlon.csv")

def fetch_data(lat, lng):
    payload = {'lat':lat, 'lng':lng}
    r = requests.post("https://data.police.uk/api/crimes-street/all-crime", params=payload)
    res = r.json()
    return res

def store_cleaned_data(locations):
    r = []
    for location in locations:
        df_ = df[df['city'] == location]
        data = fetch_data(df_.lat, df_.lng)
        for x in data:
            # TODO SQL insert queries
            
            r.append(tuple([location, x['category'], x['location']['latitude'], x['location']['longitude'], x['month']]))
    return r
        
def store_dropdown_data(locations):
    r = []
    for location in locations:
        df_ = df[df['city'] == location]
        data = fetch_data(df_.lat, df_.lng)
        for x in data:
            # TODO SQL insert queries
            r.append(tuple([location, len(data)]))
    return r
    
def store_category_data(locations):
    r = []
    for location in locations:
        df_ = df[df['city'] == location]
        data = fetch_data(df_.lat, df_.lng)
        df_ = pd.DataFrame(data)
        df_ = pd.DataFrame(df_['category'].value_counts())

        i_ = []
        for x in df_.index:
            i_.append(x)

        for i in range(len(df_)):
            # TODO SQL insert queries
            r.append(tuple([location, i_[i], df_['category'][i]]))
            
    return r


cnx = mysql.connector.connect(
                user='root',
                password='rootuser',
                host='127.0.0.1',
                database='ukgovcrime')

cursor = cnx.cursor()

insert_clean_data = ("INSERT INTO cleaned_data (location, category, lat, lng, month) VALUES (%s, %s, %s, %s, %s)")

r = store_cleaned_data(locations)
for t in r:
    cursor.execute(insert_clean_data, t)
    
cnx.close()
# DB SCHEMA

# table cleaned_data

# location varchar, category varchar, lat varchar, lng varchar, month varchar


# table dropdown_data

# hash varchar, total_counts varchar, other stats...


# table category_data

# location varchar, category varchar, count varchar





    
    




