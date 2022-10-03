# openaiwhisper

Exploring openaiwhisper.

Models can be added to the models folder to be cached in the docker images, otherwise the model will be downloaded.
To listen to audio from computer speakers, you must enable "stereo mix" on your recording devices, and then find it in the list of audio devices from the python -m sounddevice command.

### working locally
```
pip install -r local-requirements.txt
python local.py
```

### build the container:
```
docker build -t cliopenaiwhisper --target cli .

docker build -t appopenaiwhisper --target app .
```

### run the image (formatted for powershell with $(pwd) - may need adjustment for linux)
```
docker run --rm -it -v "$(pwd)\files:/files" --name=cliopenaiwhisper cliopenaiwhisper /files/MLKDream.mp3 --model tiny

docker run --rm -it -v "$(pwd)\files:/files" --name=appopenaiwhisper appopenaiwhisper
```

###  debug/code in the container (be sure to go to the src dir, as the original during build goes to WORKDIR app)
```
docker run --rm -it -v "$(pwd)\files:/files" -v "$(pwd)\src:/src" --entrypoint /bin/bash --name=cliopenaiwhisper cliopenaiwhisper

docker run --rm -it -v "$(pwd)\files:/files" -v "$(pwd)\src:/src" --entrypoint /bin/bash --name=appopenaiwhisper appopenaiwhisper
```

#### TODO:
- read audio from aws s3bucket or azure blob storage

#### References:
- https://github.com/openai/whisper
- https://click.palletsprojects.com/en/8.1.x/
- https://www.geeksforgeeks.org/python-append-to-a-file/
- https://pysoundfile.readthedocs.io/en/latest/
- https://python-sounddevice.readthedocs.io/en/0.4.5/examples.html#recording-with-arbitrary-duration
- https://python-3-patterns-idioms-test.readthedocs.io/en/latest/StateMachine.html
