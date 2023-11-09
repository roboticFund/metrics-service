# metrics-service

## Useful commands

I've made this a python package following the instructions here = https://github.com/MichaelKim0407/tutorial-pip-package

## Commands to run locally (requires Docker)

Reference article - https://docs.aws.amazon.com/lambda/latest/dg/python-image.html

```
cd resources
export ENV=dev
docker build -t metrics-service:test .
docker run -p 9000:8080 metrics-service:test
```

### Run unit tests

```
cd resources
python -m unittest discover
```
