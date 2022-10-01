import whisper

model = whisper.load_model("tiny")
result = model.transcribe("/files/MLKDream.mp3")
print(result)
