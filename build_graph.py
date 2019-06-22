import sqlite3
from typing import List

import community
import networkx as nx

graphPath = "transactions.graphml"
SELECT = """
SELECT sender, recipient, value 
FROM Quick
"""


def addEdges(graph: nx.Graph, rows: List):
    for row in rows:
        sender, recipient, value = row
        graph.add_edge(sender, recipient, vallue=value)


def setColor(graph: nx.Graph):
    partition = community.best_partition(graph)
    for node in graph:
        graph.add_node(node, color=partition[node])


def saveGraph(graph: nx.Graph):
    nx.write_graphml(graph, path=graphPath)


def main():
    conn = sqlite3.connect("blockchain.db")
    cur = conn.cursor()
    rows = cur.execute(SELECT).fetchall()

    graph = nx.Graph()
    addEdges(graph, rows)
    setColor(graph)
    saveGraph(graph)


if __name__ == '__main__':
    main()
