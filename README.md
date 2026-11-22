# Science Facts YouTube Shorts Automation

A scheduled build pipeline for short science explainers.

## What it currently automates

- Selects one topic per day from a curated science-facts rotation.
- Uses an original short narration and five matching motion-graphic cards.
- Generates British-English narration with Piper TTS.
- Creates subtitles with faster-whisper.
- Renders a vertical 1080x1920 MP4 with FFmpeg.
- Writes a topic/source review file and uploads the MP4 plus review files as a GitHub Actions artifact.

## Daily schedule

GitHub Actions is configured for 02:00 UTC daily (09:00 Cambodia time). It selects the next topic using the day of year. Artifacts are retained for seven days.

## Run a topic manually

Open **Actions → Daily science Short → Run workflow** and enter one of:

- `venus`
- `neutron-stars`
- `deep-ocean`
- `lightning`
- `james-webb`
- `octopus`
- `blue-sky`
- `moon-distance`

Or enter `auto`.

## Local build

Install FFmpeg and Python dependencies:

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg fonts-dejavu-core
pip install -r requirements.txt piper-tts
python make_short.py --topic auto
```

The MP4 and review files are written to `output/`.

## Important limits and review

- The current visuals are original animated graphic cards, not stock footage or generated cinematic video.
- Topics are selected from a curated fact library; live vidIQ research and AI-generated research scripts are not connected yet.
- The Piper voice is synthetic. Check the specific voice model and voice-data licence before any commercial use.
- Review every fact against the source URL in `output/topic.json`, and review pronunciation, captions, audio and video before publishing.
- The pipeline does **not** upload or schedule videos to YouTube. No YouTube OAuth connection or upload secret is configured.
- GitHub Actions minutes, model downloads and free service quotas are limited; this is not unlimited hosting.
- No video is guaranteed to be monetized. YouTube makes the final eligibility and policy decisions.
