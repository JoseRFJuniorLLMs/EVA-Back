cat deploy.sh 
#!/bin/bash

# Configurações
PROJECT_ID="aurora-v1-483722"
SERVICE_NAME="eva-backend"
REGION="europe-southwest1"
# MUDANÇA CRÍTICA: Usando o novo formato Artifact Registry na Europa
REPO_NAME="eva-repo"
IMAGE_TAG="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME"

echo "🚀 Iniciando Update GitHub..."
git pull

echo "🚀 Iniciando Build no Google Cloud Build..."
echo "📍 Imagem será enviada para: $IMAGE_TAG"

# O gcloud build submete para o novo endereço
gcloud builds submit --tag $IMAGE_TAG --project $PROJECT_ID

if [ $? -eq 0 ]; then
    echo "✅ Build concluído com sucesso! Iniciando Deploy no Cloud Run ($REGION)..."
    
    gcloud run deploy $SERVICE_NAME \
        --image $IMAGE_TAG \
        --platform managed \
        --region $REGION \
        --project $PROJECT_ID \
        --allow-unauthenticated \
        --port 8080 \
        --set-env-vars="API_BASE_URL=http://136.117.86.19:8000" \
        --set-env-vars="DATABASE_URL_ASYNC=postgresql+asyncpg://postgres:Debian23%40@34.175.224.36:5432/eva-db" \
        --set-env-vars="DATABASE_URL_SYNC=postgresql+psycopg2://postgres:Debian23%40@34.175.224.36:5432/eva-db" \
        --set-env-vars="FIREBASE_CREDENTIALS_PATH=serviceAccountKey.json"
        
    echo "🎉 Deploy finalizado!"
else
    echo "❌ Erro no Build. Verifique os logs acima."
    exit 1
fi
root@aurora-vm:/home/jose/EVA-Back# 