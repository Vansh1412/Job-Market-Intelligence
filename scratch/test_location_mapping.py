"""
Design and test location normalization for India jobs.
"""
import pandas as pd
import re

df = pd.read_parquet("scratch/raw_india_cache.parquet")

CITY_STATE_MAP = {
    "bengaluru": ("Bengaluru", "Karnataka"),
    "bangalore": ("Bengaluru", "Karnataka"),
    "hyderabad": ("Hyderabad", "Telangana"),
    "secunderabad": ("Hyderabad", "Telangana"),
    "pune": ("Pune", "Maharashtra"),
    "mumbai": ("Mumbai", "Maharashtra"),
    "navi mumbai": ("Mumbai", "Maharashtra"),
    "thane": ("Mumbai", "Maharashtra"),
    "mumbai suburban": ("Mumbai", "Maharashtra"),
    "chennai": ("Chennai", "Tamil Nadu"),
    "madras": ("Chennai", "Tamil Nadu"),
    "gurugram": ("Gurugram", "Haryana"),
    "gurgaon": ("Gurugram", "Haryana"),
    "noida": ("Noida", "Uttar Pradesh"),
    "greater noida": ("Noida", "Uttar Pradesh"),
    "delhi": ("Delhi NCR", "Delhi"),
    "new delhi": ("Delhi NCR", "Delhi"),
    "delhi / ncr": ("Delhi NCR", "Delhi"),
    "delhi ncr": ("Delhi NCR", "Delhi"),
    "kolkata": ("Kolkata", "West Bengal"),
    "ahmedabad": ("Ahmedabad", "Gujarat"),
    "jaipur": ("Jaipur", "Rajasthan"),
    "coimbatore": ("Coimbatore", "Tamil Nadu"),
    "vadodara": ("Vadodara", "Gujarat"),
    "baroda": ("Vadodara", "Gujarat"),
    "kochi": ("Kochi", "Kerala"),
    "cochin": ("Kochi", "Kerala"),
    "surat": ("Surat", "Gujarat"),
    "nagpur": ("Nagpur", "Maharashtra"),
    "lucknow": ("Lucknow", "Uttar Pradesh"),
    "chandigarh": ("Chandigarh", "Chandigarh"),
    "mohali": ("Mohali", "Punjab"),
    "indore": ("Indore", "Madhya Pradesh"),
    "bhopal": ("Bhopal", "Madhya Pradesh"),
    "faridabad": ("Faridabad", "Haryana"),
    "ghaziabad": ("Ghaziabad", "Uttar Pradesh"),
    "nashik": ("Nashik", "Maharashtra"),
    "aurangabad": ("Aurangabad", "Maharashtra"),
    "bhubaneswar": ("Bhubaneswar", "Odisha"),
    "trivandrum": ("Thiruvananthapuram", "Kerala"),
    "thiruvananthapuram": ("Thiruvananthapuram", "Kerala"),
    "visakhapatnam": ("Visakhapatnam", "Andhra Pradesh"),
    "vizag": ("Visakhapatnam", "Andhra Pradesh"),
    "vijayawada": ("Vijayawada", "Andhra Pradesh"),
    "patna": ("Patna", "Bihar"),
    "mysuru": ("Mysuru", "Karnataka"),
    "mysore": ("Mysuru", "Karnataka"),
    "remote": ("Remote", "Remote"),
}

# Ordered priority for matching recognized cities
RECOGNIZED_KEYS = sorted(CITY_STATE_MAP.keys(), key=lambda x: -len(x))

def normalize_location(loc_raw):
    if pd.isnull(loc_raw):
        return None, None
    s = str(loc_raw).strip()
    if not s:
        return None, None
        
    s_lower = s.lower()
    
    # Check for pure remote
    if s_lower == "remote" or s_lower.startswith("remote -"):
        # Check if remote has a city e.g. "Remote - Bengaluru"
        for k in RECOGNIZED_KEYS:
            if k != "remote" and re.search(r'\b' + re.escape(k) + r'\b', s_lower):
                c, st = CITY_STATE_MAP[k]
                return c, st
        return "Remote", "Remote"
        
    # Strip prefixes like Hybrid -
    clean_s = re.sub(r'^(hybrid\s*-\s*|work\s*from\s*home\s*-\s*)', '', s_lower).strip()
    
    # Deterministic primary-city rule:
    # First, split by comma or slash to see if first token matches a recognized city
    parts = re.split(r'[,/]', clean_s)
    first_part = parts[0].strip()
    for k in RECOGNIZED_KEYS:
        if k != "remote" and re.search(r'\b' + re.escape(k) + r'\b', first_part):
            c, st = CITY_STATE_MAP[k]
            return c, st
            
    # If first token didn't match, check entire string for first recognized metro
    for k in RECOGNIZED_KEYS:
        if k != "remote" and re.search(r'\b' + re.escape(k) + r'\b', clean_s):
            c, st = CITY_STATE_MAP[k]
            return c, st
            
    # If it has "remote" anywhere
    if "remote" in clean_s or "work from home" in clean_s:
        return "Remote", "Remote"
        
    # Fallback: Capitalize first part if not empty
    raw_first = re.split(r'[,/]', s)[0].strip()
    # Strip Hybrid prefix from raw
    raw_clean = re.sub(r'^(Hybrid\s*-\s*|Remote\s*-\s*)', '', raw_first).strip()
    return raw_clean.title() if raw_clean else None, None

cities = []
states = []
for loc in df["location"]:
    c, st = normalize_location(loc)
    cities.append(c)
    states.append(st)

df["norm_city"] = cities
df["norm_state"] = states

print("--- TOP 25 NORMALIZED CITIES ---")
print(df["norm_city"].value_counts().head(25))
print(f"\nCity coverage: {df['norm_city'].notnull().sum():,} / {len(df):,} ({df['norm_city'].notnull().sum()/len(df)*100:.2f}%)")

print("\n--- TOP 15 NORMALIZED STATES ---")
print(df["norm_state"].value_counts().head(15))
print(f"\nState coverage: {df['norm_state'].notnull().sum():,} / {len(df):,} ({df['norm_state'].notnull().sum()/len(df)*100:.2f}%)")
