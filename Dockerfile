FROM python:3.11-slim AS final

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        espeak \
    && rm -rf /var/lib/apt/lists/*

# Set timezone
RUN ln -fs /usr/share/zoneinfo/Asia/Phnom_Penh /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure logs + permissions
RUN mkdir -p /var/log/uvicorn /app/src/tts_model \
    && touch /var/log/uvicorn/app.log /var/log/uvicorn/access.log \
    && chmod 666 /var/log/uvicorn/*.log \
    && chmod +x /app/start.sh

EXPOSE 8080

ARG MODEL_FILE
COPY ${MODEL_FILE} /app/src/tts_model/pretrained_ljs.onnx

# CMD ["./start.sh"]