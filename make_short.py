#!/usr/bin/env python3
"""Build a science-and-facts YouTube Short with Piper, FFmpeg and Whisper."""
import argparse, json, re, subprocess, textwrap, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS, OUT = ROOT / "assets", ROOT / "output"
WORK = OUT / "work"
VOICE = "en_GB-alan-medium"
VOICE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/"

# Fact scripts are deliberately short enough for a 30-second Short.
# Each entry includes a primary institutional source for human fact-checking.
TOPICS = [
    {
        "title": "Venus: the backwards world",
        "slug": "venus",
        "narration": "Venus spins so slowly that one rotation takes about 243 Earth days. Its trip around the Sun takes only about 225 days. That means a Venus day, measured by one full rotation, is longer than its year. Venus also rotates in the opposite direction to most planets. Scientists are still studying how this unusual world evolved.",
        "source": "https://science.nasa.gov/venus/",
        "scenes": [
            ("PLANET VENUS", "A STRANGE WORLD", "Our neighbouring planet hides an unusual clock"),
            ("243 EARTH DAYS", "ONE FULL SPIN", "Venus rotates extremely slowly"),
            ("225 EARTH DAYS", "ONE ORBIT", "Its year is shorter than its rotation"),
            ("RETROGRADE", "BACKWARDS SPIN", "Venus rotates opposite to most planets"),
            ("A MYSTERY", "STILL STUDYING", "Its history is an active area of research"),
        ],
    },
    {
        "title": "Neutron stars: matter pushed to extremes",
        "slug": "neutron-stars",
        "narration": "A neutron star is the crushed core left behind by some exploding stars. It can contain more mass than the Sun, packed into a sphere only around twenty kilometres wide. Matter there is incredibly dense. A small amount would have an enormous mass on Earth. These objects help scientists test physics under extreme conditions.",
        "source": "https://science.nasa.gov/universe/stars/neutron-stars/",
        "scenes": [
            ("AFTER A SUPERNOVA", "A STELLAR CORE", "Some stars leave behind a neutron star"),
            ("ABOUT 20 KM", "CITY-SIZED", "An entire star's core in a tiny sphere"),
            ("MORE THAN THE SUN", "EXTREME MASS", "Some neutron stars outweigh our Sun"),
            ("INCREDIBLE DENSITY", "MATTER COMPRESSED", "Atoms are pushed into extraordinary conditions"),
            ("COSMIC LABORATORY", "TESTING PHYSICS", "Scientists study matter at its limits"),
        ],
    },
    {
        "title": "The deep ocean: Earth's hidden world",
        "slug": "deep-ocean",
        "narration": "Most of Earth's ocean is still unexplored in detail. Far below the surface, sunlight fades away and pressure rises dramatically. Yet life survives around some deep-sea hydrothermal vents, where ecosystems can rely on chemical energy instead of sunlight. The deep ocean is not empty darkness. It is a place where scientists continue to discover remarkable life.",
        "source": "https://oceanexplorer.noaa.gov/facts/exploration.html",
        "scenes": [
            ("EARTH'S OCEAN", "A HIDDEN WORLD", "Vast regions remain poorly explored"),
            ("NO SUNLIGHT", "THE DEEP", "Sunlight disappears with depth"),
            ("HIGH PRESSURE", "EXTREME CONDITIONS", "Water pressure increases far below the surface"),
            ("HYDROTHERMAL VENTS", "LIFE WITHOUT SUNLIGHT", "Some ecosystems use chemical energy"),
            ("NEW DISCOVERIES", "STILL EXPLORING", "Researchers continue to find unusual species"),
        ],
    },
    {
        "title": "Lightning: hotter than the Sun's surface",
        "slug": "lightning",
        "narration": "A lightning channel can heat the surrounding air to around thirty thousand degrees Celsius for a brief moment. That is several times hotter than the visible surface of the Sun. The sudden heating makes the air expand rapidly, creating the sound we hear as thunder. Lightning is powerful, unpredictable, and best observed from a safe place indoors.",
        "source": "https://www.weather.gov/safety/lightning-science",
        "scenes": [
            ("A STORM", "LIGHTNING", "A powerful electrical discharge in the atmosphere"),
            ("30,000°C", "EXTREME HEAT", "The channel heats surrounding air briefly"),
            ("HOTTER THAN THE SUN'S SURFACE", "A SURPRISING COMPARISON", "The Sun's visible surface is much cooler"),
            ("RAPID EXPANSION", "THUNDER", "Heated air expands and creates a shock wave"),
            ("STAY INDOORS", "RESPECT THE STORM", "Watch lightning from a safe location"),
        ],
    },
    {
        "title": "The James Webb Space Telescope",
        "slug": "james-webb",
        "narration": "The James Webb Space Telescope observes the universe mainly in infrared light. Its giant segmented mirror is about six and a half metres wide. Webb studies the atmospheres of distant planets, stars being born, and some of the earliest galaxies. It does not travel to those galaxies. It collects faint light that has crossed space for billions of years.",
        "source": "https://science.nasa.gov/mission/webb/",
        "scenes": [
            ("SPACE OBSERVATORY", "JAMES WEBB", "A telescope designed to see infrared light"),
            ("6.5 METRES", "GIANT MIRROR", "Its segmented primary mirror gathers faint light"),
            ("INFRARED", "INVISIBLE TO OUR EYES", "Webb detects wavelengths beyond visible light"),
            ("DISTANT WORLDS", "PLANET ATMOSPHERES", "It studies stars, galaxies and exoplanets"),
            ("ANCIENT LIGHT", "LOOKING BACK", "Some light has travelled for billions of years"),
        ],
    },
    {
        "title": "Octopuses: intelligent ocean animals",
        "slug": "octopus",
        "narration": "An octopus has three hearts. Two pump blood through the gills, while the third pumps it to the rest of the body. Its blood is blue because it uses a copper-containing protein called haemocyanin to carry oxygen. Octopuses are also known for problem-solving and camouflage. Their biology is very different from our own.",
        "source": "https://ocean.si.edu/ocean-life/invertebrates/octopuses",
        "scenes": [
            ("OCEAN LIFE", "THE OCTOPUS", "An animal with remarkable biology"),
            ("THREE HEARTS", "NOT JUST ONE", "Two hearts serve the gills; one serves the body"),
            ("BLUE BLOOD", "COPPER CHEMISTRY", "Haemocyanin carries oxygen"),
            ("CAMOUFLAGE", "MASTER OF DISGUISE", "Special skin cells help it change appearance"),
            ("PROBLEM SOLVERS", "UNUSUAL INTELLIGENCE", "Octopuses can learn and solve puzzles"),
        ],
    },
    {
        "title": "Why the sky looks blue",
        "slug": "blue-sky",
        "narration": "Sunlight looks white, but it contains many colours. As sunlight enters Earth's atmosphere, tiny gas molecules scatter shorter blue wavelengths more strongly than longer red wavelengths. That scattered blue light reaches our eyes from across the sky. At sunset, sunlight travels through more atmosphere, so much of the blue light is scattered away from the direct path.",
        "source": "https://spaceplace.nasa.gov/blue-sky/en/",
        "scenes": [
            ("SUNLIGHT", "MANY COLOURS", "White sunlight contains a spectrum of colours"),
            ("ATMOSPHERE", "TINY MOLECULES", "Air molecules scatter incoming sunlight"),
            ("BLUE LIGHT", "SCATTERED MORE", "Shorter blue wavelengths scatter strongly"),
            ("OUR VIEW", "A BLUE SKY", "Scattered light arrives from all directions"),
            ("SUNSET", "A LONGER PATH", "More atmosphere changes the colours we see"),
        ],
    },
    {
        "title": "How far is the Moon?",
        "slug": "moon-distance",
        "narration": "The Moon is about 384,400 kilometres from Earth on average. The distance is large enough that light takes a little over one second to travel between them. The Moon's orbit is not a perfect circle, so its distance changes during the month. Even our closest natural neighbour is farther away than it may look in the night sky.",
        "source": "https://science.nasa.gov/moon/",
        "scenes": [
            ("EARTH'S NEIGHBOUR", "THE MOON", "Our closest natural celestial neighbour"),
            ("384,400 KM", "AVERAGE DISTANCE", "The distance changes throughout its orbit"),
            ("1.3 SECONDS", "LIGHT TRAVEL TIME", "Moonlight takes just over a second to reach Earth"),
            ("ELLIPTICAL ORBIT", "NOT A PERFECT CIRCLE", "The Moon moves closer and farther away"),
            ("CLOSER THAN IT LOOKS", "A VAST DISTANCE", "Our nearest neighbour is still far away"),
        ],
    },
]

def run(cmd, **kwargs):
    print("+", " ".join(map(str, cmd)), flush=True)
    subprocess.run(list(map(str, cmd)), check=True, **kwargs)

def choose_topic(requested):
    if requested.lower() == "auto":
        day = datetime.now(timezone.utc).timetuple().tm_yday
        return TOPICS[(day - 1) % len(TOPICS)]
    key = requested.strip().lower()
    for topic in TOPICS:
        if key in (topic["slug"], topic["title"].lower()):
            return topic
    raise SystemExit("Unknown topic. Use --topic auto or one of: " + ", ".join(t["slug"] for t in TOPICS))

def getfont(size, bold=False):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(path, size) if Path(path).exists() else ImageFont.load_default()

def make_slide(index, topic_title, scene):
    kicker, title, subtitle = scene
    width, height = 1080, 1920
    im = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(im)
    for y in range(height):
        t = y / height
        draw.line((0, y, width, y), fill=(int(10 + 12*t), int(23 + 15*t), int(39 + 20*t)))
    draw.ellipse((660, -160, 1310, 490), fill=(32, 74, 94), outline=(100, 190, 210), width=8)
    draw.ellipse((-250, 1260, 470, 1980), fill=(31, 58, 76), outline=(100, 190, 210), width=6)
    draw.rounded_rectangle((65, 320, 1015, 1460), radius=42, fill=(229, 237, 231), outline=(104, 177, 184), width=8)
    draw.text((125, 405), "SCIENCE • FACTS", font=getfont(42, True), fill=(22, 83, 93))
    draw.line((125, 490, 955, 490), fill=(90, 157, 164), width=5)
    draw.text((125, 610), kicker, font=getfont(54, True), fill=(20, 100, 113))
    for j, line in enumerate(textwrap.wrap(title, 20)):
        draw.text((125, 770 + j*112), line, font=getfont(82, True), fill=(24, 38, 48))
    for j, line in enumerate(textwrap.wrap(subtitle, 34)):
        draw.text((125, 1120 + j*58), line, font=getfont(36), fill=(54, 69, 73))
    draw.rounded_rectangle((125, 1530, 955, 1635), radius=22, fill=(17, 111, 126))
    draw.text((160, 1555), f"SCIENCE SHORT • {index+1}/5", font=getfont(34, True), fill=(245, 250, 245))
    draw.text((65, 1790), topic_title.upper()[:52], font=getfont(28, True), fill=(220, 238, 235))
    path = WORK / f"slide_{index:02}.png"
    im.save(path)
    return path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="auto", help="auto or one of the science topic slugs")
    parser.add_argument("--music", default=str(ASSETS / "music.mp3"))
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    topic = choose_topic(args.topic)
    ASSETS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)

    for filename in (VOICE + ".onnx", VOICE + ".onnx.json"):
        path = ASSETS / filename
        if not path.exists():
            print("Downloading Piper voice:", filename, flush=True)
            urllib.request.urlretrieve(VOICE_URL + filename, path)

    narration = topic["narration"]
    (OUT / "narration.txt").write_text(narration, encoding="utf-8")
    (OUT / "topic.json").write_text(json.dumps({
        "title": topic["title"], "topic": topic["slug"],
        "primary_source_for_review": topic["source"],
        "note": "Verify claims against the source before publishing."
    }, indent=2), encoding="utf-8")

    voice = OUT / "voice.wav"
    run(["piper", "--model", ASSETS / (VOICE + ".onnx"),
         "--config", ASSETS / (VOICE + ".onnx.json"),
         "--output_file", voice], input=narration, text=True)

    clips = []
    for i, scene in enumerate(topic["scenes"]):
        still = make_slide(i, topic["title"], scene)
        clip = WORK / f"scene_{i:02}.mp4"
        clips.append(clip)
        run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", still,
             "-vf", "zoompan=z='min(zoom+0.0007,1.06)':d=180:s=1080x1920:fps=30,format=yuv420p",
             "-t", "6", "-an", "-c:v", "libx264", "-preset", "veryfast", clip])

    concat = WORK / "concat.txt"
    concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in clips), encoding="utf-8")
    visuals = WORK / "visuals.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", concat, "-c", "copy", visuals])

    from faster_whisper import WhisperModel
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(voice), word_timestamps=False)
    def stamp(seconds):
        ms = int(seconds * 1000)
        hours, ms = divmod(ms, 3600000)
        minutes, ms = divmod(ms, 60000)
        secs, ms = divmod(ms, 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"
    rows = []
    for number, segment in enumerate(segments, 1):
        rows.extend([str(number), f"{stamp(segment.start)} --> {stamp(segment.end)}", segment.text.strip(), ""])
    captions = OUT / "captions.srt"
    captions.write_text("\n".join(rows), encoding="utf-8")

    music = Path(args.music)
    if music.exists():
        # Input order: 0=video, 1=narration, 2=music.
        audio_args = ["-i", music, "-filter_complex",
                      "[1:a]volume=1.0[voice];[2:a]volume=0.12[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=2[audio]",
                      "-map", "0:v", "-map", "[audio]"]
    else:
        # Generate a quiet, simple tonal bed; this is not a licensed music track.
        audio_args = ["-f", "lavfi", "-i", "sine=frequency=110:duration=30",
                      "-filter_complex",
                      "[1:a]volume=1.0[voice];[2:a]volume=0.025,lowpass=f=220[bed];[voice][bed]amix=inputs=2:duration=first[audio]",
                      "-map", "0:v", "-map", "[audio]"]

    output = Path(args.output) if args.output else OUT / f"{topic['slug']}_science_short.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", visuals, "-i", voice, *audio_args,
         "-vf", f"subtitles={captions.as_posix()}:force_style='FontName=DejaVu Sans,FontSize=18,Bold=1,Outline=2,Shadow=1,Alignment=2,MarginV=170'",
         "-t", "30", "-r", "30", "-c:v", "libx264", "-preset", "veryfast",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", output])
    print("MP4 READY:", output.resolve())
    print("TOPIC SOURCE FOR HUMAN REVIEW:", topic["source"])

if __name__ == "__main__":
    main()
