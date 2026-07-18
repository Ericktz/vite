import sqlite3
from collections import defaultdict, OrderedDict
from datetime import datetime
import os
import pandas as pd
import json
import requests

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
        logger.info(f"Error en la solicitud RPC: {e}")
        return None


class genesisgenisis:
    def __init__(self, file_path):
        self.file_path = os.path.expanduser(file_path)
        self.data = self._load_json()
        self.df = self._create_dataframe()
    def _load_json(self):
        with open(self.file_path, 'r') as file:
            return json.load(file)
    def _create_dataframe(self):
        account_balance_map = self.data['AccountBalanceMap']
        balance_data = []
        for address, tokens in account_balance_map.items():
            for token_id, amount in tokens.items():
                balance_data.append({
                    'address': address,
                    'token_id': token_id,
                    'amount': int(amount/1E18)  # Convert amount to int
                })
        df = pd.DataFrame(balance_data)
        print(df)
        #df['amount'] = df['amount'].astype(float)  # Ensure 'amount' is of type int
        return df
    def total_accounts(self):
        return self.df['address'].nunique()
    def accounts_per_token(self, token_id):
        return self.df[self.df['token_id'] == token_id]['address'].nunique()
    def account_with_max_balance(self, token_id):
        df_token = self.df[self.df['token_id'] == token_id]
        if df_token.empty:
            return None
        max_row = df_token.loc[df_token['amount'].idxmax()]
        return max_row['address'], max_row['amount']
    def top_accounts(self, token_id, top_n=10):
        df_token = self.df[self.df['token_id'] == token_id]
        return df_token.nlargest(top_n, 'amount')[['address', 'amount']]
    def get_amount_by_address(self, address, token_id):
        df_address_token = self.df[(self.df['address'] == address) & (self.df['token_id'] == token_id)]
        if df_address_token.empty:
            return 0
        print(df_address_token['amount'])
        return df_address_token['amount'].values[0]

# Ejemplo de uso
file_path = '~/vite/003_TransactionsByAddress/genesis.json'
genisis = genesisgenisis(file_path)

tti_vcp = 'tti_251a3e67a41b5ea2373936c8'
tti_vite = 'tti_5649544520544f4b454e6e40'
tti_vx = 'tti_564954455820434f494e69b5'

# Cantidad total de cuentas
print(f"1.- Total de cuentas: {genisis.total_accounts()}")

# Cantidad de cuentas por token
print(f"\n2.- Cuentas con VCP {tti_vcp}: {genisis.accounts_per_token(tti_vcp)}")
print(f"\n3.- Cuentas con VITE {tti_vite}: {genisis.accounts_per_token(tti_vite)}")
print(f"\n4.- Cuentas con VX {tti_vx}: {genisis.accounts_per_token(tti_vx)}")


# Cuenta con el mayor balance para un token específico
max_account, max_balance = genisis.account_with_max_balance(tti_vite)
print(f"\n5.- La cuenta con el mayor balance de VITE {tti_vite} es: {max_account} con un balance de {max_balance:,.0f} VITE")

# Las 10 cuentas con el mayor balance para un token específico
print(f"\n6.- Las 10 cuentas con el mayor balance de VITE {tti_vite}:")
print(genisis.top_accounts(tti_vite, top_n=10))

# Las 100 cuentas con el mayor balance para un token específico
print(f"7.- Las 100 cuentas con el mayor balance de VITE {tti_vite}:")
print(genisis.top_accounts(tti_vite, top_n=100))

# Obtener el amount de una cuenta específica para un token específico en el genesis.json
sbpAddress = 'vite_0000000000000000000000000000000000000004d28108e76b'
quotaAddress = 'vite_0000000000000000000000000000000000000003f6af7459b9'
vitexAddress = 'vite_0000000000000000000000000000000000000006e82b8ba657'

OLDfullNodeDistrAddress = 'vite_86f729c9b7dda636e46b7ae738785be87f71390f532828ace9'
fullNodeDistrAddress = 'vite_1737bb7abc4883cc2f415a804f80274d3a725a68a5bee5bad3'
fullNodeDailyAddress = 'vite_8cf2663cc949442db2d3f78f372621733292d1fb0b846f1651'

sbpGenesis = genisis.get_amount_by_address(sbpAddress, tti_vite)
quotaGenesis = genisis.get_amount_by_address(quotaAddress, tti_vite)
vitexGenesis = genisis.get_amount_by_address(vitexAddress, tti_vite)

OLDfullNodeDistrGenesis = genisis.get_amount_by_address(OLDfullNodeDistrAddress, tti_vite)
fullNodeDistrGenesis = genisis.get_amount_by_address(fullNodeDistrAddress, tti_vite)
fullNodeDailyGenesis = genisis.get_amount_by_address(fullNodeDailyAddress, tti_vite)

actualSBP = int(ejecutar_rpc('ledger_getAccountInfoByAddress',[sbpAddress])['result']['balanceInfoMap']['tti_5649544520544f4b454e6e40']['balance'])/10**18
print(f"\n8.- SBP: El genesis de {sbpAddress} para el token {tti_vite} es: {sbpGenesis:,.18f}")

actualQuota = int(ejecutar_rpc('ledger_getAccountInfoByAddress',[quotaAddress])['result']['balanceInfoMap']['tti_5649544520544f4b454e6e40']['balance'])/10**18
print(f"\n9.- Quota: El genesis de {quotaAddress} para el token {tti_vite} es: {quotaGenesis:,.18f}-{actualQuota:,.18f}")

actualVitex = int(ejecutar_rpc('ledger_getAccountInfoByAddress',[vitexAddress])['result']['balanceInfoMap']['tti_5649544520544f4b454e6e40']['balance'])/10**18
print(f"\n9.- Vitex: El genesis de {vitexAddress} para el token {tti_vite} es: {vitexGenesis:,.18f}-{actualVitex:,.18f}")

actualFullnodeOLD = int(ejecutar_rpc('ledger_getAccountInfoByAddress',[OLDfullNodeDistrAddress])['result']['balanceInfoMap']['tti_5649544520544f4b454e6e40']['balance'])/10**18
print(f"\n9.- OLDfullNodeDistr: El genesis de {OLDfullNodeDistrAddress} para el token {tti_vite} es: {OLDfullNodeDistrGenesis:,.18f}-{actualFullnodeOLD:,.18f}")

actualFullnode = int(ejecutar_rpc('ledger_getAccountInfoByAddress',[fullNodeDistrAddress])['result']['balanceInfoMap']['tti_5649544520544f4b454e6e40']['balance'])/10**18
print(f"\n9.- fullNodeDistr: El genesis de {fullNodeDistrAddress} para el token {tti_vite} es: {fullNodeDistrGenesis:,.18f}-{actualFullnode:,.18f}")

actualFullnodeDaily = int(ejecutar_rpc('ledger_getAccountInfoByAddress',[fullNodeDailyAddress])['result']['balanceInfoMap']['tti_5649544520544f4b454e6e40']['balance'])/10**18
print(f"\n9.- FullnodeDaily: El genesis de {fullNodeDailyAddress} para el token {tti_vite} es: {fullNodeDailyGenesis:,.18f}-{actualFullnodeDaily:,.18f}")

def get_daily_balances(dbName, amountGenesis):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()

    query = '''
    SELECT * 
    FROM transactions 
    ORDER BY datetime
    '''

    cursor.execute(query)
    rows = cursor.fetchall()

    # Obtener nombres de columnas
    column_names = [description[0] for description in cursor.description]
    conn.close()

    # Crear DataFrame
    df = pd.DataFrame(rows, columns=column_names)
    df['date'] = pd.to_datetime(df['datetime'], unit='s').dt.date

    # # Calcular la suma acumulativa de 'decimalAmount'
    # df['cumulativeAmount'] = df['decimalAmount'].cumsum().astype(int)

    # Agrupar por fecha y calcular la suma diaria
    daily_df = df.groupby('date')['decimalAmount'].sum().reset_index()
    daily_df['cumulativeAmount'] = daily_df['decimalAmount'].cumsum() + amountGenesis

    result = list(zip(daily_df['date'], daily_df['cumulativeAmount']))
    return result


# Nuevo método para sumar los valores positivos de 'decimalAmount' agrupados por día
def get_daily_positive_balances(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()

    query = '''
    SELECT * 
    FROM transactions 
    ORDER BY datetime
    '''

    cursor.execute(query)
    rows = cursor.fetchall()

    # Obtener nombres de columnas
    column_names = [description[0] for description in cursor.description]
    conn.close()

    # Crear DataFrame
    df = pd.DataFrame(rows, columns=column_names)
    df['date'] = pd.to_datetime(df['datetime'], unit='s').dt.date

    # Filtrar y sumar solo los valores positivos
    df_positive = df[df['decimalAmount'] > 0]
    daily_positive_df = df_positive.groupby('date')['decimalAmount'].sum().reset_index()

    return daily_positive_df

# Nuevo método para sumar los valores negativos de 'decimalAmount' agrupados por día
def get_daily_negative_balances(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()

    query = '''
    SELECT * 
    FROM transactions 
    ORDER BY datetime
    '''

    cursor.execute(query)
    rows = cursor.fetchall()

    # Obtener nombres de columnas
    column_names = [description[0] for description in cursor.description]
    conn.close()

    # Crear DataFrame
    df = pd.DataFrame(rows, columns=column_names)
    df['date'] = pd.to_datetime(df['datetime'], unit='s').dt.date

    # Filtrar y sumar solo los valores negativos
    df_negative = df[df['decimalAmount'] < 0]
    daily_negative_df = df_negative.groupby('date')['decimalAmount'].sum().reset_index()

    return daily_negative_df

# Ejemplo de uso
def getBalancesIssueContract():
    db_file = os.path.expanduser('~/vite/003_TransactionsByAddress/transactions_issueContract.db')
    
    # Obtener el balance diario con todos los valores
    issueTotalDaily = get_daily_balances(db_file, 0)
    
    # Obtener los balances positivos diarios
    daily_burns = get_daily_positive_balances(db_file)
    
    # Obtener los balances negativos diarios
    daily_issue = get_daily_negative_balances(db_file)
    
    # Aquí puedes imprimir o trabajar con los resultados
    # Por ejemplo, para imprimir:
    # for date, balance in sbpDaily:
    #     print('{}: {:,.0f}'.format(date, balance))
    
    return issueTotalDaily, daily_burns, daily_issue


# Ejemplo de uso
def getBalancesSBP():
    db_file = os.path.expanduser('~/vite/003_TransactionsByAddress/transactions_SBP.db')
    sbpDaily = get_daily_balances(db_file, sbpGenesis)
    # for date, balance in sbpDaily:
    #     print('{}: {:,.0f}'.format(date,balance))    
    return sbpDaily
    
def getBalancesVitex():
    db_file = os.path.expanduser('~/vite/003_TransactionsByAddress/transactions_vitex.db')
    vitexDaily = get_daily_balances(db_file, 0)
    # for date, balance in vitexDaily:
    #     print('{}: {:,.0f}'.format(date,balance))    
    return vitexDaily

    
def getBalancesQuota():
    db_file = os.path.expanduser('~/vite/003_TransactionsByAddress/transactions_Quota.db')
    quotaDaily = get_daily_balances(db_file, quotaGenesis)
    # for date, balance in quotaDaily:
    #     print('{}: {:,.0f}'.format(date,balance))
    return quotaDaily

def getBalancesFullNodesDaily():
    db_file = os.path.expanduser('~/vite/003_TransactionsByAddress/transactions_FullNodesDaily.db')
    fullNodeDaily = get_daily_balances(db_file, 0)
    # for date, balance in quotaDaily:
    #     print('{}: {:,.0f}'.format(date,balance))
    return fullNodeDaily



def getBalancesFullNodeDistr():
    db_file = os.path.expanduser('~/vite/003_TransactionsByAddress/transactions_FullnodeDistribution.db')
    fullnodeDist = get_daily_balances(db_file, fullNodeDistrGenesis)
    # for date, balance in quotaDaily:
    #     print('{}: {:,.0f}'.format(date,balance))
    return fullnodeDist

def getBalancesFullNodeDistrOLD():
    db_file = os.path.expanduser('~/vite/003_TransactionsByAddress/transactions_OLDFullnodeDistribution.db')
    OLDfullnodeDistOLD = get_daily_balances(db_file,OLDfullNodeDistrGenesis)
    # for date, balance in quotaDaily:
    #     print('{}: {:,.0f}'.format(date,balance))
    return OLDfullnodeDistOLD

## Para imprimir en pantalla la lista de fechas y balance acumulado dentro del arreglo en el formato visible
# for date, balance in sbpDaily:
#     print('{}: {:,.0f}'.format(date,balance))

SBP = getBalancesSBP()
Vitex = getBalancesVitex()
Quota = getBalancesQuota()
FullnodeDaily = getBalancesFullNodesDaily()
GactualFullnode = getBalancesFullNodeDistr()
GactualFullnodeOLD = getBalancesFullNodeDistrOLD()

issueTotalDaily, daily_burns, daily_issue = getBalancesIssueContract()
print(issueTotalDaily)
print('\nquemado Total: {:,.0f}'.format(daily_burns['decimalAmount'].sum()))
print('creado Total: {:,.0f}'.format(daily_issue['decimalAmount'].sum()))
print('Promedio Diario creado: {:,.0f}'.format(daily_issue['decimalAmount'].mean()))
print('median Diario creado: {:,.0f}\n'.format(daily_issue['decimalAmount'].median()))



print('SBP {:,.18f}-{:,.18f}-{}'.format(SBP[-1][1],actualSBP, SBP[-1][1]-actualSBP))
print('Vitex {:,.18f}-{:,.18f}-{}'.format(Vitex[-1][1],actualVitex, Vitex[-1][1]-actualVitex))
print('Quota {:,.18f}-{:,.18f}-{}'.format(Quota[-1][1],actualQuota, Quota[-1][1]-actualQuota))
print('FullnodeDaily {:,.18f}-{:,.18f}-{}'.format(FullnodeDaily[-1][1],actualFullnodeDaily, FullnodeDaily[-1][1]-actualFullnodeDaily))
print('actualFullnode {:,.18f}-{:,.18f}-{}'.format(GactualFullnode[-1][1],actualFullnode, GactualFullnode[-1][1]-actualFullnode))
print('actualFullnodeOLD {:,.18f}-{:,.18f}-{}'.format(GactualFullnodeOLD[-1][1],actualFullnodeOLD, GactualFullnodeOLD[-1][1]-actualFullnodeOLD))




