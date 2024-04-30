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
    # Ensure Merkle root and coinbase transaction hash are exactly 32 bytes each
    merkle_root_bytes = bytes.fromhex(merkle_root)
    if len(merkle_root_bytes) < 32:
        merkle_root_bytes = b'\x00' * (32 - len(merkle_root_bytes)) + merkle_root_bytes
    elif len(merkle_root_bytes) > 32:
        merkle_root_bytes = merkle_root_bytes[:32]
    merkle_root = merkle_root_bytes.hex()
    
    coinbase_txid = valid_txids[0][:64]  # Take the first 64 characters, which represent 32 bytes
    if len(coinbase_txid) < 64:
        coinbase_txid = coinbase_txid + '0' * (64 - len(coinbase_txid))  # Pad with zeros
    elif len(coinbase_txid) > 64:
        coinbase_txid = coinbase_txid[:64]
    
    # Padding to achieve 80 bytes for the header
    merkle_root = merkle_root.ljust(64, '0')  # Pad with zeros
    coinbase_txid = coinbase_txid.ljust(64, '0')  # Pad with zeros
    
    # Add more block construction logic here
    
    return {
        'merkle_root': merkle_root,
        'valid_txids': valid_txids,
        'coinbase_txid': coinbase_txid
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
        f.write(f"Block Header: {block['merkle_root']}\n")
        f.write(f"Coinbase Transaction: {block['valid_txids'][0]}\n")
        
        for txid in block['valid_txids']:
            f.write(f"{txid}\n")

if __name__ == "__main__":
    main()
