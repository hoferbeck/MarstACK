FROM python:3.12-alpine
RUN apk add --no-cache su-exec

ENV LOG_LEVEL=info

WORKDIR /code/app
COPY ./requirements.txt /code/requirements.txt
COPY ./app /code/app
ENV PATH="/home/mack/.local/bin:${PATH}"

RUN adduser --disabled-password --gecos "MarstACK" mack
RUN chown -R mack:mack /code

# USER mack -> handled by su-exec in run.py
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./logging_config.yaml /code/logging_config.yaml

CMD ["python", "run.py"]
