FROM python:3.12-alpine

ENV LOG_LEVEL=info

WORKDIR /code/app
COPY ./requirements.txt /code/requirements.txt
COPY ./app /code/app
ENV PATH="/home/mack/.local/bin:${PATH}"

RUN adduser --disabled-password --gecos "MarstACK" mack
RUN chown -R mack:mack /code
USER mack
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./logging_config.yaml /code/logging_config.yaml

CMD ["/bin/sh", "-c", "uvicorn main:app --log-level ${LOG_LEVEL} --log-config /code/logging_config.yaml --host 0.0.0.0 --port 8000"]
