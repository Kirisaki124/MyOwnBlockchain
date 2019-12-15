# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 20:16:39 2019

@author: Kiri
"""

import datetime
import hashlib
import json
import requests
from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse

# Bulding blockchain

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof =  1, previous_hash = '0')
        self.nodes = set()
    
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                'timestamp': str(datetime.datetime.now()),
                'proof': proof,
                'transactions': self.transactions,
                'previous_hash': previous_hash}
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:5] == '00000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:5] != '00000':
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender, 
                                  'receiver': receiver, 
                                  'amount': amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    def add_node(self, address):
        parse_url = urlparse(address)
        self.nodes.add(parse_url.netloc)

    def replace_change(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
#--------------------------------------------------------------------------------------------------------------------------
# Mining blockchain

# Create blockchain
blockchain = Blockchain()

# WebApp: Flask
app = Flask(__name__)

# Creating an address for node on port 5000
node_address = str(uuid4()).replace('-', '')


# Mining a block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    
    blockchain.add_transaction(sender = node_address, receiver = 'Me', amount = 1)
    block = blockchain.create_block(proof, previous_hash)
    response = {"message":"Congratulation! You just mined a block!",
                "index": block["index"],
                "timestamp": block["timestamp"],
                "proof": block["proof"],
                "transactions": block["transactions"],
                "previous_hash": block["previous_hash"]}
    return jsonify(response), 200

# Get full blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {"chain": blockchain.chain,
                "length": len(blockchain.chain)}
    return jsonify(response), 200

# Check blockchain valid
@app.route('/check_validate', methods = ['GET'])
def check_validate():
    chain = blockchain.chain
    check = blockchain.is_chain_valid(chain)
    if check is True:
        response = {"Message": "Blockchain is good to go"}
    else:
        response = {"Message": "We got fucked"}
    return jsonify(response), 200

# Adding a new transaction to the blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'This transaction is invaild: Something is missing check again sender, receiver, amount', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'The transaction is add to block {index}'}
    return response, 201

# Running the app
app.run(host = '0.0.0.0', port = 5000)

