# Script para eliminar los hash de trasnascciones que no eran VITE.

import requests
import sqlite3

def ejecutar_rpc(method, params):
    # url_rpc = 'https://node.vite.net/gvite'
    url_rpc = 'http://85.190.246.211:48132'
    header = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json'
    }
    body = {
        'jsonrpc': '2.0',
        'id': 5,
        'method': method,
        'params': params
    }
    try:
        response = requests.post(url=url_rpc, json=body, headers=header)
        response.raise_for_status()  # Lanzará una excepción si hay un error HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud RPC: {e}")
        return None

# def get_hashes_from_db(db_path):
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     cursor.execute("SELECT hash FROM transactions")
#     hashes = [row[0] for row in cursor.fetchall()]
#     conn.close()
#     return hashes

# def main():
#     db_path = 'transactions_vitex.db'  # Ruta a la base de datos
#     hashes = get_hashes_from_db(db_path)

#     for hash in hashes:
#         result = ejecutar_rpc('ledger_getAccountBlockByHash', [hash])
#         if result and 'result' in result and 'tokenInfo' in result['result']:
#             token_symbol = result['result']['tokenInfo'].get('tokenSymbol', 'No tokenSymbol')
#             print(f"Hash: {hash}, Token Symbol: {token_symbol}")
#         else:
#             print(f"Hash: {hash}, No result found or tokenSymbol missing")

# if __name__ == "__main__":
#     main()


# Conexión a la base de datos SQLite
db_path = 'transactions_vitex.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Obtener todos los hashes de la tabla `transactions`
cursor.execute("SELECT hash FROM transactions")
hashes = cursor.fetchall()

# Iterar sobre cada hash y verificar `tokenSymbol`
for (hash,) in hashes:
    result = ejecutar_rpc('ledger_getAccountBlockByHash', [hash])
    if result and 'result' in result and 'tokenInfo' in result['result']:
        tokenSymbol = result['result']['tokenInfo'].get('tokenSymbol')
        if tokenSymbol != 'VITE':
            # Eliminar el registro si el tokenSymbol no es 'VITE'
            cursor.execute("DELETE FROM transactions WHERE hash = ?", (hash,))
            conn.commit()

# Cerrar la conexión
conn.close()
