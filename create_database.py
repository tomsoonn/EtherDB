import time
from typing import Iterable

from web3 import Web3

from config import START_BLOCK, BLOCKS_NUMBER, PROVIDER_URI, TIME_PER_BLOCK_PATH, LAST_BLOCK_PATH
from database.async_request import getTransactions
from database.organize import createBlockRecord, saveTables

startTime = time.time()


def getNextBlock():
    try:
        with open(LAST_BLOCK_PATH, 'r') as f:
            number = f.read()
            return int(number) + 1 if number else START_BLOCK
    except FileNotFoundError:
        return START_BLOCK


def timePerBlockIter(iterator: Iterable) -> Iterable:
    with open(TIME_PER_BLOCK_PATH, 'a') as file:
        for i in iterator:
            yield i
            print(f"blockNum:{i} time:{time.time() - startTime}", file=file)
            file.flush()


def updateCurrentBlock(iterator: Iterable) -> Iterable:
    with open(LAST_BLOCK_PATH, 'w') as f:
        for i in iterator:
            yield i
            f.seek(0)
            f.write(str(i))


def main():
    web3 = Web3(Web3.HTTPProvider(PROVIDER_URI))
    quickTable, txTable, blockTable = [], [], []
    startBlock = getNextBlock()

    for blockNum in updateCurrentBlock(timePerBlockIter(
            range(startBlock, startBlock + BLOCKS_NUMBER))):
        print(f"blockNum: {blockNum}")

        blockRecord, blockData = createBlockRecord(blockNum, web3)
        blockTable.append(blockRecord)

        for quickRecord, TXRecord in getTransactions(web3, blockData, blockNum):
            quickTable.append(quickRecord)
            txTable.append(TXRecord)

        saveTables(quickTable, txTable, blockTable)
        del quickTable, txTable, blockTable
        quickTable, txTable, blockTable = [], [], []


if __name__ == '__main__':
    main()
