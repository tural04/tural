import datetime
import hashlib
import json
from flask import Flask, jsonify
import psycopg2
import pandas as pd

class Blockchain:
    def postgre(self):   #коннект к базе данных
        conn = psycopg2.connect(dbname='postgres', user='postgres', password='turalalexey12345', host='localhost')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "customers"')
        df = cursor.fetchall()
        df = pd.DataFrame(df)
        df = df.drop(0, axis=1)
        print(df)
        return df
    
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):  #первый блок
        df = self.postgre()
        self.create_block(proof=1, previous_hash='0', df=df)
        
    def create_block(self, proof, previous_hash, df):
        block = {'id': len(self.chain) + 1,
                 'firstname': str(df[1].iloc[len(self.chain)]),
                 'adress': str(df[2].iloc[len(self.chain)]),
                 'phone': str(df[3].iloc[len(self.chain)]),
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block

    def print_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof): #пруф работы
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:5] == '00000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    def chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:5] != '00000':
                return False
            previous_block = block
            block_index += 1
        return True
# Создание веб-приложения с использованием flask
app = Flask(__name__)
blockchain = Blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.print_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    df = blockchain.postgre()  # Получаем df из postgre()
    block = blockchain.create_block(proof, previous_hash, df)  # Передаем df в create_block()
    response = {'message': 'A block is MINED',
                'id': block['id'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    return jsonify(response), 200
@app.route('/display_chain', methods=['GET'])

def display_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/valid', methods=['GET'])
#
@app.route('/valid', methods=['GET'])
def valid():
    valid = blockchain.chain_valid(blockchain.chain)
    if valid:
        response = {'message': 'The Blockchain is valid.'}
    else:
        response = {'message': 'The Blockchain is not valid.'}
    return jsonify(response), 200

app.run(host='172.20.10.2', port=5000)
