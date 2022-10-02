import queue
import sounddevice as sd
import soundfile as sf
import sys
import time
import whisper

model = whisper.load_model("small.en")


class State:
    name: str

    def run(self):
        assert 0, "run not implemented"

    def next(self, input):
        assert 0, "next not implemented"


class StateMachine:
    def __init__(self, initial_state: State):
        self.current_state = initial_state
        # self.current_state.run()

    def run(self, input):
        print(input)
        self.current_state = self.current_state.next(input)
        self.current_state.run()


class Transcriber(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, Transcriber.waiting)


class ApplicationAction:
    def __init__(self, action):
        self.action = action

    def __str__(self):
        return self.action

    def __cmp__(self, other):
        return cmp(self.action, other.action)

    # Necessary when __cmp__ or __eq__ is defined
    # in order to make this class usable as a
    # dictionary key:
    def __hash__(self):
        return hash(self.action)


class Transcriber(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, Transcriber.waiting)


class ApplicationAction:
    def __init__(self, action):
        self.action = action

    def __str__(self):
        return self.action

    def __cmp__(self, other):
        return cmp(self.action, other.action)

    # Necessary when __cmp__ or __eq__ is defined
    # in order to make this class usable as a
    # dictionary key:
    def __hash__(self):
        return hash(self.action)


ApplicationAction.waits = ApplicationAction("Waiting")
ApplicationAction.starts_recording = ApplicationAction("Recording started")
ApplicationAction.stops_recording = ApplicationAction("Recording stopped")
ApplicationAction.quits = ApplicationAction("Quitting application")


class Waiting(State):
    name: str = "Waiting"

    def run(self):
        print("Waiting for input...")

    def next(self, input):
        if input == ApplicationAction.starts_recording:
            return Transcriber.recording
        if input == ApplicationAction.quits:
            return Transcriber.quitting
        return Transcriber.waiting


q = queue.Queue()


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())


class Recording(State):
    name: str = "Recording"

    def run(self):
        file_name = "./files/output.wav"

        fs = 44100
        try:
            # Make sure the file is opened before recording anything:
            with sf.SoundFile(
                file_name, mode="w", samplerate=fs, channels=2, subtype="PCM_24"
            ) as file:
                with sd.InputStream(samplerate=fs, channels=2, callback=callback):
                    print("#" * 10)
                    print("press Ctrl+C to stop the recording")
                    print("#" * 10)
                    while True:
                        file.write(q.get())
        except KeyboardInterrupt:
            print("\nRecording finished: " + repr(file_name))
        except Exception as e:
            print(type(e).__name__ + ": " + str(e))

    def next(self, input):
        if input == ApplicationAction.stops_recording:
            return Transcriber.transcribing
        if input == ApplicationAction.quits:
            return Transcriber.quitting
        return Transcriber.recording


class Transcribing(State):
    name: str = "Transcribing"

    def run(self):
        start_time = time.time()
        result = model.transcribe("./files/output.wav", language="en")
        print(result["text"])
        print("--- Transcription took: %s seconds ---" % (time.time() - start_time))

    def next(self, input):
        if input == ApplicationAction.quits:
            return Transcriber.quitting
        return Transcriber.waiting


class Quitting(State):
    name: str = "Quitting"

    def run(self):
        print("Goodbye!")
        exit(0)


Transcriber.waiting = Waiting()
Transcriber.recording = Recording()
Transcriber.transcribing = Transcribing()
Transcriber.quitting = Quitting()


def quit_or_wait(value):
    action = None
    if value == "quit":
        action = ApplicationAction.quits
    else:
        action = ApplicationAction.waits
    return action


transcriber = Transcriber()
while 1:
    action = None
    print(transcriber.current_state.name)

    if transcriber.current_state.name == "Waiting":
        value = input(
            "Hit enter to begin a recording, or type quit at any time to exit the program."
        )
        if value == "":
            action = ApplicationAction.starts_recording
        else:
            action = quit_or_wait(value)

    elif transcriber.current_state.name == "Recording":
        value = input(
            "Hit enter to use the current recording, or any other key and enter to record again."
        )
        if value == "":
            action = ApplicationAction.stops_recording
        else:
            action = quit_or_wait(value)

    elif transcriber.current_state.name == "Transcribing":
        action = ApplicationAction.waits

    elif transcriber.current_state.name == "Quitting":
        action = ApplicationAction.quits

    transcriber.run(action)
