import hashlib
import json
import os

def validate_transaction(tx):
    if tx['version'] != 2:
        return False
    
    if tx['locktime'] != 0:
        return False
    
    # Add more validation checks here
    
    return True

def get_txid(tx):
    tx_hex = json.dumps(tx, separators=(',', ':'), sort_keys=True)
    tx_hash = hashlib.sha256(tx_hex.encode()).hexdigest()
    return tx_hash

def calculate_merkle_root(txids):
    if len(txids) == 0:
        return None
    
    while len(txids) > 1:
        if len(txids) % 2 != 0:
            txids.append(txids[-1])
        
        new_txids = []
        
        for i in range(0, len(txids), 2):
            combined = txids[i] + txids[i + 1]
            combined_hash = hashlib.sha256(hashlib.sha256(bytes.fromhex(combined)).digest()).hexdigest()
            new_txids.append(combined_hash)
        
        txids = new_txids
    
    return txids[0]

def construct_block(transactions):
    valid_txids = []
    
    for tx in transactions:
        if validate_transaction(tx):
            txid = get_txid(tx)
            valid_txids.append(txid)
    
    merkle_root = calculate_merkle_root(valid_txids)
    
    # Constructing the block header
    version = '02000000'
    prev_block_hash = '0000000000000000000000000000000000000000000000000000000000000000'
    timestamp = '1231006505'  # Example timestamp (Genesis block)
    bits = '1d00ffff'  # Difficulty target
    nonce = '00000000'  # Placeholder nonce
    
    block_header = version + prev_block_hash + merkle_root + timestamp + bits + nonce
    
    # Calculate the hash of the block header
    block_hash = hashlib.sha256(hashlib.sha256(bytes.fromhex(block_header)).digest()).hexdigest()
    
    return {
        'block_header': block_header,
        'block_hash': block_hash,
        'merkle_root': merkle_root,
        'valid_txids': valid_txids
    }

def main():
    files = [f for f in os.listdir("mempool") if f.endswith('.json')]
    
    transactions = []
    
    for file in files:
        with open(os.path.join("mempool", file), 'r') as f:
            data = json.load(f)
            transactions.append(data)
    
    block = construct_block(transactions)
    
    # Write the block header and serialized coinbase transaction to output.txt
    with open("output.txt", "w") as f:
        f.write(f"Block Header: {block['block_header']}\n")
        f.write(f"Block Hash: {block['block_hash']}\n")
        f.write(f"Merkle Root: {block['merkle_root']}\n")
        f.write(f"Coinbase Transaction: {block['valid_txids'][0]}\n")
        
        for txid in block['valid_txids']:
            f.write(f"{txid}\n")

if __name__ == "__main__":
    main()
