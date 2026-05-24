FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y ca-certificates && update-ca-certificates

RUN pip install --upgrade -r requirements.txt

COPY src/recommendation_ui.py .
COPY src/llm_recommendation.py .
COPY src/youtube_search_tools.py .

CMD ["streamlit","run","recommendation_ui.py","--server.port=8501","--server.address=0.0.0.0"]