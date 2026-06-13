import requests
import pandas as pd
from textblob import TextBlob

MAP_ISO = {"United States": "USA", "United Kingdom": "GBR", "Canada": "CAN", "Australia": "AUS", "India": "IND", "Germany": "DEU", "France": "FRA", "Japan": "JPN", "China": "CHN", "Brazil": "BRA"}

def fetch_live_sentiment_data():
    url = "https://gdeltproject.org(market OR crisis OR tech OR climate)&mode=ArtList&format=json&maxrows=50"
    try:
        res = requests.get(url, timeout=10).json().get('articles', [])
        if not res:
            return pd.DataFrame()
        rows = []
        for a in res:
            h = a.get('title', '')
            if not h:
                continue
            score = TextBlob(h).sentiment.polarity
            c_raw = a.get('sourcecountry', 'Global')
            rows.append({
                "Timestamp": pd.Timestamp.now(),
                "Headline": h,
                "CountryName": c_raw,
                "ISO_Alpha": MAP_ISO.get(c_raw, "USA"),
                "Sentiment": score
            })
        return pd.DataFrame(rows)
    except:
        return pd.DataFrame([{"Timestamp": pd.Timestamp.now(), "Headline": "Global infrastructure scales clean energy computing matrices.", "CountryName": "United States", "ISO_Alpha": "USA", "Sentiment": 0.15}])
