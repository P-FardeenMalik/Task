import hashlib
import json
import os
import datetime
import time

def validate_transaction(tx):
    if tx['version'] != 2:
        return False
    
    if tx['locktime'] != 0:
        return False
    
    for vin in tx['vin']:
        if 'prevout' not in vin or 'value' not in vin['prevout']:
            return False
        
        if vin['prevout']['scriptpubkey_type'] not in ['v0_p2wpkh', 'v1_p2tr']:
            return False
        
        if vin['prevout']['value'] <= 0:
            return False
    
    for vout in tx['vout']:
        if vout['scriptpubkey_type'] != 'p2sh':
            return False
        
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
    # Handle the "coinbase" transaction separately
    if "coinbase" in txids:
        txids.remove("coinbase")
    
    # If the list has an odd number of items, duplicate the last item
    if len(txids) % 2 != 0:
        txids.append(txids[-1])

    while len(txids) > 1:
        new_txids = []

        for i in range(0, len(txids), 2):
            hash1 = hashlib.sha256(hashlib.sha256(bytes.fromhex(txids[i])).digest()).hexdigest()
            
            # Check if the next hash exists before calculating
            if i + 1 < len(txids):
                hash2 = hashlib.sha256(hashlib.sha256(bytes.fromhex(txids[i + 1])).digest()).hexdigest()
            else:
                hash2 = hash1  # If not, use the same hash for the second one

            new_hash = hashlib.sha256(hash1.encode() + hash2.encode()).hexdigest()
            new_txids.append(new_hash)

        txids = new_txids

    return txids[0]




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

    # Remove "coinbase" from valid_txids
    valid_txids.remove("coinbase")

    # Calculate Merkle root
    merkle_root = calculate_merkle_root(valid_txids)

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
