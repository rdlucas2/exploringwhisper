# openaiwhisper

Exploring openaiwhisper.

Models can be added to the models folder to be cached in the docker images, otherwise the model will be downloaded.

### References:
https://click.palletsprojects.com/en/8.1.x/
https://www.geeksforgeeks.org/python-append-to-a-file/
https://pysoundfile.readthedocs.io/en/latest/
https://python-sounddevice.readthedocs.io/en/0.4.5/examples.html#recording-with-arbitrary-duration
https://python-3-patterns-idioms-test.readthedocs.io/en/latest/StateMachine.html

#### TODO:


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
