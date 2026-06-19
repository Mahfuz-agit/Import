import os
import json
import re
from datetime import datetime
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

TOPIC_DISCOVERY_PROMPT = """
You are an autonomous elite knowledge curator.

Today's date: {date}

Your task: Decide what topics a truly elite, intellectually curious human SHOULD explore today.

Rules:
- Do NOT repeat obvious or common topics
- Think across all domains: science, philosophy, history, math, technology, society, art, cognition
- Choose topics that expand worldview, not just career skills
- Be unpredictable. Be bold. Be elite.

Return ONLY a JSON array of 10 topic search queries. Nothing else. No markdown.
Example: ["quantum decoherence explained", "stoic philosophy Marcus Aurelius", ...]
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

def discover_topics() -> list:
    prompt = TOPIC_DISCOVERY_PROMPT.format(date=datetime.utcnow().strftime("%B %d, %Y"))
    response = model.generate_content(prompt)
    text = response.text.strip()
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if not match:
        return []
    topics = json.loads(match.group())
    print(f"[TOPICS] Gemini chose: {topics}")
    return topics


def find_elite_video(topic: str) -> dict | None:
    try:
        prompt = SEARCH_PROMPT.format(topic=topic)
        response = model.generate_content(prompt)
        text = response.text.strip()

        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            print(f"[SKIP] No JSON found for: {topic}")
            return None

        data = json.loads(match.group())

        if float(data.get("score", 0)) < 9.7:
            print(f"[SKIP] Low score for: {topic}")
            return None

        data["curated_at"] = datetime.utcnow().isoformat()
        print(f"[OK] Found: {data['title']}")
        return data

    except Exception as e:
        print(f"[ERROR] {topic}: {e}")
        return None


def run():
    results = []

    print("Gemini is deciding today's elite topics...")
    topics = discover_topics()

    for topic in topics:
        print(f"\nSearching: {topic}")
        video = find_elite_video(topic)
        if video:
            results.append(video)

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
