import time
import whisper
start_time = time.time()
model = whisper.load_model("small.en")
result = model.transcribe("./files/MLKDream.mp3", language='en')
print(result["text"])
print("--- %s seconds ---" % (time.time() - start_time))
