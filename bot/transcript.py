import json
import os
from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_id: str) -> str:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US"])
        text = " ".join([t["text"] for t in transcript])
        print(f"[OK] Transcript fetched: {video_id}")
        return text
    except Exception as e:
        print(f"[ERROR] No transcript for {video_id}: {e}")
        return ""


def run():
    with open("data/videos.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for video in data["videos"]:
        vid = video.get("video_id", "")
        if not vid:
            continue
        transcript = get_transcript(vid)
        video["transcript"] = transcript[:8000]  # Gemini context limit

    with open("data/videos.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\nDone. Transcripts added.")


if __name__ == "__main__":
    run()
