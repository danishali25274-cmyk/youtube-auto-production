# Facts Empire — Automated Science Shorts

GitHub Actions builds a vertical science Short every day and when production code changes.

## Automated pipeline
1. Select a science topic from the curated topic library (or choose one in Actions).
2. Download candidate video clips from Wikimedia Commons and keep only files whose metadata indicates public domain, CC0, CC BY or CC BY-SA licensing.
3. Save creator, source URL and licence details in \`output/asset_manifest.json\`.
4. Generate British-English narration with Piper.
5. Render 1080×1920 vertical scenes with FFmpeg; use moving footage when a suitable clip is found and animated graphics as fallback.
6. Generate word-level Whisper captions, burn them into the MP4, and export SRT.
7. Package the MP4 and review files as a GitHub Actions artifact for seven days.

## Run manually
Open **Actions → Daily science Short → Run workflow** and choose:
- \`water-resistant\`
- \`venus\`
- \`neutron-stars\`
- \`deep-ocean\`
- \`lightning\`
- \`james-webb\`
- \`octopus\`
- \`blue-sky\`
- \`moon-distance\`
- \`auto\`

## Local run
\`\`\`bash
sudo apt-get update && sudo apt-get install -y ffmpeg fonts-dejavu-core
pip install -r requirements.txt piper-tts
python fetch_footage.py water-resistant
python make_short.py --topic water-resistant
\`\`\`

## Honest limitations / required review
- Wikimedia Commons may not have a suitable clip for every scene. If none is found, the build falls back to original animated graphics; inspect the asset manifest before calling the result a real-footage edit.
- The Piper voice model is synthetic. Verify the specific model/data licence before commercial use; do not assume every voice model is monetization-safe.
- Music must be supplied as a separately licensed \`assets/music.mp3\`; if absent, the current renderer uses a simple generated tonal bed, not a commercial music track.
- vidIQ research is not part of the GitHub build yet. The connected vidIQ account currently has only two credits remaining, so do not spend credits without approval.
- The pipeline creates a review-ready artifact. It does not upload or schedule to YouTube. No YouTube OAuth / upload credential is configured, and publishing requires explicit approval.
- GitHub Actions usage is subject to GitHub account quotas. No unlimited free video generation or monetization is promised.
