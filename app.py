import time
import whisper
start_time = time.time()
model = whisper.load_model("tiny")
result = model.transcribe("./files/MLKDream.mp3")
print(result["text"])
print("--- %s seconds ---" % (time.time() - start_time))
