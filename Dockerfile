FROM alpine:latest

RUN apk add python3 python3-dev gcc musl-dev

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install mypy pylint
