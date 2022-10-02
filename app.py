from time import sleep
import whisper
import sounddevice as sd
from scipy.io.wavfile import write

model = whisper.load_model("tiny")

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


class UserAction:
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


UserAction.waits = UserAction("Waiting")
UserAction.starts_recording = UserAction("Recording started")
UserAction.stops_recording = UserAction("Recording stopped")
UserAction.quits = UserAction("Quitting application")


class Waiting(State):
    name: str = "Waiting"

    def run(self):
        print("Waiting for input...")

    def next(self, input):
        if input == UserAction.starts_recording:
            return Application.recording
        if input == UserAction.quits:
            return Application.quitting
        return Application.waiting


class Recording(State):
    name: str = "Recording"

    def run(self):
        print("Recording... Press the 'Enter' key again to stop.")
        fs = 44100  # Sample rate
        seconds = 3  # Duration of recording
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()  # Wait until recording is finished
        write('./files/output.wav', fs, myrecording)  # Save as WAV file 


    def next(self, input):
        if input == UserAction.stops_recording:
            return Application.transcribing
        if input == UserAction.quits:
            return Application.quitting
        return Application.recording


class Transcribing(State):
    name: str = "Transcribing"

    def run(self):
        print(
            "Please wait while your transcription is generated. The results will display in a moment."
        )
        result = model.transcribe("./files/output.wav")
        print(result)

    def next(self, input):
        if input == UserAction.quits:
            return Application.quitting
        return Application.waiting


class Quitting(State):
    name: str = "Quitting"

    def run(self):
        print("Goodbye!")
        exit(0)


class Application(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, Application.waiting)


Application.waiting = Waiting()
Application.recording = Recording()
Application.transcribing = Transcribing()
Application.quitting = Quitting()


def quit_or_wait(value):
    action = None
    if value == "quit":
        action = UserAction.quits
    else:
        action = UserAction.waits
    return action


is_recording = False
application = Application()
while 1:
    action = None
    print(application.current_state.name)

    if application.current_state.name == "Waiting":
        value = input(
            "Hit enter to begin a 3 second recording, or type quit at any time to exit the program."
        )
        if value == "":
            action = UserAction.starts_recording
            is_recording = True
        else:
            action = quit_or_wait(value)

    elif application.current_state.name == "Recording":
        value = input("Hit enter to use the current recording, or any other key and enter to record again.")
        if value == "":
            action = UserAction.stops_recording
            is_recording = False
        else:
            action = quit_or_wait(value)

    elif application.current_state.name == "Transcribing":
        application.run(UserAction.waits)
        continue

    elif application.current_state.name == "Quitting":
        application.run(UserAction.quits)
        continue

    application.run(action)
    sleep(0.5)
