import pandas as pd
import requests
import hashlib
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
            input = [location, x['category'], x['location']['latitude'], x['location']['longitude'], x['month']]
            s = ""
            for x in input:
                s += x
            
            p_key = hashlib.sha256(s.encode()).hexdigest()
            input.insert(0, p_key)
            
            r.append(tuple(input))
            
    return r
        
def store_dropdown_data(locations):
    r = []
    for location in locations:
        df_ = df[df['city'] == location]
        data = fetch_data(df_.lat, df_.lng)
        input = [location, str(len(data))]
        s = ""
        for x in input:
            s += x
            
        p_key = hashlib.sha256(s.encode()).hexdigest()
        input.insert(0, p_key)
        
        r.append(tuple(input))

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
            input = [location, i_[i], str(df_['category'][i])]
            s = ""
            for x in input:
                s += x
            
            p_key = hashlib.sha256(s.encode()).hexdigest()
            input.insert(0, p_key)
            
            r.append(tuple(input))
            
    return r


cnx = mysql.connector.connect(
                user='root',
                password='rootuser',
                host='127.0.0.1',
                database='ukgovcrime')

cursor = cnx.cursor()

insert_clean_data = ("REPLACE INTO cleaned_data (hash, location, category, lat, lng, month) VALUES (%s, %s, %s, %s, %s, %s)")

r = store_cleaned_data(locations)
for t in r:
    cursor.execute(insert_clean_data, t)

insert_category_data = ("REPLACE INTO category_data (hash, location, category, count) VALUES (%s, %s, %s, %s)")

r = store_category_data(locations)
for t in r:
    cursor.execute(insert_category_data, t)

insert_dropdown_data = ("REPLACE INTO dropdown_data (hash, location, count) VALUES (%s, %s, %s)")

r = store_dropdown_data(locations)
for t in r:
    cursor.execute(insert_dropdown_data, t)

cnx.commit()
cursor.close()
cnx.close()

# DB SCHEMA

# table cleaned_data

# location varchar, category varchar, lat varchar, lng varchar, month varchar


# table dropdown_data

# hash varchar, count varchar, other stats...


# table category_data

# location varchar, category varchar, count varchar




    
    




