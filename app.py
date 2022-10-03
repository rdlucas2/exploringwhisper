import click
import time
import whisper

@click.command()
@click.option('--filepath', prompt='Path to file to audio file', help='The path to the audio file to transcribe.')
@click.option('--model', default='tiny', prompt='Openai whisper model to use. See help for valid options.', help='Defaults to tiny. Options are: tiny, base, small, medium, large. Add ".en" to any of these options for english only')
@click.option('--language', default='en', prompt='Language of the provided audio file.', help='Defaults to English. Valid languages found here: https://github.com/openai/whisper/blob/main/whisper/tokenizer.py')
def run(filepath, model, language):
    start_time = time.time()
    model = whisper.load_model(model)
    result = model.transcribe(filepath, language=language)
    print(result["text"])
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == '__main__':
    run()
