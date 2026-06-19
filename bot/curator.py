import os
import json
import re
import time
from datetime import datetime
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

TOPIC_DISCOVERY_PROMPT = """
You are an autonomous elite knowledge curator.

Today's date: {date}

Decide what topics a truly elite, intellectually curious human SHOULD explore today.

Rules:
- Think across ALL domains: science, philosophy, history, math, technology, society, art, cognition
- No obvious or common topics
- Expand worldview, not just career skills
- Be unpredictable. Be bold.

Return ONLY a JSON array of 5 topic search queries. Nothing else. No markdown.
Example: ["quantum decoherence explained", "stoic philosophy Marcus Aurelius"]
"""

SEARCH_PROMPT = """
You are an elite knowledge curator. Find the single best educational YouTube video for: "{topic}"

Rules:
- Must be a REAL YouTube video with a real URL
- Must score 9.7 or above out of 10
- Prefer: university lectures, expert talks, Nobel laureates, pioneer researchers
- Reject: clickbait, oversimplified content, entertainment

Respond ONLY in this exact JSON format, nothing else:
{{
  "title": "video title",
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "video_id": "VIDEO_ID",
  "channel": "channel name",
  "topic": "{topic}",
  "why_elite": "2 sentence reason why this is 9.7+ quality",
  "score": 9.8
}}
"""

def call_gemini(prompt: str) -> str:
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"[RETRY {attempt+1}] {e}")
            time.sleep(30)
    return ""


def discover_topics() -> list:
    prompt = TOPIC_DISCOVERY_PROMPT.format(date=datetime.utcnow().strftime("%B %d, %Y"))
    text = call_gemini(prompt)
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if not match:
        return []
    topics = json.loads(match.group())
    print(f"[TOPICS] {topics}")
    return topics


def find_elite_video(topic: str) -> dict | None:
    try:
        text = call_gemini(SEARCH_PROMPT.format(topic=topic))
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            print(f"[SKIP] No JSON: {topic}")
            return None

        data = json.loads(match.group())

        if float(data.get("score", 0)) < 9.7:
            print(f"[SKIP] Low score: {topic}")
            return None

        data["curated_at"] = datetime.utcnow().isoformat()
        print(f"[OK] {data['title']}")
        return data

    except Exception as e:
        print(f"[ERROR] {topic}: {e}")
        return None


def run():
    results = []

    print("Gemini deciding today's topics...")
    topics = discover_topics()
    time.sleep(20)

    for topic in topics:
        print(f"\nSearching: {topic}")
        video = find_elite_video(topic)
        if video:
            results.append(video)
        time.sleep(15)

    os.makedirs("data", exist_ok=True)
    with open("data/videos.json", "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": datetime.utcnow().isoformat(),
            "total": len(results),
            "videos": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\nDone. {len(results)} elite videos curated.")


if __name__ == "__main__":
    run()
