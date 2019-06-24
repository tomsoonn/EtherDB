import sqlite3
from collections import namedtuple
from typing import List
import networkx as nx

from build_graph import addEdges, setColor, saveGraph

contract = '0xB8c77482e45F1F44dE1745F52C74426C631bDD52'  # Binance Token
graphPath = 'Binance.graphml'

askedFields = ['sender', 'recipient', 'input']
DBRow = namedtuple('DBRow', field_names=askedFields)
SELECT = f"""
SELECT {','.join(askedFields)}
FROM Quick
JOIN TX ON Quick.txHash = TX.txHash
"""


def isInterestedContract(transaction: DBRow):
    return contract == transaction.recipient


def transferGenerator(transactions: List[DBRow]):
    """Extraction based on
    https://stackoverflow.com/questions/48004356/get-token-transfer-detail-from-transaction-hash-with-web3js
    """
    for t in transactions:
        sig = '0x' + t.input[2:10]
        if sig == '0xa9059cbb':  # Keccak-256 hash of: 'transfer(address,uint256)'
            sendAddress = '0x' + t.input[10:74]
            amount = int(t.input[74:138], base=16)
            yield t.sender, sendAddress, amount


def main():
    transactions = executeSelect(SELECT)
    transactions = list(filter(isInterestedContract, transactions))

    graph = nx.Graph()
    edges = list(transferGenerator(transactions))
    addEdges(graph, edges)
    setColor(graph)
    saveGraph(graph, path=graphPath)


def executeSelect(select: str) -> List[DBRow]:
    conn = sqlite3.connect("blockchain.db")
    cur = conn.cursor()
    rows = cur.execute(select).fetchall()
    namedRows = [DBRow(*r) for r in rows]
    return namedRows


if __name__ == '__main__':
    main()
