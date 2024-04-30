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
    coinbase_txid = valid_txids[0]
    
    # Ensure Merkle root and coinbase transaction hash are exactly 32 bytes each
    merkle_root_bytes = bytes.fromhex(merkle_root)
    merkle_root = merkle_root_bytes.hex()
    
    coinbase_txid_bytes = bytes.fromhex(coinbase_txid)
    coinbase_txid = coinbase_txid_bytes.hex()
    
    # Construct the block header
    block_header = merkle_root + coinbase_txid
    
    # Pad the block header to ensure it's exactly 80 bytes
    block_header_padded = block_header.ljust(160, '0')[:160]
    
    return {
        'header': block_header_padded,
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
        f.write(f"{block['header']}\n")
        
        for txid in block['valid_txids']:
            f.write(f"{txid}\n")

if __name__ == "__main__":
    main()
