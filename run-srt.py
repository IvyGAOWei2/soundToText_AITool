from faster_whisper import WhisperModel
import os

# Configuration parameters
audio_path = "audio/thedetail-20240810-0500-the_business_of_tradwives-256.mp3"
model_size = "medium"

# Generate output filename: original filename - transcript.srt
audio_filename = os.path.splitext(os.path.basename(audio_path))[0]
output_filename = f"{audio_filename} - transcript.srt"
output_dir = "output-srt"
srt_path = os.path.join(output_dir, output_filename)

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Initialize model
model = WhisperModel(model_size, device="cuda", compute_type="int8")

# Transcribe audio
segments, info = model.transcribe(audio_path, beam_size=5)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

# Utility function: Convert seconds to SRT timestamp format
def format_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

# Write SRT file
with open(srt_path, "w", encoding="utf-8") as f:
    for i, segment in enumerate(segments, start=1):
        start = format_timestamp(segment.start)
        end = format_timestamp(segment.end)
        text = segment.text.strip()

        f.write(f"{i}\n")
        f.write(f"{start} --> {end}\n")
        f.write(f"{text}\n\n")

print(f"SRT subtitle saved to: {srt_path}")