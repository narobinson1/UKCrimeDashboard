import pandas as pd
import requests
import hashlib
import mysql.connector

df = pd.read_csv("gb_latlon.csv")
locations = list(df['city'])[:10]


d = []

for x in range(24):
    l = ["20"]
    if x < 10:
        l.append("0")
        l.append(str(x))
        l.append("-")
        l_ = l[:]
    else:
        l.append(str(x))
        l.append("-")
        l_ = l[:]
        
    for j in range(1, 13):
        if j < 10:
            l_.append("0")
            l_.append(str(j))
            d.append(''.join(l_))
            l_ = l[:]
        else:
            l_.append(str(j))
            d.append(''.join(l_))
            l_ = l[:]

def fetch_data(lat, lng, date):
        payload = {'lat':lat, 'lng':lng, 'date':date}
        r = requests.post("https://data.police.uk/api/crimes-street/all-crime", params=payload)
        if r.status_code == 404:
            return ""
        else:
            res = r.json()
            return res

def store_cleaned_data(locations):
    r = []
    for location in locations:
        df_ = df[df['city'] == location]
        lat = float(df_.lat)
        lng = float(df_.lng)

        p = int(df_.population)

        for x in d[250:]:
            data = fetch_data(lat, lng, x)
            t = len(data)
            if t != 0:
                for i in data:
                    c = i['category']
                    m = x
                    input = [location, c, str(lat), str(lng), m]

                    s = ""
                    for j in input:
                        s+=j

                    p_key = hashlib.sha256(s.encode()).hexdigest()
                    input.insert(0, p_key)
                    r.append(tuple(input))
                
        return r


def store_dropdown_data(locations):
    r = []
    for location in locations:
        df_ = df[df['city'] == location]
        lat = float(df_.lat)
        lng = float(df_.lng)

        p = int(df_.population)

        for x in d[250:]:
            data = fetch_data(lat, lng, x)
            t = len(data)
            if t != 0:
                f = t/p
                m = x
                input = [location, str(t), str(f), str(lat), str(lng), m]

                s = ""
                for j in input:
                    s+=j

                p_key = hashlib.sha256(s.encode()).hexdigest()
                input.insert(0, p_key)
                r.append(tuple(input))
    return r

def store_category_data(locations):
    r = []
    for location in locations:
        df_ = df[df['city'] == location]
        lat = float(df_.lat)
        lng = float(df_.lng)

        p = int(df_.population)

        for x in d[250:]:
            data = fetch_data(lat, lng, x)
            t = len(data)
            if t != 0:
                df_ = pd.DataFrame(data)
                df_ = df_['category'].value_counts()
                df_ = pd.DataFrame(df_)
                
                i_ = []
                t_ = len(data)
                if t != 0:
                    i_ = []
                    for j in df_.index:
                        i_.append(j)

                    
                    for i in range(len(df_)):

                        t = df_['category'][i]
                        f = t/p
                        
                        input = [location, i_[i], str(t), str(f), x]
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

insert_category_data = ("REPLACE INTO category_data (hash, location, category, total, fractional, month) VALUES (%s, %s, %s, %s, %s, %s)")

r = store_category_data(locations)
for t in r:
    cursor.execute(insert_category_data, t)

insert_dropdown_data = ("REPLACE INTO dropdown_data (hash, location, total, fractional, lat, lng, month) VALUES (%s, %s, %s, %s, %s, %s, %s)")

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

# hash varchar, total varchar, fractional varchar, lat varchar, lng varchar, month varchar


# table category_data

# location varchar, category varchar, total varchar, fractional varchar, month varchar




    
    




