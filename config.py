import os

# database
PROVIDER_URI = 'https://mainnet.infura.io/v3/ca48ee46d4b04cf1b4e335fde0794792'
START_BLOCK = 8020000
BLOCKS_NUMBER = 1000

_outputPath = 'output'
os.makedirs(_outputPath, exist_ok=True)

DATABASE_PATH = os.path.join(_outputPath, 'blockChain.db')
LAST_BLOCK_PATH = os.path.join(_outputPath, 'lastBlock.txt')
TIME_PER_BLOCK_PATH = os.path.join(_outputPath, 'timePerBlocks.txt')

# graph
GENERAL_GRAPH_PATH = os.path.join(_outputPath, 'transactions.graphml')

# contact graph
CONTRACT_HASH = '0xB8c77482e45F1F44dE1745F52C74426C631bDD52'  # Binance Token
CONTRACT_GRAPH_PATH = os.path.join(_outputPath, 'Binance.graphml')
