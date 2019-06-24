from functools import singledispatch
from typing import Union, Dict, Tuple

from hexbytes import HexBytes
from web3 import Web3
from web3.datastructures import AttributeDict

from config import DATABASE_PATH as db_name


def createBlockRecord(block: int, web3: Web3) -> Tuple[Dict, AttributeDict]:
    """ build a block table to be compatible with SQLite data types"""
    block_data = web3.eth.getBlock(block)
    block_table = dict(block_data)

    # mapping keys to avoid name clashes
    m = {'hash': 'blockHash', 'gasUsed': 'blockGasUsed',
         'number': 'blockNumber', 'logsBloom': 'blockLogsBloom',
         'nonce': 'blockNonce'}
    block_table = dict((m.get(k, k), v) for (k, v) in block_table.items())

    # convert types to be SQLite-compatible
    tostring = ['transactions', 'difficulty', 'totalDifficulty', 'uncles']
    tohex = ['blockHash', 'blockLogsBloom', 'blockNonce', 'extraData', 'mixHash', 'parentHash',
             'receiptsRoot', 'sha3Uncles', 'stateRoot', 'transactionsRoot']

    for nn in block_table.keys():
        if nn in tohex:
            block_table[nn] = web3.toHex(block_table[nn])
        elif nn in tostring:
            block_table[nn] = str(block_table[nn])
    return block_table, block_data


@singledispatch
def createQuickRecord(
        dispatch: Union[AttributeDict, HexBytes],
        block: int, web3: Web3, balance=False) -> Tuple[Dict, AttributeDict]:
    raise TypeError


@createQuickRecord.register
def _(hashh: HexBytes, block, web3, balance=False):
    tx_data: AttributeDict = web3.eth.getTransaction(hashh)
    return createQuickRecord(tx_data, block, web3, balance)


@createQuickRecord.register
def _(tx_data: AttributeDict, block, web3, balance=False):
    # get addresses
    addr_from = tx_data['from']
    addr_to = tx_data['to']

    # get balances of these addresses
    if balance:
        balance_from = web3.eth.getBalance(addr_from, block_identifier=block)
        try:
            balance_to = web3.eth.getBalance(addr_to, block_identifier=block)
        except TypeError:
            balance_to = -1
    else:
        balance_to = None
        balance_from = None
    # build a quick table
    quick_table = {}
    quick_keys = ['from', 'to', 'value', 'hash',
                  'nonce', 'blockNumber']

    # convert types to be SQLite-compatible
    for nn in quick_keys:
        if nn == "hash":
            quick_table["txHash"] = web3.toHex(tx_data[nn])
        elif nn == "value":
            quick_table["value"] = str(tx_data[nn])
        else:
            quick_table[nn] = tx_data[nn]
    # add balances
    quick_table['balanceTo'] = str(balance_to)
    quick_table['balanceFrom'] = str(balance_from)

    return quick_table, tx_data


@singledispatch
def createTxRecord(dispatch: Union[HexBytes, AttributeDict],
                   tx_data: AttributeDict, web3: Web3) -> Dict:
    raise TypeError


@createTxRecord.register
def _(hashh: HexBytes, tx_data, web3):
    receipt_data = web3.eth.getTransactionReceipt(hashh)
    createTxRecord(receipt_data, tx_data, web3)


@createTxRecord.register
def _(receipt_data: AttributeDict, tx_data, web3):
    """ build a TX table to be compatible with SQLite data types"""
    TX_table = dict(tx_data)
    pop_tx_keys = ['from', 'to', 'value',
                   'nonce', 'blockHash', 'hash']
    for nn in pop_tx_keys:
        TX_table.pop(nn)

    receipt_keys = ['contractAddress', 'cumulativeGasUsed',
                    'gasUsed', 'gasUsed', 'logs', 'logsBloom',
                    'status', 'transactionHash', 'transactionIndex']

    for nn in receipt_keys:
        try:
            if nn == "logs":
                TX_table[nn] = str(receipt_data[nn])
            elif nn == "logsBloom":
                TX_table[nn] = web3.toHex(receipt_data[nn])
            elif nn == 'transactionHash':
                TX_table['txHash'] = receipt_data[nn]
            else:
                TX_table[nn] = receipt_data[nn]
        except KeyError:
            TX_table[nn] = -1

    tohex = ['r', 's', 'txHash']

    # conversion to strings
    for nn in TX_table.keys():
        if nn in tohex:
            TX_table[nn] = web3.toHex(TX_table[nn])
    return TX_table


def saveTables(table_quick, table_tx, table_block):
    import os
    from database.sql_helper import create_database, update_database, create_index
    import sqlite3 as sq3

    db_is_new = not os.path.exists(db_name)

    # connect to the database
    conn = sq3.connect(db_name)  # or use :memory: to put it in RAM
    cur = conn.cursor()

    if db_is_new:
        print('Creating a new DB.')
        create_database(cur)
        create_index(cur)

    update_database(cur, table_quick, table_tx, table_block)
    conn.commit()
    conn.close()
