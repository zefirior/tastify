FROM python:3.11

WORKDIR /back

ENV PYTHONPATH=/
COPY back/requirements.txt /back/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /back/requirements.txt
COPY back /back

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "entrypoint:app"]
