FROM python:alpine

COPY pyproject.toml README.md ./
COPY sonyci sonyci

RUN pip install .[cli]

CMD [ "ci" ]