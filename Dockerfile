# ─────────────────────────────────────────────────────────────
#  DocMind AI — Single Dockerfile
#  Runs Backend (FastAPI) + Frontend (React/Vite) together
#  Backend  → http://localhost:8000
#  Frontend → http://localhost:3000
# ─────────────────────────────────────────────────────────────

FROM python:3.11-slim

# ── System dependencies ──────────────────────────────────────
RUN apt-get update && apt-get install -y \
    curl \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    supervisor \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# ── Backend setup ─────────────────────────────────────────────
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
RUN mkdir -p storage/uploads storage/faiss_index

# ── Frontend setup ────────────────────────────────────────────
WORKDIR /app/frontend
COPY frontend/package.json .
RUN npm install
COPY frontend/ .

# ── Supervisor config ─────────────────────────────────────────
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# ── Expose ports ──────────────────────────────────────────────
EXPOSE 8000 3000

# ── Start both services ───────────────────────────────────────
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
