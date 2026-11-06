# Signal Stories

A short-video series on the history of information theory (Nyquist 1924 and 1928, Hartley 1928, Shannon 1948),
plus the small, testable pipeline that makes it. English and Mandarin versions, vertical 9:16.

```
topic -> script -> images -> voice -> assemble (ffmpeg) -> publish -> finance ledger
```

Every stage works out of the box in **offline mode** (no API keys); swap in real providers one stage at a time.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp config.example.yaml config.yaml
# ffmpeg must be installed and on PATH (brew install ffmpeg / apt install ffmpeg)

python3 -m shortform.pipeline list-topics
python3 -m shortform.pipeline run --topic bit-story --lang en
python3 -m shortform.pipeline run --topic bit-story --lang zh
```

Output lands in `output/<topic>/` (`output/<topic>-zh/` for Mandarin): `script.json`, `images/`, `voice/`,
`video.mp4`, and `publish.json` (the upload manifest, including the sources list).

## Topics

`topics/information_theory.yaml`, English and Mandarin: `bit-story`, `nyquist-limit`, `hartley-measure`,
`shannon-1948`, `shannon-hartley`. Each topic has `scenes` (`visual`, `caption`, `narration`, `*_zh`),
optional `series` / `palette` / `tags`, and a `sources:` list that is added to the upload description.
Items still to verify are noted at the top of the file. Add a series by adding another `topics/*.yaml`.

## Stages

| Stage | Module | Offline default | Real provider |
|---|---|---|---|
| Script | `script_gen.py` | Scenes from `topics/*.yaml` | Anthropic API (`ANTHROPIC_API_KEY`) |
| Images | `images.py` | Original flat illustrations drawn with Pillow | Google Imagen photos when `GEMINI_API_KEY` is set (`images.provider: auto`), with headline and subtitle drawn on top |
| Voice | `voice.py` | `auto`: edge-tts (internet), else macOS `say`, else silent | One clip per scene, so scene length follows the narration |
| Assemble | `assemble.py` | ffmpeg, 9:16, slow zoom, timed to narration | - |
| Publish | `publish.py` | Dry run, writes manifest | Add platform uploaders |
| Finance | `finance.py` | CSV ledger + summary | - |

## Voice and look

- `voice.provider: auto` tries `edge-tts` first (free, needs internet), then the macOS `say` voice (offline), then a silent track. The console prints which one was used.
- Pick a different voice with `voice.voice_name` (edge-tts, e.g. `en-US-GuyNeural`) or `voice.say_voice` (macOS, list with `say -v '?'`).
- If you copied `config.example.yaml` earlier, copy it again (or set `voice.provider: auto` and `images.provider: illustrated`) to pick up the new defaults.
- Scenes live in `topics/*.yaml`: `narration`, `caption` and `visual` (`telegraph wave bits channel formula timeline follow`; `formula` and `years` fields feed the formula and timeline visuals). Add a topic by copying one.
- Image sources: the built-in scenes are original illustrations; Google scenes are AI-generated pictures, not archival photographs; your own photos in `assets/` are yours. Disclose AI-generated content as the platform requires (the uploader already sends YouTube's flag), and only use photos you own or are licensed to use.

## Using your own photos

Put a picture in `assets/` (git-ignored, so it stays on your computer) and point a scene at it in `topics/*.yaml`:

```yaml
- {visual: bits, photo: shannon.jpg, fit: contain, caption: "...", narration: "..."}
```

`fit: contain` shows the whole photo on a blurred background (best for small or landscape photos); `fit: cover` crops it to 9:16.
If the file is missing, the scene falls back to a generated or illustrated image.
Only use images you own, that are public domain, or that you are licensed to use, and keep their attribution in the topic's `sources:`.

## Mandarin version

```bash
python3 -m shortform.pipeline run --topic bit-story --lang zh
```

- Uses the `narration_zh` / `caption_zh` / `title_zh` fields in `topics/*.yaml`, a Mandarin voice (`voice.voice_name_zh`, default `zh-CN-XiaoxiaoNeural`; male: `zh-CN-YunxiNeural`; macOS fallback `Tingting`) and Chinese subtitles (drawn with Noto Sans CJK, Hiragino Sans GB or PingFang).
- The upload gets a Chinese title, description and tags, and YouTube's language set to `zh-CN`.
- Set `language: zh` in `config.yaml` to make it the default.
- Have a native speaker review the Chinese text before publishing.
- If the macOS voice is missing, download "Tingting" in System Settings -> Accessibility -> Spoken Content -> System Voice -> Manage Voices.

### Choosing and tuning the Mandarin voice

```bash
python3 -m shortform.voice audition
open output/voice_samples
```

This makes a short sample in each of five Mandarin voices so you can pick one by ear. Set your choice in `config.yaml` as `voice.voice_name_zh`
(for example `zh-CN-YunxiNeural`). `python3 -m shortform.voice list` shows every Chinese voice. Set `voice.rate` (for example `"+10%"`) to speak faster.
If a word is mispronounced, add a `tts_zh` field to that scene in `topics/*.yaml` with a respelled version for the voice to read; the on-screen text stays unchanged.

## Photo scenes with Google

Set a key and run as usual; every scene's `image_prompt` in `topics/*.yaml` becomes a photo:

```bash
export GEMINI_API_KEY=your_key
python3 -m shortform.pipeline run --topic bit-story
```

- Get the key from Google AI Studio. Imagen may require billing to be enabled on the Google account; if every scene fails with HTTP 400, the error message printed in the console says why.
- `images.provider: auto` (default) uses photos when the key exists, otherwise the local illustrations.
  Use `google` to require photos, `illustrated` to never call the API.
- A scene whose photo fails (quota, network, bad key) falls back to its illustration and prints a warning.
- Photos are cached in `cache/images/` (git-ignored), so re-running a topic costs nothing; edit an `image_prompt` to get a new image.
- `images.google_model: auto` asks Google which image model your key can use (Imagen, else a Gemini image model). See the list with `python3 -m shortform.image_providers`, or set a model name yourself.
- Text (headline, subtitle) is drawn by this code, not by the image model.
- AI-generated pictures are not archival photographs. Disclose this to the platform (the uploader already sends the flag) and do not present them as documentary footage.

## Finance ledger

```bash
python3 -m shortform.finance add --kind cost --amount 4.50 --note "image credits"
python3 -m shortform.finance add --kind income --amount 12.00 --note "creator fund" --platform tiktok
python3 -m shortform.finance summary
```

Data is stored in `data/ledger.csv` on your computer. The `data/` folder is git-ignored, so your numbers are not pushed to GitHub.

## Publishing to YouTube Shorts

Default is a dry run. Real uploads are opt-in and start as **private** videos.

One-time setup:

1. [Google Cloud Console](https://console.cloud.google.com/) -> create a project -> enable **YouTube Data API v3**.
2. APIs & Services -> OAuth consent screen: choose External, add your own Google account as a **test user**.
3. Credentials -> Create credentials -> **OAuth client ID** -> type **Desktop app** -> download the JSON.
4. Save it as `secrets/client_secret.json` (the `secrets/` folder is git-ignored; never commit it).
5. Install and log in (the login opens a browser and saves `secrets/youtube_token.json`):

```bash
pip install -r requirements-youtube.txt
python3 -m shortform.pipeline auth-youtube
```

Upload:

```bash
python3 -m shortform.pipeline run --topic bit-story --upload
```

Notes:

- Check `publish.youtube.privacy` in `config.yaml` (`private` by default). Review the video in YouTube Studio, then set it public there.
- YouTube has in the past forced uploads from unverified API projects to private until the project passed an audit; Google's current reference page says unverified projects are not restricted. Unconfirmed either way, so do one private test upload first and check the result in YouTube Studio.
- Each upload costs about 1,600 of the default 10,000 daily quota units.
- The AI-content disclosure is sent automatically (`containsSyntheticMedia`).
- TikTok and Instagram Reels have no uploader yet; they are skipped.

## Notes

- When pasting commands into a Mac terminal, paste only the command lines (not any `#` comments).
- Check each platform's policy on AI-generated content and label it as required.
- Verify every historical claim in `topics/*.yaml` against a primary or reputable source before publishing, and list the sources in the topic's `sources:`; the script generator only uses what is in the topic file.
- Never commit `config.yaml` or API keys (they are git-ignored).

## Tests

```bash
pip install pytest && pytest -q
```
