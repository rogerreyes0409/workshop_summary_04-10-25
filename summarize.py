import json
import re
import sys
from collections import defaultdict
from fpdf import FPDF
from transformers import pipeline
import dateparser

def load_transcript(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["segments"]

def extract_action_items(text):
    patterns = [
        r"\b(we need to|let'?s|you should|please|action item|I will|can you|make sure to)\b.+?[.?!]",
        r"\b(todo|to-do|next step|follow up)\b.+?[.?!]"
    ]
    matches = []
    for pattern in patterns:
        matches += re.findall(pattern, text, re.IGNORECASE)
    return matches

def schedule_action_items(items):
    schedule = {"Tomorrow": [], "Next Week": []}
    for item in items:
        parsed_date = dateparser.parse(item, settings={"PREFER_DATES_FROM": "future"})
        if parsed_date:
            days_out = (parsed_date.date() - dateparser.parse("now").date()).days
            if days_out == 1:
                schedule["Tomorrow"].append(item)
            elif 2 <= days_out <= 7:
                schedule["Next Week"].append(item)
    return schedule

def chunk_segments(segments, chunk_size=120):
    chunks = []
    current = {"start": segments[0]["start"], "end": None, "text": "", "speakers": set()}
    for seg in segments:
        current["text"] += " " + seg["text"]
        if "speaker" in seg:
            current["speakers"].add(seg["speaker"])
        if seg["end"] - current["start"] >= chunk_size:
            current["end"] = seg["end"]
            chunks.append(current)
            current = {"start": seg["end"], "end": None, "text": "", "speakers": set()}
    if current["text"]:
        current["end"] = segments[-1]["end"]
        chunks.append(current)
    return chunks

def generate_summary(text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(text, max_length=150, min_length=60, do_sample=False)
    return summary[0]['summary_text']

def generate_pdf_report(chunks, schedule, pdf_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "Workshop Summary Report\n", align="C")

    for i, chunk in enumerate(chunks):
        start_min = int(chunk["start"] // 60)
        end_min = int(chunk["end"] // 60)
        topic_title = f"Topic {i+1} (Minutes {start_min}-{end_min})"
        speakers = ", ".join(chunk["speakers"]) if chunk["speakers"] else "Unknown"

        pdf.set_font("Arial", style='B', size=12)
        pdf.multi_cell(0, 10, f"\n{topic_title}")
        pdf.set_font("Arial", style='', size=11)
        pdf.multi_cell(0, 10, f"Speakers: {speakers}")
        pdf.multi_cell(0, 10, f"Summary: {chunk['summary']}")

    if schedule["Tomorrow"] or schedule["Next Week"]:
        pdf.set_font("Arial", style='B', size=12)
        pdf.multi_cell(0, 10, "\nAction Items:")

    if schedule["Tomorrow"]:
        pdf.set_font("Arial", style='B', size=11)
        pdf.multi_cell(0, 10, "To Do Tomorrow:")
        pdf.set_font("Arial", size=11)
        for item in schedule["Tomorrow"]:
            pdf.multi_cell(0, 10, f"- {item.strip()}")

    if schedule["Next Week"]:
        pdf.set_font("Arial", style='B', size=11)
        pdf.multi_cell(0, 10, "\nTo Do Next Week:")
        pdf.set_font("Arial", size=11)
        for item in schedule["Next Week"]:
            pdf.multi_cell(0, 10, f"- {item.strip()}")

    pdf.output(pdf_path)
    print(f"PDF report saved to: {pdf_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python summarize.py <transcript_json>")
        sys.exit(1)

    transcript_path = sys.argv[1]
    base_name = transcript_path.replace("_transcript.json", "")
    pdf_path = f"{base_name}_summary.pdf"

    segments = load_transcript(transcript_path)
    chunks = chunk_segments(segments)

    for chunk in chunks:
        chunk["summary"] = generate_summary(chunk["text"])

    all_text = " ".join([seg["text"] for seg in segments])
    raw_actions = extract_action_items(all_text)
    schedule = schedule_action_items(raw_actions)

    generate_pdf_report(chunks, schedule, pdf_path)

if __name__ == "__main__":
    main()
