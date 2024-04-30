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
    merkle_root_bytes = merkle_root_bytes[:32]  # Ensure only 32 bytes are taken
    
    coinbase_txid = valid_txids[0][:64]  # Take the first 64 characters, which represent 32 bytes
    coinbase_txid = coinbase_txid[:64]  # Ensure only 64 characters are taken
    
    # Pad Merkle root and coinbase transaction hash to achieve 32 bytes each
    merkle_root = merkle_root_bytes.hex()
    coinbase_txid = coinbase_txid.ljust(64, '0')  # Pad with zeros to reach 64 characters
    
    # Combine Merkle root and coinbase transaction hash to form the block header
    block_header = merkle_root + coinbase_txid
    
    # Pad block header to achieve exactly 80 bytes
    block_header = block_header.ljust(160, '0')  # Pad with zeros to reach 80 bytes
    
    # Write the block header and serialized coinbase transaction to output.txt
    with open("output.txt", "w") as f:
        f.write(f"Block Header: {block_header}\n")
        f.write(f"Coinbase Transaction: {valid_txids[0]}\n")
        
        for txid in valid_txids:
            f.write(f"{txid}\n")

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
        f.write(f"{block['merkle_root']}\n")
        f.write(f"{block['valid_txids'][0]}\n")
        
        for txid in block['valid_txids']:
            f.write(f"{txid}\n")

if __name__ == "__main__":
    main()
