import os
import lzma
import json
import pandas as pd
from datetime import datetime, timezone
import instaloader
import re
from dotenv import load_dotenv
import time

load_dotenv()
USERNAME = os.getenv("USERNAME", "YOUR_USERNAME_HERE")

def safe_get(d, keys, default=None):
    for key in keys:
        if isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return default
    return d

def extract_email_from_text(text):
    matches = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text or "")
    return matches[0] if matches else ""

def get_profile_data(shortcode):
    L = instaloader.Instaloader()
    L.load_session_from_file(USERNAME)
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    profile = instaloader.Profile.from_username(L.context, post.owner_username)
    return {
        "username": profile.username,
        "biography": profile.biography,
    }

def truncate_text(text, max_length=255):
    return text[:max_length] if text and len(text) > max_length else text

def process_instagram_json(json_path):
    with lzma.open(json_path, "rt", encoding="utf-8") as f:
        data = json.load(f)
    post = safe_get(data, ["node"], data)
    caption = safe_get(post, ["edge_media_to_caption", "edges"], [])
    caption_text = caption[0]["node"]["text"] if caption else ""
    caption_text = truncate_text(caption_text)
    timestamp = safe_get(post, ["taken_at_timestamp"], 0)
    date = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if timestamp else ""
    shortcode = safe_get(post, ["shortcode"], "")
    post_url = f"https://www.instagram.com/p/{shortcode}/" if shortcode else ""
    statut = "new" if timestamp and (datetime.now(timezone.utc) - datetime.fromtimestamp(timestamp, tz=timezone.utc)).days < 30 else "old"
    likes = safe_get(post, ["edge_liked_by", "count"], 0)
    comments = safe_get(post, ["edge_media_to_comment", "count"], 0)
    profile_data = get_profile_data(shortcode)
    time.sleep(10)  # Add delay to avoid rate limiting
    username = profile_data.get("username", "")
    bio = profile_data.get("biography", "")
    email = extract_email_from_text(bio) or extract_email_from_text(caption_text)
    return {
        "username": username,
        "email": email,
        "bio": bio,
        "biography": bio,
        "caption": caption_text,
        "likes": likes,
        "comments": comments,
        "date": date,
        "post_url": post_url,
        "statut": statut
    }

def auto_adjust_column_widths(writer, df, sheet_name):
    worksheet = writer.sheets[sheet_name]
    for idx, col in enumerate(df.columns):
        series = df[col].astype(str)
        max_len = max(series.map(len).max(), len(str(series.name))) + 2
        worksheet.set_column(idx, idx, max_len)

def main():
    dossier = "downloads"
    toutes_donnees = []

    for fichier in os.listdir(dossier):
        if fichier.endswith(".json.xz"):
            chemin_json = os.path.join(dossier, fichier)
            try:
                donnees_post = process_instagram_json(chemin_json)
                if not donnees_post.get("post_url") or not donnees_post.get("username"):
                    continue
                toutes_donnees.append(donnees_post)
            except Exception as e:
                print("Erreur fichier", fichier, ":", e)

    if not toutes_donnees:
        print("Aucune donnée à exporter.")
        return

    df = pd.DataFrame(toutes_donnees)
    with pd.ExcelWriter("data.xlsx", engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Instagram Data')
        auto_adjust_column_widths(writer, df, 'Instagram Data')

    saleshandy_df = df.rename(columns={
        "username": "Name",
        "email": "Email",
        "bio": "Company Name",
        "post_url": "Website",
        "caption": "Notes",
        "date": "Created Date",
        "statut": "Status"
    })
    saleshandy_df["Source"] = "Instagram"
    colonnes = [
        "Name", "Email", "Company Name", "Website",
        "Status", "Source", "Notes", "Created Date"
    ]
    saleshandy_df = saleshandy_df[colonnes]
    with pd.ExcelWriter("contact.xlsx", engine='xlsxwriter') as writer:
        saleshandy_df.to_excel(writer, index=False, sheet_name='SalesHandy Format')
        auto_adjust_column_widths(writer, saleshandy_df, 'SalesHandy Format')

if __name__ == "__main__":
    main()
