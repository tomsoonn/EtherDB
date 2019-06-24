import uuid
from concurrent.futures import ThreadPoolExecutor, Future
from typing import List, Iterable, Tuple

from web3 import Web3
from web3.datastructures import AttributeDict

from database.organize import createQuickRecord, createTxRecord


class FutureWrapper:
    def __init__(self, future: Future):
        self.future = future

    def get(self, timeout):
        result = self.future.result(timeout)
        if result is None:
            return {'error': f"No response within {timeout}s"}
        else:
            return {'result': result}


def asyncRequest(self: Web3.RequestManager, executor: ThreadPoolExecutor,
                 method: str, hash_) -> uuid.UUID:
    future = executor.submit(self.request_blocking, method, [hash_])
    request_id = uuid.uuid4()
    self.pending_requests[request_id] = FutureWrapper(future)
    return request_id


def getTransactions(web3: Web3, block_data: AttributeDict,
                    block: int) -> Iterable[Tuple[List, List]]:
    requestIds = []
    with ThreadPoolExecutor(max_workers=60) as executor:
        for hash_ in block_data['transactions']:
            transactionId = asyncRequest(web3.manager, executor, "eth_getTransactionByHash", hash_)
            trReceiptId = asyncRequest(web3.manager, executor, "eth_getTransactionReceipt", hash_)
            requestIds.append((transactionId, trReceiptId))

    for tId, trId in requestIds:
        try:
            transactionData = web3.manager.receive_blocking(tId, timeout=3)
            trReceiptData = web3.manager.receive_blocking(trId, timeout=3)
        except ValueError as error:
            print(str(error))
            continue

        quickRecord, transactionData = createQuickRecord(transactionData, block, web3)
        TXRecord = createTxRecord(trReceiptData, transactionData, web3)

        yield quickRecord, TXRecord
