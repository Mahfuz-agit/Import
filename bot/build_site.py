import json
import os
from datetime import datetime

def build_card(video: dict) -> str:
    title = video.get("title", "Unknown")
    url = video.get("url", "#")
    channel = video.get("channel", "")
    topic = video.get("topic", "")
    score = video.get("score", "")
    why_elite = video.get("why_elite", "")
    insights = video.get("key_insights", [])
    graph = video.get("knowledge_graph", [])

    insights_html = "".join([f"<li>{i}</li>" for i in insights])

    graph_html = ""
    for node in graph:
        concept = node.get("concept", "")
        desc = node.get("description", "")
        connects = ", ".join(node.get("connects_to", []))
        graph_html += f"""
        <div class="node">
            <strong>{concept}</strong>
            <span>{desc}</span>
            <small>→ {connects}</small>
        </div>"""

    return f"""
    <div class="card" onclick="toggleCard(this)">
        <div class="card-header">
            <div class="meta">
                <span class="topic">{topic}</span>
                <span class="score">⭐ {score}/10</span>
            </div>
            <h2><a href="{url}" target="_blank">{title}</a></h2>
            <p class="channel">{channel}</p>
            <p class="why">{why_elite}</p>
        </div>
        <div class="card-body">
            <div class="section">
                <h3>Elite Insights</h3>
                <ul>{insights_html}</ul>
            </div>
            <div class="section">
                <h3>Knowledge Graph</h3>
                <div class="graph">{graph_html}</div>
            </div>
        </div>
    </div>"""


def build_html(videos: list, updated_at: str) -> str:
    cards = "".join([build_card(v) for v in videos])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite Knowledge</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: #f5f5f0;
            color: #1a1a1a;
            padding: 2rem;
        }}
        header {{
            text-align: center;
            margin-bottom: 3rem;
        }}
        header h1 {{
            font-size: 2.5rem;
            font-weight: 800;
            letter-spacing: -1px;
        }}
        header p {{
            color: #666;
            margin-top: 0.5rem;
        }}
        .grid {{
            max-width: 900px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }}
        .card {{
            background: #ffffff;
            border-radius: 12px;
            padding: 1.5rem;
            cursor: pointer;
            border: 1px solid #e0e0e0;
            transition: box-shadow 0.2s;
        }}
        .card:hover {{ box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
        .meta {{
            display: flex;
            gap: 1rem;
            margin-bottom: 0.5rem;
        }}
        .topic {{
            background: #f0f0f0;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            color: #555;
        }}
        .score {{
            font-size: 0.85rem;
            color: #e6a817;
            font-weight: 600;
        }}
        .card h2 {{ font-size: 1.2rem; margin-bottom: 0.3rem; }}
        .card h2 a {{ color: #1a1a1a; text-decoration: none; }}
        .card h2 a:hover {{ color: #0066cc; }}
        .channel {{ color: #888; font-size: 0.85rem; margin-bottom: 0.5rem; }}
        .why {{ color: #444; font-size: 0.9rem; line-height: 1.5; }}
        .card-body {{ display: none; margin-top: 1.5rem; border-top: 1px solid #eee; padding-top: 1.5rem; }}
        .card.open .card-body {{ display: block; }}
        .section {{ margin-bottom: 1.5rem; }}
        .section h3 {{ font-size: 1rem; margin-bottom: 0.8rem; color: #333; }}
        .section ul {{ padding-left: 1.2rem; }}
        .section ul li {{ margin-bottom: 0.5rem; font-size: 0.9rem; line-height: 1.5; color: #333; }}
        .graph {{ display: flex; flex-direction: column; gap: 0.8rem; }}
        .node {{
            background: #f8f8f8;
            border-radius: 8px;
            padding: 0.8rem 1rem;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        .node strong {{ font-size: 0.95rem; color: #1a1a1a; }}
        .node span {{ font-size: 0.85rem; color: #555; }}
        .node small {{ font-size: 0.8rem; color: #999; }}
        footer {{
            text-align: center;
            margin-top: 3rem;
            color: #aaa;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <header>
        <h1>Elite Knowledge</h1>
        <p>Curated by AI. Updated daily. Only 9.7+ scores make it here.</p>
        <p style="margin-top:0.3rem; font-size:0.8rem; color:#aaa;">Last updated: {updated_at}</p>
    </header>
    <div class="grid">
        {cards}
    </div>
    <footer>Built with Gemini AI + GitHub Actions</footer>
    <script>
        function toggleCard(card) {{
            card.classList.toggle('open');
        }}
    </script>
</body>
</html>"""


def run():
    with open("data/videos.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    videos = data.get("videos", [])
    updated_at = data.get("updated_at", "")

    os.makedirs("docs", exist_ok=True)
    html = build_html(videos, updated_at)

    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Site built. {len(videos)} videos.")


if __name__ == "__main__":
    run()
