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
    def __init__(blockchain):
        blockchain.chain = []  
        blockchain.transactions = []
        blockchain.create_block(proof=1, previous_hash='0000000000000000000000000000')  # Cria o bloco inicial
        blockchain.nodes = set()  # Armazena os nós na rede

    def create_block(blockchain, proof, previous_hash):
        # Cria um novo bloco na blockchain
        block = {
            "index": len(blockchain.chain) + 1,
            "timestamp": str(datetime.datetime.now()),
            "proof": proof,
            "previous_hash": previous_hash,
            "transactions": blockchain.transactions,
        }
        hash_value = blockchain.hash(block)
        block["hash"] = hash_value
        blockchain.transactions = []
        blockchain.chain.append(block)
        return block

    def get_previous_block(blockchain):
        # Obtém o bloco mais recente na blockchain
        return blockchain.chain[-1]


    def proof_of_work(blockchain, previous_hash):
        new_proof = 1
        check_proof = False
        hash_anterior = int(previous_hash, 16) 
        transactions = blockchain.transactions_int()
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof + hash_anterior + transactions).encode()).hexdigest()
            if hash_operation[:5] == '00000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(blockchain, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        hashed_result = hashlib.sha256(encoded_block).hexdigest()
        if hashed_result[0] == '0':
            hashed_result = '1' + hashed_result[1:]
        return hashed_result

    def is_chain_valid(blockchain, chain):
        # Verifica a validade da cadeia de blocos
        previous_block = chain[0]
        block_index = 1
        
        while block_index < len(chain):
            block = chain[block_index]
            if block["previous_hash"] != blockchain.hash(previous_block):
                return False
            previous_proof = previous_block["proof"]
            proof = block["proof"]
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:5] != "00000":
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transactions(blockchain, sender, receiver, amount):
        blockchain.transactions.append({
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        })
        previous_block = blockchain.get_previous_block()
        return previous_block["index"] + 1

    def add_node(blockchain, address):
        # Adiciona um novo nó à rede
        parsed_url = urlparse(address)
        blockchain.nodes.add(parsed_url.netloc)
    
    
    def transactions_int(blockchain):
        # Gera o hash das transações
        transactions_string = json.dumps(blockchain.transactions, sort_keys=True)
        return int(hashlib.sha256(transactions_string.encode()).hexdigest(), 16)

    def replace_chain(blockchain):
        # Substitui a cadeia local pela mais longa na rede
        network = blockchain.nodes
        longest_chain = None
        max_length = len(blockchain.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]
                if length > max_length and blockchain.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            blockchain.chain = longest_chain
            return True
        return False

# Minerando a Blockchain

app = Flask(__name__)

CORS(app)

node_address = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route("/mine_block", methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_hash = previous_block["hash"]
    blockchain.add_transactions(sender="Recompensador", receiver="Minerador", amount=10)
    proof = blockchain.proof_of_work(previous_hash)
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
