# YouTube Auto Production

Starter pipeline for a 30-second vertical history Short using Piper TTS, FFmpeg, Pillow and Whisper captions.

## One-line build (Linux / Colab after dependencies are installed)

```bash
python make_short.py --topic "American Revolution"
```

Install once:

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg fonts-dejavu-core
pip install -r requirements.txt piper-tts
```

The MP4 is written to `output/american_revolution_short.mp4`. Whisper transcribes the generated voice and burns captions into the video. Add a properly licensed MP3 at `assets/music.mp3` to use your own background music; otherwise a quiet generated ambient tone is used.

## GitHub Actions
Open **Actions → Build documentary Short → Run workflow**. Download the resulting `american-revolution-short` artifact when the run finishes.

## Important
- This creates original graphic slides, not archival photographs or live footage.
- The default Piper voice is British English male Alan. Check the voice model card and voice-data licence before commercial use; the Piper software licence does not automatically cover voice data.
- Captions and historical claims need human review before publishing.
- No YouTube upload is automated. Review rights, policies and the final MP4 yourself.
- GitHub Actions and free Colab usage have limits; neither is unlimited.
