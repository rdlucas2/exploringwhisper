import click
import queue
import sounddevice as sd
import soundfile as sf
import sys
import time
import whisper


class State:
    name: str

    def run(self):
        assert 0, "run not implemented"

    def next(self, input):
        assert 0, "next not implemented"


class StateMachine:
    def __init__(self, initial_state: State):
        self.current_state = initial_state
        action = self.current_state.run()
        self.run(action)

    def run(self, input):
        print(input)
        self.current_state = self.current_state.next(input)
        action = self.current_state.run()
        self.run(action)


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


class Waiting(State):
    name: str = "Waiting"

    def run(self) -> ApplicationAction:
        value = input(
            "Hit enter to begin a recording, or type quit at any time to exit the program."
        )
        if value == "":
            action = ApplicationAction.starts_recording
        else:
            action = quit_or_wait(value)

        return action

    def next(self, input):
        if input == ApplicationAction.starts_recording:
            return Transcriber.recording
        if input == ApplicationAction.quits:
            return Transcriber.quitting
        return Transcriber.waiting


class Recording(State):
    name: str = "Recording"
    filepath: str
    q: queue = queue.Queue()

    def __init__(self, filepath="./files/output.wav"):
        self.filepath = filepath

    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())

    def run(self) -> ApplicationAction:
        fs = 44100
        try:
            # Make sure the file is opened before recording anything:
            with sf.SoundFile(
                self.filepath, mode="w", samplerate=fs, channels=2, subtype="PCM_24"
            ) as file:
                with sd.InputStream(samplerate=fs, channels=2, callback=self.callback):
                    print("#" * 10)
                    print("press Ctrl+C to stop the recording")
                    print("#" * 10)
                    while True:
                        file.write(self.q.get())
        except KeyboardInterrupt:
            print("\nRecording finished: " + repr(self.filepath))
        except Exception as e:
            print(type(e).__name__ + ": " + str(e))
        finally:
            value = input(
                "Hit enter to use the current recording, or any other key and enter to record again."
            )
            if value == "":
                action = ApplicationAction.stops_recording
            else:
                action = quit_or_wait(value)
            return action

    def next(self, input):
        if input == ApplicationAction.stops_recording:
            return Transcriber.transcribing
        if input == ApplicationAction.quits:
            return Transcriber.quitting
        return Transcriber.recording


class Transcribing(State):
    name: str = "Transcribing"
    model: whisper
    language: str
    filepath: str

    def __init__(
        self, language="en", filepath="./files/output.wav", model="small.en"
    ) -> None:
        self.model = whisper.load_model("small.en")
        self.language = language
        self.filepath = filepath

    def run(self) -> ApplicationAction:
        start_time = time.time()
        result = self.model.transcribe(self.filepath, language=self.language)
        print(result["text"])
        print("--- Transcription took: %s seconds ---" % (time.time() - start_time))
        return ApplicationAction.waiting

    def next(self, input):
        if input == ApplicationAction.quits:
            return Transcriber.quitting
        return Transcriber.waiting


class Quitting(State):
    name: str = "Quitting"

    def run(self):
        print("Goodbye!")
        exit(0)


def quit_or_wait(value):
    action = None
    if value == "quit":
        action = ApplicationAction.quits
    elif value == "q":
        action = ApplicationAction.quits
    else:
        action = ApplicationAction.waits
    return action


@click.command()
@click.option(
    "--filepath",
    default="./files/output.wav",
    prompt="Path to file to audio file",
    help="The path to the audio file to transcribe.",
)
@click.option(
    "--model",
    default="small.en",
    prompt="Openai whisper model to use. See help for valid options.",
    help='Defaults to tiny. Options are: tiny, base, small, medium, large. Add ".en" to any of these options for english only',
)
@click.option(
    "--language",
    default="en",
    prompt="Language of the provided audio file.",
    help="Defaults to English. Valid languages found here: https://github.com/openai/whisper/blob/main/whisper/tokenizer.py",
)
def run(filepath, model, language):
    ApplicationAction.waits = ApplicationAction("Waiting")
    ApplicationAction.starts_recording = ApplicationAction("Recording started")
    ApplicationAction.stops_recording = ApplicationAction("Recording stopped")
    ApplicationAction.quits = ApplicationAction("Quitting application")
    Transcriber.waiting = Waiting()
    Transcriber.recording = Recording(filepath=filepath)
    Transcriber.transcribing = Transcribing(
        language=language, filepath=filepath, model=model
    )
    Transcriber.quitting = Quitting()

    transcriber = Transcriber()

if __name__ == "__main__":
    run()
