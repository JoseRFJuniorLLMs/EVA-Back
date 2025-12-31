import os
import psycopg2
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, auth

# ------------------------------
# Configurações
# ------------------------------
DATABASE_URL = "postgres://postgres:Debian23%40@34.39.249.108:5432/eva-db?sslmode=disable"
FIREBASE_CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")

IDOSO_ID = 1
IDOSO_CPF = "64525430249"

# ------------------------------
# Inicializar Firebase
# ------------------------------
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

# ------------------------------
# Gerar Custom Token
# ------------------------------
custom_token = auth.create_custom_token(IDOSO_CPF)  # CPF como UID
token_str = custom_token.decode('utf-8')  # converte bytes para string
print("Token gerado:", token_str)

# ------------------------------
# Salvar no banco PostgreSQL
# ------------------------------
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Atualiza token do idoso de id 1
cur.execute("""
    UPDATE public.idosos
    SET device_token = %s,
        device_token_valido = TRUE,
        device_token_atualizado_em = %s
    WHERE id = %s
""", (token_str, datetime.utcnow(), IDOSO_ID))

conn.commit()
cur.close()
conn.close()

print("Token salvo no banco com sucesso!")
