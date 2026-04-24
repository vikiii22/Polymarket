import os
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

load_dotenv()

def resolver_onboarding():
    # 1. Cargamos tus datos del .env
    pk = os.getenv("PRIVATE_KEY")
    address = os.getenv("FUNDER_ADDRESS")
    
    # 2. Inicializamos el cliente
    # IMPORTANTE: El host debe ser el de la CLOB
    client = ClobClient(
        host="https://clob.polymarket.com",
        key=pk, 
        chain_id=137
    )

    print(f"--- Intentando conectar con: {address} ---")
    
    try:
        # Paso A: Obtener el estado de la cuenta
        # Si ya has operado, esto debería devolver tus datos
        print("Buscando perfil en el servidor...")
        
        # Paso B: El truco del Senior -> Derivar en lugar de Crear
        # Como ya has operado, es posible que ya tengas una clave asignada.
        # 'derive_api_key' la recupera usando tu firma digital.
        print("Intentando DERIVAR API Key existente...")
        try:
            creds = client.derive_api_key()
        except:
            print("No se pudo derivar, intentando CREAR una nueva...")
            # Si no existe, intentamos crearla pero asegurando el onboarding
            client.create_account()
            creds = client.create_api_key()

        print("\n¡CONEXIÓN EXITOSA!")
        print("-" * 30)
        print(f"POLYMARKET_API_KEY={creds.api_key}")
        print(f"POLYMARKET_API_SECRET={creds.api_secret}")
        print(f"POLYMARKET_API_PASSPHRASE={creds.api_passphrase}")
        print("-" * 30)
        print("Copia estos 3 valores a tu .env ahora mismo.")

    except Exception as e:
        print(f"\nERROR CRÍTICO:")
        print(f"Detalle: {e}")
        print("\nSi el error persiste y ya tienes fondos:")
        print("1. Verifica que tu IP no sea de un país restringido (EE.UU. por ejemplo).")
        print("2. Asegúrate de que la PRIVATE_KEY en el .env es la misma que la de la wallet que usas en la web.")

if __name__ == "__main__":
    resolver_onboarding()