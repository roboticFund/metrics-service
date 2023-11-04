FROM public.ecr.aws/lambda/python:3.11

LABEL maintainer="ROBOTICFUND PTY LTD"

# Copies requirements.txt file into the container
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Installs dependencies found in your requirements.txt file
RUN pip install -r requirements.txt

# Be sure to copy over the function itself!
# Goes last to take advantage of Docker caching.
COPY . ${LAMBDA_TASK_ROOT}

# Points to the handler function of your lambda function
CMD ["app.handler"]
