import json
import hashlib
import os
import datetime

def validate_transaction(tx):
    # Check version
    if tx['version'] != 2:
        return False
    
    # Check locktime
    if tx['locktime'] != 0:
        return False
    
    # Validate vin
    for vin in tx['vin']:
        # Check if prevout exists
        if 'prevout' not in vin or 'value' not in vin['prevout']:
            return False
        
        # Check scriptpubkey
        if vin['prevout']['scriptpubkey_type'] not in ['v0_p2wpkh', 'v1_p2tr']:
            return False
        
        # Check value
        if vin['prevout']['value'] <= 0:
            return False
    
    # Validate vout
    for vout in tx['vout']:
        # Check scriptpubkey
        if vout['scriptpubkey_type'] != 'p2sh':
            return False
        
        # Check value
        if vout['value'] <= 0:
            return False
    
    return True

def calculate_fee(tx):
    total_input = sum(vin['prevout']['value'] for vin in tx['vin'])
    total_output = sum(vout['value'] for vout in tx['vout'])
    return total_input - total_output

def get_txid(tx):
    tx_hex = json.dumps(tx, separators=(',', ':'), sort_keys=True)
    tx_hash = hashlib.sha256(tx_hex.encode()).hexdigest()
    return tx_hash

def calculate_merkle_root(txids):
    return hashlib.sha256(hashlib.sha256(txids.encode()).digest()).hexdigest()

def mine_block(header):
    nonce = 0
    block_hash = hashlib.sha256(header.encode()).hexdigest()
    while not block_hash.startswith('0000'):
        nonce += 1
        block_hash = hashlib.sha256((header + str(nonce)).encode()).hexdigest()
    return nonce

def serialize_transaction(tx):
    return json.dumps(tx, separators=(',', ':'), sort_keys=True)

def main():
    mempool_folder = "./mempool"
    block_size = 0
    transactions = []
    valid_txids = []
    total_fee = 0

    # Read transactions from mempool
    for filename in os.listdir(mempool_folder):
        with open(os.path.join(mempool_folder, filename), 'r') as f:
            tx = json.load(f)
            
            if validate_transaction(tx):
                fee = calculate_fee(tx)
                if block_size + 1 <= 1000000:  # Block size limit (placeholder)
                    block_size += 1
                    total_fee += fee
                    transactions.append(tx)
                    txid = get_txid(tx)
                    valid_txids.append(txid)

    # Create coinbase transaction
    coinbase_tx = {
        "txid": "coinbase",
        "vout": [{"value": total_fee + 5000000000, "scriptPubKey": "coinbase"}]
    }
    transactions.insert(0, coinbase_tx)
    valid_txids.insert(0, "coinbase")

    # Calculate Merkle root
    merkle_root = calculate_merkle_root(''.join(valid_txids))

    # Create block header
    header = {
        "previous_block_hash": "0000000000000000000000000000000000000000000000000000000000000000",
        "merkle_root": merkle_root,
        "timestamp": int(datetime.datetime.now().timestamp()),
        "difficulty_target": "0000ffff00000000000000000000000000000000000000000000000000000000",
        "nonce": ""
    }

    # Mine block
    header["nonce"] = mine_block(json.dumps(header, separators=(',', ':'), sort_keys=True))

    # Serialize coinbase transaction
    coinbase_tx_serialized = serialize_transaction(coinbase_tx)

    # Write to output.txt
    with open("output.txt", "w") as f:
        f.write(json.dumps(header) + "\n")
        f.write(coinbase_tx_serialized + "\n")
        for txid in valid_txids:
            f.write(txid + "\n")

if __name__ == "__main__":
    main()
