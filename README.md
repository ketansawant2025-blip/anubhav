# Aniruddha Bapu Anubhav Dashboard (free)

One simple page: Bapu's photo, search box, category chips (Farmers, Education, Accident, Health, Finance, Family, Beyond Expectations) and a language filter (English / Hindi / Marathi).

## One-time setup (about 15 minutes, all free)

1. **Photo**: put Bapu's photo in this folder and name it `bapu.jpg`.
2. **Marathi channel**: open `config.json` and add the Marathi channel next to the other two:
   `{ "name": "...", "id": "UCxxxxxxxxxxxxxxxxxxxxxx", "lang": "Marathi" }`
   (Channel ID: open the channel on YouTube > About > Share channel > Copy channel ID.)
3. **Anubhav playlists (recommended)**: if the channels have playlists of anubhav, paste their IDs (the `PLxxxx` part of the link) into `"playlists"` in `config.json`. Every video in them is treated as anubhav. Without playlists, the updater picks videos whose title or description contains words like "anubhav" or "अनुभव".
4. **YouTube API key (free)**: go to console.cloud.google.com, create a project, enable "YouTube Data API v3", then Credentials > Create API key.
5. **GitHub**: create a free account and a new public repository. Upload all files from this folder (including the `.github` folder).
6. In the repository: Settings > Secrets and variables > Actions > New secret. Name: `YT_API_KEY`, value: your key.
7. Settings > Pages > Source: "Deploy from a branch", branch `main`, folder `/ (root)`. Your dashboard link appears there.
8. Actions tab > "Update anubhav" > Run workflow. After that it runs by itself every day at 7:00 AM IST, adds new anubhav and sorts them into categories.

## Fixing a wrong category
Sorting is keyword-based. To fix one, add the video ID to `overrides.json`:
`{ "VIDEO_ID": "Health" }`
To improve sorting overall, add words to `categories.json`.

## Notes
- Anubhav text comes from the video description, plus captions when YouTube provides them (captions can be blocked from GitHub servers; then only the description is used).
- Anything that matches no category goes to "Beyond Expectations".
- You can also open `index.html` directly on your computer; it works offline with whatever is in `data.js`.
