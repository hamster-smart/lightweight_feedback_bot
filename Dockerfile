FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

RUN addgroup --system appgroup && adduser --system appuser --ingroup appgroup

COPY bulgaria_helps_bot.py .
COPY security.py .

RUN chown -R appuser:appgroup /app
USER appuser

CMD ["python", "bulgaria_helps_bot.py"]
