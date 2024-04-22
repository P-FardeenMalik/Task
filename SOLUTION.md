# Blockchain Block Construction

## Design Approach

**Read Transactions:** Read transactions from the mempool directory.

**Validate Transactions:** Validate each transaction for version, locktime, scriptpubkey, and value.

**Calculate Fees:** Calculate the transaction fees for each valid transaction.

**Create Coinbase Transaction:** Create a coinbase transaction to collect the block reward and fees.

**Calculate Merkle Root:** Calculate the Merkle root using the valid transaction IDs.

**Construct Block Header:** Assemble the block header with the previous block hash, Merkle root, timestamp, difficulty target, and nonce.

**Mine Block:** Find the nonce that meets the target difficulty.

**Serialise Transactions:** Serialise the coinbase transaction and valid transaction IDs.

**Write to File:** Write the block header, coinbase transaction, and transaction IDs to output.txt.


## Implementation Details
**Pseudo Code**
function validate_transaction(tx):
    for each input in tx['vin']:
        validate prevout, scriptpubkey, value
    for each output in tx['vout']:
        validate scriptpubkey, value
    return true if valid, false otherwise

function calculate_fee(tx):
    total_input = sum(input['value'] for input in tx['vin'])
    total_output = sum(output['value'] for output in tx['vout'])
    return total_input - total_output

function get_txid(tx):
    return sha256(hash(tx))

function calculate_merkle_root(txids):
    return sha256(sha256(txids))

function mine_block(header):
    nonce = 0
    while not hash(header + str(nonce)).startswith('0000'):
        nonce += 1
    return nonce

function main():
    read transactions from mempool
    validate and filter transactions
    calculate total fee
    create coinbase transaction
    calculate merkle root
    construct block header
    mine block
    serialize coinbase transaction and valid txids
    write to output.txt


## Results and Performance
The program successfully reads transactions from the mempool, validates them, calculates fees, constructs a coinbase transaction, calculates the Merkle root, constructs a block header, mines the block, serialises transactions, and writes the block to output.txt.

## Efficiency
The program processes transactions sequentially, which might be inefficient for a large number of transactions. However, for the given mempool size and requirements, the efficiency is acceptable.

## Conclusion
This solution demonstrates the basic principles of constructing a valid block in a blockchain system like Bitcoin. The key concepts of transaction validation, fee calculation, Merkle root calculation, block header construction, and mining are implemented from scratch without relying on Bitcoin-specific libraries.

