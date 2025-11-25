from faster_whisper import WhisperModel
import os

# Configuration parameters
audio_path = "audio/thedetail-20240810-0500-the_business_of_tradwives-256.mp3"
model_size = "medium"

# Generate output filename: original filename - transcript.txt
audio_filename = os.path.splitext(os.path.basename(audio_path))[0]
output_filename = f"{audio_filename} - transcript.txt"
output_dir = "output-text"
output_path = os.path.join(output_dir, output_filename)

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Initialize model (using int8 precision to save GPU memory)
model = WhisperModel(model_size, device="cuda", compute_type="int8")

# Transcribe audio
segments, info = model.transcribe(audio_path, beam_size=5)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

# Save transcription result as .txt file
with open(output_path, "w", encoding="utf-8") as f:
    for segment in segments:
        f.write(f"[{segment.start:.2f} - {segment.end:.2f}] {segment.text}\n")

print(f"Transcription saved to: {output_path}")