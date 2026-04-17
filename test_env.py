from dotenv import load_dotenv
import os

# Carrega as variáveis do .env para o ambiente
load_dotenv()

client_id = os.getenv("BLIZZARD_CLIENT_ID")
client_secret = os.getenv("BLIZZARD_CLIENT_SECRET")
region = os.getenv("BLIZZARD_REGION")

print(f"Client ID carregado: {client_id[:8]}..." if client_id else "❌ Client ID não encontrado")
print(f"Client Secret carregado: {'sim' if client_secret else 'não'}")
print(f"Região: {region}")