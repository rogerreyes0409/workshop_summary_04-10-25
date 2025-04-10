import cv2
import pytesseract
import json
import re
import dateparser
from collections import defaultdict

def extract_speaker_names(video_path, frame_interval=5):
    print("Scanning video for speaker names...")
    vid = cv2.VideoCapture(video_path)
    fps = vid.get(cv2.CAP_PROP_FPS)
    frame_gap = int(fps * frame_interval)

    speakers = set()
    frame_idx = 0

    while True:
        vid.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = vid.read()
        if not ret:
            break

        text = pytesseract.image_to_string(frame)
        detected_names = re.findall(r'[A-Z][a-z]+\\s[A-Z][a-z]+', text)
        speakers.update(detected_names)

        frame_idx += frame_gap

    vid.release()
    print(f"Detected speakers: {speakers}")
    return list(speakers)

def match_speakers_to_segments(segments, speakers):
    print("Assigning speaker names (heuristic)...")
    for seg in segments:
        assigned = speakers[hash(seg["text"]) % len(speakers)] if speakers else "Unknown"
        seg["speaker"] = assigned
    return segments

def schedule_action_items(action_items):
    schedule = {"Tomorrow": [], "Next Week": []}
    for item in action_items:
        parsed_date = dateparser.parse(item, settings={"PREFER_DATES_FROM": "future"})
        if parsed_date:
            delta = (parsed_date.date() - dateparser.parse("now").date()).days
            if delta == 1:
                schedule["Tomorrow"].append(item)
            elif 2 <= delta <= 7:
                schedule["Next Week"].append(item)
    return schedule

def save_augmented_transcript(segments, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"segments": segments}, f, indent=2, ensure_ascii=False)
    print(f"Updated transcript with speakers saved to: {output_path}")

def main():
    import sys
    if len(sys.argv) != 3:
        print("Usage: python analyze_video.py <video_file> <transcript_json>")
        return

    video_path = sys.argv[1]
    transcript_path = sys.argv[2]

    with open(transcript_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    segments = data["segments"]

    speakers = extract_speaker_names(video_path)
    segments = match_speakers_to_segments(segments, speakers)
    save_augmented_transcript(segments, transcript_path)

if __name__ == "__main__":
    main()
