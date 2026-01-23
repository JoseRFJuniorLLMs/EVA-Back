import asyncio
import httpx
import sys
import os

# Adiciona o diretório da aplicação ao sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

async def test_finops_endpoint():
    url = "http://localhost:8000/api/v1/finops/"
    print(f"Testando endpoint: {url}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("JSON recebido com sucesso!")
                print(f"Total Tokens: {data.get('total_tokens')}")
                print(f"Total Minutos: {data.get('total_minutos')}")
                print(f"Consumo por Idoso: {len(data.get('consumo_por_idoso', []))} registros")
            else:
                print(f"Erro: {response.text}")
        except Exception as e:
            print(f"Falha na conexão: {e}")
            print("\nNota: Certifique-se de que o servidor esta rodando (python main.py)")

if __name__ == "__main__":
    asyncio.run(test_finops_endpoint())
