import os
import json
import re
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

ANALYZE_PROMPT = """
You are an elite knowledge analyst.

Here is a YouTube video transcript:
---
{transcript}
---

Video title: {title}

Your job:
1. Write 5 elite-level key insights from this video (not summaries, actual deep insights)
2. Create a knowledge graph with 5 nodes — concepts that connect to each other

Respond ONLY in this exact JSON format, nothing else:
{{
  "key_insights": [
    "insight 1",
    "insight 2",
    "insight 3",
    "insight 4",
    "insight 5"
  ],
  "knowledge_graph": [
    {{"concept": "Concept A", "connects_to": ["Concept B", "Concept C"], "description": "one line"}},
    {{"concept": "Concept B", "connects_to": ["Concept A", "Concept D"], "description": "one line"}},
    {{"concept": "Concept C", "connects_to": ["Concept A", "Concept E"], "description": "one line"}},
    {{"concept": "Concept D", "connects_to": ["Concept B"], "description": "one line"}},
    {{"concept": "Concept E", "connects_to": ["Concept C"], "description": "one line"}}
  ]
}}
"""

def analyze_video(video: dict) -> dict:
    transcript = video.get("transcript", "")
    title = video.get("title", "")

    if not transcript:
        print(f"[SKIP] No transcript: {title}")
        video["key_insights"] = []
        video["knowledge_graph"] = []
        return video

    try:
        prompt = ANALYZE_PROMPT.format(transcript=transcript[:6000], title=title)
        response = model.generate_content(prompt)
        text = response.text.strip()

        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            print(f"[SKIP] No JSON: {title}")
            return video

        analysis = json.loads(match.group())
        video["key_insights"] = analysis.get("key_insights", [])
        video["knowledge_graph"] = analysis.get("knowledge_graph", [])
        print(f"[OK] Analyzed: {title}")

    except Exception as e:
        print(f"[ERROR] {title}: {e}")

    return video


def run():
    with open("data/videos.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    data["videos"] = [analyze_video(v) for v in data["videos"]]

    with open("data/videos.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\nDone. Analysis complete.")


if __name__ == "__main__":
    run()
