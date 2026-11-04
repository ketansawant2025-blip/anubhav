"""Fetch anubhav videos from YouTube, sort into categories, write data.json + data.js.
Needs a free YouTube Data API key in env var YT_API_KEY. Run daily via GitHub Actions."""
import json, os, re, urllib.parse, urllib.request

KEY = os.environ["YT_API_KEY"]
BASE = os.path.dirname(os.path.abspath(__file__))
load = lambda n, d: json.load(open(os.path.join(BASE, n), encoding="utf-8")) if os.path.exists(os.path.join(BASE, n)) else d
cfg, cats, overrides = load("config.json", {}), load("categories.json", {}), load("overrides.json", {})
old = {v["id"]: v for v in load("data.json", [])}

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except Exception:
    YouTubeTranscriptApi = None

def api(endpoint, **p):
    p["key"] = KEY
    url = f"https://www.googleapis.com/youtube/v3/{endpoint}?" + urllib.parse.urlencode(p)
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)

def playlist_items(pid):
    token = None
    while True:
        p = dict(part="snippet", playlistId=pid, maxResults=50)
        if token: p["pageToken"] = token
        d = api("playlistItems", **p)
        yield from d.get("items", [])
        token = d.get("nextPageToken")
        if not token: break

def transcript(vid):
    if not YouTubeTranscriptApi: return ""
    try:
        t = YouTubeTranscriptApi().fetch(vid, languages=["mr", "hi", "en"])
        return " ".join(s.text for s in t)[:6000]
    except Exception:
        return ""  # captions missing or blocked: description is used instead

def guess_lang(text, default):
    if re.search(r"[\u0900-\u097F]", text):
        marathi = len(re.findall(r"आहे|आहेत|मी |ला |झाले|केले|होते|नाही|तुम्ही", text))
        return "Marathi" if marathi >= 2 or default == "Marathi" else ("Hindi" if default != "Regional" else "Marathi")
    return default

def categorize(text):
    t = text.lower()
    best, score = "Beyond Expectations", 0
    for c, words in cats.items():
        s = sum(t.count(w.lower()) for w in words)
        if s > score: best, score = c, s
    return best

kw = [k.lower() for k in cfg.get("anubhav_keywords", [])]
sources = [(c["id"], c["lang"], None) for c in cfg.get("channels", [])]
sources += [(None, "", p) for p in cfg.get("playlists", [])]

found = {}
for cid, lang, pid in sources:
    force = pid is not None
    for it in playlist_items(pid or "UU" + cid[2:]):
        s = it["snippet"]
        vid = s["resourceId"]["videoId"]
        if s["title"] in ("Private video", "Deleted video"): continue
        blob = (s["title"] + " " + s.get("description", "")).lower()
        if force or any(k in blob for k in kw):
            found[vid] = (s, lang or "English")

for vid, (s, lang) in found.items():
    if vid in old:
        old[vid]["category"] = overrides.get(vid, old[vid]["category"]); continue
    text = (s.get("description", "").strip() + "\n\n" + transcript(vid)).strip()
    old[vid] = {
        "id": vid, "title": s["title"], "date": s["publishedAt"][:10],
        "language": guess_lang(s["title"] + " " + text, lang),
        "category": overrides.get(vid) or categorize(s["title"] + " " + text),
        "text": text, "url": f"https://www.youtube.com/watch?v={vid}",
        "thumb": f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg",
    }

data = sorted(old.values(), key=lambda v: v["date"], reverse=True)
json.dump(data, open(os.path.join(BASE, "data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(os.path.join(BASE, "data.js"), "w", encoding="utf-8").write("window.ANUBHAV_DATA = " + json.dumps(data, ensure_ascii=False) + ";")
print(f"{len(data)} anubhav saved")
