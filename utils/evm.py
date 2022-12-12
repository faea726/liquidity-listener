from web3 import Web3


class Evm:
    """EVM helper"""

    def __init__(self, http_rpc_endpoint: str):
        self.web3 = Web3(Web3.HTTPProvider(http_rpc_endpoint))
        print(f"Connected:", self.web3.isConnected())
        if not self.web3.isConnected():
            exit(1)

    def create_contract(self, adr, abi):
        """Crate interactable contract"""
        try:
            return self.web3.eth.contract(address=adr, abi=abi)
        except Exception as err:
            exit(err)
