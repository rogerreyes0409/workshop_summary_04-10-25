import os
import sys
import json
import subprocess
import whisper

def extract_audio(video_path, audio_path):
    print(f"Extracting audio from: {video_path}")
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path
    ], check=True)
    print(f"Audio saved to: {audio_path}")

def transcribe_audio(audio_path, output_json):
    print("Loading Whisper model...")
    model = whisper.load_model("base")
    print("Transcribing...")
    result = model.transcribe(audio_path, language='en')

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Transcription saved to: {output_json}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python transcribe.py <video_file.mp4>")
        sys.exit(1)

    video_path = sys.argv[1]
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = f"{base_name}_audio.wav"
    output_json = f"{base_name}_transcript.json"

    extract_audio(video_path, audio_path)
    transcribe_audio(audio_path, output_json)

if __name__ == "__main__":
    main()
