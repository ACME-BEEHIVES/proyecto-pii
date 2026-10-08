FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema para PaddleOCR, pymupdf y extracción de Office
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    libglib2.0-dev \
    poppler-utils \
    antiword \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Instalar paddlepaddle CPU primero (paquete grande, mejor en capa separada)
RUN pip install --no-cache-dir paddlepaddle==2.6.2 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html || \
    pip install --no-cache-dir paddlepaddle-cpu

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
