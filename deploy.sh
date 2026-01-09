#!/bin/bash

# Configurações
PROJECT_ID="fuchsia-427001"
SERVICE_NAME="eva-backend"
REGION="southamerica-east1"
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Iniciando Update GitHub..."
git pull

echo "🚀 Iniciando Build no Google Cloud Build..."
gcloud builds submit --tag $IMAGE_TAG

if [ $? -eq 0 ]; then
    echo "✅ Build concluído com sucesso! Iniciando Deploy no Cloud Run..."
    
    # Adicionadas as variáveis de banco de dados para evitar o crash no startup
    gcloud run deploy $SERVICE_NAME \
        --image $IMAGE_TAG \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --port 8080 \
        --set-env-vars="API_BASE_URL=http://136.117.86.19:8000" \
        --set-env-vars="DATABASE_URL_ASYNC=postgresql+asyncpg://postgres:Debian23%40@34.39.249.108:5432/eva-db" \
        --set-env-vars="DATABASE_URL_SYNC=postgresql+psycopg2://postgres:Debian23%40@34.39.249.108:5432/eva-db" \
        --set-env-vars="FIREBASE_CREDENTIALS_PATH=serviceAccountKey.json"
        
    echo "🎉 Deploy finalizado!"
else
    echo "❌ Erro no Build. Verifique os logs acima."
    exit 1
fi