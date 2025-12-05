
FROM python:3.10-slim
RUN apt-get update && apt-get install -y ffmpeg git
RUN pip install openai-whisper pydub
WORKDIR /app
COPY app /app
CMD ["python","transcribe.py"]
