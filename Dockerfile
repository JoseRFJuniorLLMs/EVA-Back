GNU nano 7.2                                                               Dockerfile                                                                         
FROM python:3.11-slim

# Instala dependências do sistema necessárias para compilar pacotes
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia o requirements do eva-enterprise
COPY eva-enterprise/requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do eva-enterprise
COPY eva-enterprise /app

# Expõe a porta 8080
EXPOSE 8080

# Inicia a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
