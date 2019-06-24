import sqlite3
from typing import Tuple, Iterable, NamedTuple

import graph_util as gu
from config import CONTRACT_GRAPH_PATH, CONTRACT_HASH, DATABASE_PATH

DBRow = NamedTuple('DBRow', sender=str, recipient=str, input=str)
SELECT = f"""
SELECT sender,recipient,input
FROM Quick
JOIN TX ON Quick.txHash = TX.txHash
"""


def executeSelect(select: str) -> Iterable[DBRow]:
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    rows = cur.execute(select)
    namedRows = (DBRow(*r) for r in rows)
    return namedRows


def isInterestedContract(transaction: DBRow):
    return CONTRACT_HASH == transaction.recipient


def transferGenerator(transactions: Iterable[DBRow]) -> Iterable[Tuple[str, str, int]]:
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
    transactions = filter(isInterestedContract, transactions)
    edges = list(transferGenerator(transactions))

    graph = gu.createGraph()
    gu.addEdges(graph, edges)
    gu.setColor(graph)
    gu.saveGraph(graph, path=CONTRACT_GRAPH_PATH)


if __name__ == '__main__':
    main()
