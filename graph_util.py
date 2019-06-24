import sqlite3
from typing import List, Any, Tuple

import community
import networkx as nx

from config import GENERAL_GRAPH_PATH, DATABASE_PATH


def createGraph() -> nx.Graph:
    return nx.Graph()


def addEdges(graph: nx.Graph, rows: List[Tuple[str, str, Any]]):
    for row in rows:
        sender, recipient, value = row
        graph.add_edge(sender, recipient, value=value)


def setColor(graph: nx.Graph):
    partition = community.best_partition(graph)
    for node in graph:
        graph.add_node(node, color=partition[node])


def saveGraph(graph: nx.Graph, path: str):
    nx.write_graphml(graph, path=path)


def main():
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    select = """SELECT sender, recipient, value FROM Quick"""
    rows: List[Tuple[str, str, str]] = cur.execute(select).fetchall()

    graph = nx.Graph()
    addEdges(graph, rows)
    setColor(graph)
    saveGraph(graph, GENERAL_GRAPH_PATH)


if __name__ == '__main__':
    main()
