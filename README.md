# openaiwhisper

exploring openaiwhisper

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
