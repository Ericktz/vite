import traceback
import argparse
import requests
import json
import os
import sys
import pandas as pd  # pip install pandas / alternativ, if several python installations: python3 -m pip install pandas
from datetime import datetime, timezone
import time
import sqlite3

# Create the parser
parser = argparse.ArgumentParser(description='Request parameters')
# Add the arguments
parser.add_argument('--vaddr', type=str, help='VITE address')
parser.add_argument('--nodeIP', type=str, help='VITE node IP')
parser.add_argument('--fromDate', type=lambda s: datetime.strptime(s, '%Y-%m-%d'), help='From date YYYY-MM-DD (incl.) [optional]')
parser.add_argument('--toDate', type=lambda s: datetime.strptime(s, '%Y-%m-%d'), help='To date YYYY-MM-DD (incl.) [optional]')
parser.add_argument('--name', type=str, help='Name db file [optional]')
parser.add_argument('--mode', type=str, help='mode of running [default, actualizar, reanudar]')


# Execute the parse_args() method
args = parser.parse_args()

fromDate = args.fromDate
toDate = args.toDate
viteAddress = args.vaddr
nodeIP = args.nodeIP
name = args.name
mode = args.mode

if mode is None:
    mode = 'default'

if name is not None:
    Name = 'transactions_' + name
else:
    Name = 'transactions_'

if fromDate is not None:
    fromDate = datetime.timestamp(fromDate)
if toDate is not None:
    toDate = datetime.timestamp(toDate)

if fromDate is not None and toDate is not None:
    if toDate < fromDate:
        sys.exit('  ###> toDate must be equal or greater than fromDate')

if fromDate is not None and toDate is None:
    toDate = datetime.today().timestamp()  # strftime('%Y-%m-%d')

filterToken = ['VITE']  # ['VITE', 'BAN']
filterTokenId = ['tti_5649544520544f4b454e6e40']
filterTime = [fromDate, toDate]
print(filterTime)

if nodeIP is None:
    sys.exit('  ###> You have to enter an IP of a VITE node.')

nodeDetails = [
    {'name': '', 'IP': nodeIP}
]
print(nodeDetails)
if viteAddress is None:
    sys.exit('  ###> You have to enter a VITE address with parameter --vaddr')

transactionsPerRequest = 1000
pageMax = 200_000

path = os.path.dirname(os.path.abspath(__file__))

def getURL(ip):
    return 'http://' + ip + ':48132'

def getHeader():
    header = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json'
    }
    return header

def getBody(viteAddr, pg, transPerRequest):
    body = {
        'jsonrpc': '2.0',
        'id': 2,
        'method': 'ledger_getAccountBlocksByAddress',
        'params': [viteAddr, pg, transPerRequest]
    }
    return body

def writeToSQLite(transactions):
    try:
        conn = sqlite3.connect(Name + '.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                fromAddress TEXT,
                toAddress TEXT,
                transactionType TEXT,
                hash TEXT,
                decimalAmount REAL,
                amount TEXT,
                decimals INTEGER,
                fee TEXT,
                tokenName TEXT,
                tokenSymbol TEXT,
                datetime INTEGER
            )
        ''')

        cursor.executemany('''
            INSERT INTO transactions (fromAddress, toAddress, transactionType, hash, decimalAmount, amount, decimals, fee, tokenName, tokenSymbol, datetime)
            VALUES (:fromAddress, :toAddress, :transactionType, :hash, :decimalAmount, :amount, :decimals, :fee, :tokenName, :tokenSymbol, :datetime)
        ''', transactions)

        conn.commit()
        conn.close()
        print('Transactions saved to SQLite')
    except Exception as e:
        print('###> Exception during SQLite operation:')
        traceback.print_exc()
        sys.exit(1)

def get_db_date_range():
    conn = sqlite3.connect(Name + '.db')
    cursor = conn.cursor()
    cursor.execute('SELECT MIN(datetime), MAX(datetime) FROM transactions')
    result = cursor.fetchone()
    conn.close()
    return result

def requestNodeData(mode='default'):
    if len(nodeDetails) == 1:
        url = getURL(nodeDetails[0]['IP'])
        header = getHeader()

        page = 0
        endPage = True
        transactions = []
        if mode != 'default':
            min_date, max_date = get_db_date_range()
        while page < pageMax and endPage:
            body = getBody(viteAddress, page, transactionsPerRequest)
            try:
                response = requests.post(url=url, json=body, headers=header)

                if response.status_code == 200:
                    resp = response.json()
                    #condición de termino de recorrido
                    if resp['result'] is None:
                        print('Last requested page has no transaction results.')
                        endPage = False
                        break

                    #para cada bloque, analizar los tipos de transacciones
                    for result in resp['result']:
                        tokenInfo = result.get('tokenInfo')
                        timestamp = result['timestamp']

                        # se debe reanudar el procso de obtención de transaciones, solo debe iniciar cuando la fecha obtenida ne la transacción es menor que la fecha más antigüa guardada, 
                        # todo otra condición debe pasarse
                        if mode == 'reanudar' and timestamp >= min_date:
                            continue
                        #se debe actualizar la base de datos hasta que se llegue a la feechas más actual en ella, y despues se cierra el proceso
                        if mode == 'actualizar' and timestamp <= max_date:
                            endPage = False
                            break

                        if result['blockType'] == 4 and result['sendBlockList'] is not None and tokenInfo and tokenInfo.get('tokenSymbol') in filterToken:
                            for send_block in result.get('sendBlockList', []):

                                if (float(send_block.get('amount')) > 0
                                    and send_block.get('fromAddress') in viteAddress
                                    and send_block.get('tokenId') in filterTokenId
                                ):
                                    transactionType = 'Sent'
                                    transactionMultiplier = -1
                                    amount = int(send_block['amount'])
                                    decimals = int(tokenInfo['decimals'])
                                    decimalAmount = (amount / 10**decimals) * transactionMultiplier
                                    print(decimalAmount)
                                    dtobj = datetime.fromtimestamp(result['timestamp'], timezone.utc)

                                    transaction = {
                                        'fromAddress': send_block['fromAddress'],
                                        'toAddress': send_block['toAddress'],
                                        'transactionType': transactionType,
                                        'hash': send_block['hash'],
                                        'decimalAmount': decimalAmount,
                                        'amount': str(amount),
                                        'decimals': decimals,
                                        'fee': result['fee'],
                                        'tokenName': tokenInfo['tokenName'],
                                        'tokenSymbol': tokenInfo['tokenSymbol'],
                                        'datetime': result['timestamp']
                                    }

                                    transactions.append(transaction)
                        
                        if tokenInfo and tokenInfo.get('tokenSymbol') in filterToken and int(result['amount']) > 0:
                            if (filterTime[0] is None and filterTime[1] is None) or (int(filterTime[0]) <= result['timestamp'] and result['timestamp'] <= int(filterTime[1])):
                                if result['toAddress'] == viteAddress:
                                    transactionType = 'Received'
                                    transactionMultiplier = 1
                                if result['fromAddress'] == viteAddress:
                                    transactionType = 'Sent'
                                    transactionMultiplier = -1

                                amount = int(result['amount'])
                                decimals = int(tokenInfo['decimals'])
                                decimalAmount = (amount / 10**decimals) * transactionMultiplier
                                print(decimalAmount)
                                dtobj = datetime.fromtimestamp(result['timestamp'], timezone.utc)

                                transaction = {
                                    'fromAddress': result['fromAddress'],
                                    'toAddress': result['toAddress'],
                                    'transactionType': transactionType,
                                    'hash': result['hash'],
                                    'decimalAmount': decimalAmount,
                                    'amount': str(amount),
                                    'decimals': decimals,
                                    'fee': result['fee'],
                                    'tokenName': tokenInfo['tokenName'],
                                    'tokenSymbol': tokenInfo['tokenSymbol'],
                                    'datetime': result['timestamp']
                                }

                                transactions.append(transaction)
                    if len(transactions) > 0:
                        writeToSQLite(transactions)
                        transactions = []
                else:
                    print(response.status_code)
                    endPage = False
                    break
            except Exception as e:
                print('###> Exception during request:')
                traceback.print_exc()
                # sys.exit(1)
                time.sleep(2)
            page = page + 1
            print('Downloaded page ' + str(page))
        
        print('Total transactions downloaded: ' + str(len(transactions)))
        print('Done')


print('{}\n'.format(datetime.today()))
print('{}: {}\n'.format(name,viteAddress))
print('{}\n'.format(mode))

requestNodeData(mode)
