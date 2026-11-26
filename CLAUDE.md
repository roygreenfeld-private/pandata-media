# Pandata media repo (Instagram @haya___data)

Hebrew Instagram account that explains data with the panda mascot Pandata (פנדאטה). Work on branch `media`.
Raw URL for any file: `https://raw.githubusercontent.com/roygreenfeld-private/pandata-media/media/<path>`

## Setup in a fresh session
```bash
git clone --depth 1 -b media https://github.com/roygreenfeld-private/pandata-media /home/claude/pandata-media
cp /home/claude/pandata-media/tools/* /home/claude/
cp /home/claude/pandata-media/assets/images/* /home/claude/
mkdir -p /home/claude/ig/stories && cp /home/claude/pandata-media/assets/images/pandata_curious_9x16.jpg /home/claude/ig/
cd /home/claude
```
The tools expect to run from /home/claude (font path /home/claude/rubik.ttf).

## Layout
- `reels/` final reels. `*_c.mp4` = version with the cover appended as a 0.2 s last frame (use these in Buffer, with `thumbnailOffset` = duration ms − 120).
- `stories/` story images 1080x1920. `covers/` reel covers. `highlights/` profile highlight covers.
- `assets/images/` Pandata stills for backgrounds. `assets/clips/` Pandata video clips (intro/outro/reactions/topic clips).
- `tools/` scripts:
  - `stories2.py` → `make2(src, out, tag, title_lines, body_lines, code_lines, footer, dark_bg, chips)` builds a story.
  - `ig.py` → `cover(src, crop_box, title_lines, number, out)` builds a reel cover.
  - `reelkit.py spec.json` builds a reel (intro clip → graphics with captions → outro clip). `add_cover(video, cover, out)` returns thumbnailOffset.
  - `titles.py` fonts/colors; `captions.py` speech timing.

## Content rules (from the account owner)
- Hebrew, short, flowing, correct. Technical terms in English letters (SQL, pipeline, Airflow).
- Stories: technical tips with real code (SQL, Excel, Python, Pandas) and tool concepts (Airflow, Spark, Warehouse/Lake, dbt, APIs). Tool-name chips under the card. No logos. No statistics topics, no shallow trivia.
- Reels: the topic fills the screen; Pandata appears only at the start, the end, and maybe one short reaction. Full captions of the whole narration, style B (white text, dark-teal outline, Rubik). Real Hebrew tables/code/graphs.
- Narration: ElevenLabs, voice Nimrod `ZiofZHcEBTn5sRySe5h8`, model `eleven_v4`, generations_count 1. Write the mascot name as "Pandata" in English letters. Check every word before generating; credits are limited. If credits run out, stop and tell the owner.
- Seedance prompts: never "jumps/hops/pops in from below" (content filter); use "walks in from the side". Mouth closed, no text, no dialogue.
- Every reel posted from Buffer must have a cover (appended last frame) and a caption.

## Schedules (claude.ai project doc `claude/posting-schedule.md` is the source of truth)
Cadence: story 09:30, reel 13:00, story 21:00 (Asia/Jerusalem). Buffer free plan: max 10 scheduled posts.
