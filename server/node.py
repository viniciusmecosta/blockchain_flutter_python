import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse
from flask_cors import CORS

# Construindo a Blockchain

class Blockchain:
    def __init__(self):
        self.chain = []  # Armazena os blocos da blockchain
        self.transactions = []  # Armazena as transações temporariamente
        self.create_block(proof=1, previous_hash='0')  # Cria o bloco inicial
        self.nodes = set()  # Armazena os nós na rede

    def create_block(self, proof, previous_hash):
        # Cria um novo bloco na blockchain
        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(datetime.datetime.now()),
            "proof": proof,
            "previous_hash": previous_hash,
            "transactions": self.transactions,
        }
        hash_value = self.hash(block)
        block["hash"] = hash_value
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        # Obtém o bloco mais recente na blockchain
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        # Implementa o algoritmo de prova de trabalho
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:6] == '000000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        # Gera o hash do bloco
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        # Verifica a validade da cadeia de blocos
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block["previous_hash"] != self.hash(previous_block):
                return False
            previous_proof = previous_block["proof"]
            proof = block["proof"]
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:6] != "000000":
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transactions(self, sender, receiver, amount):
        # Adiciona uma nova transação à lista de transações
        self.transactions.append({
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        })
        previous_block = self.get_previous_block()
        return previous_block["index"] + 1

    def add_node(self, address):
        # Adiciona um novo nó à rede
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        # Substitui a cadeia local pela mais longa na rede
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

# Minerando a Blockchain

app = Flask(__name__)

CORS(app)

node_address = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route("/mine_block", methods=['GET'])
def mine_block():
    # Rota para minerar um novo bloco
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    previous_hash = previous_block["hash"]
    blockchain.add_transactions(sender="Alguem", receiver="Alguem", amount="1000")
    proof = blockchain.proof_of_work(previous_proof)
    block = blockchain.create_block(proof, previous_hash)

    response = {
        "message": "Novo bloco minerado!",
        "index": block["index"],
        "timestamp": block["timestamp"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"],
        "transactions": block["transactions"],
    }

    return jsonify(response), 200

@app.route("/get_chain", methods=["GET"])
def get_chain():
    # Rota para obter a cadeia de blocos
    response = {
        "chain": blockchain.chain,
        "active_nodes": list(blockchain.nodes),
        "length": len(blockchain.chain)
    }

    return jsonify(response)

@app.route("/is_valid", methods=["GET"])
def is_valid():
    # Rota para verificar a validade da cadeia de blocos
    is_valid_chain = blockchain.is_chain_valid(blockchain.chain)
    if is_valid_chain:
        response = {'message': "Tudo certo! A Blockchain é válida."}
    else:
        response = {'message': "Temos um problema. A Blockchain não é válida."}
    return jsonify(response), 200

@app.route("/add_transaction", methods=['POST'])
def add_transactions():
    # Rota para adicionar transações à blockchain
    json_data = request.json
    transaction_keys = ["sender", "receiver", "amount"]

    if not all(key in json_data for key in transaction_keys):
        return "Faltam alguns elementos da transação", 400

    index = blockchain.add_transactions(json_data["sender"], json_data["receiver"], json_data["amount"])
    response = {
        "message": f"Esta transação será adicionada ao Bloco {index}"
    }
    return jsonify(response), 201

# Descentralização

@app.route("/connect_node", methods=['POST'])
def connect_node():
    # Rota para conectar novos nós à rede
    json_data = request.json
    nodes = json_data.get('nodes')
    if nodes is None:
        return "Nenhum nó", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {
        "message": "Todos os nós estão agora conectados. A Blockchain ViCoin agora contém os seguintes nós:",
        "total_nodes": list(blockchain.nodes)
    }
    return jsonify(response), 201

@app.route("/replace_chain", methods=["GET"])
def replace_chain():
    # Rota para substituir a cadeia local pela mais longa na rede
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': "Os nós tinham cadeias diferentes, então a cadeia foi substituída pela mais longa.", "new_chain": blockchain.chain}
    else:
        response = {'message': "Tudo certo. A cadeia é a maior.", "actual_chain": blockchain.chain}
    return jsonify(response), 200

app.run(host='0.0.0.0', port=5000, debug=True)
