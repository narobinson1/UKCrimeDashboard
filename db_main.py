import pandas as pd
import requests

locations = ['London', 'Manchester']
df = pd.read_csv("gb_latlon.csv")

def fetch_data(lat, lng):
    payload = {'lat':lat, 'lng':lng}
    r = requests.post("https://data.police.uk/api/crimes-street/all-crime", params=payload)
    res = r.json()
    return res
    
r = []
for location in locations:
    df_ = df[df['city'] == location]
    data = fetch_data(df_.lat, df_.lng)
    print(data[20])

# DB SCHEMA

# table raw_data

# location varchar, category varchar, lat varchar, lng varchar, month varchar


# table dropdown_data

# hash varchar, total_counts varchar, other stats...


# table category_data

# location varchar, category varchar, count varchar





    
    




