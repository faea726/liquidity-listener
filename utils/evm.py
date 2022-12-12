from web3 import Web3


class Evm:
    """EVM helper"""

    def __init__(self, http_rpc_endpoint: str, weth_adr, busd_adr, usdt_adr, erc20_abi):
        self.web3 = Web3(Web3.HTTPProvider(http_rpc_endpoint))
        self._setTokens(weth_adr, busd_adr, usdt_adr, erc20_abi)
        print("[*] Connected:", self.web3.isConnected())
        if not self.web3.isConnected():
            exit(1)

    def create_contract(self, address: str, abi):
        """Crate interactable contract"""
        try:
            return self.web3.eth.contract(
                address=Web3.toChecksumAddress(address), abi=abi
            )
        except Exception as err:
            exit(err)

    def _setTokens(self, weth_adr: str, busd_adr: str, usdt_adr: str, erc20_abi):
        self.WETH = self.create_contract(weth_adr, erc20_abi)
        self.BUSD = self.create_contract(busd_adr, erc20_abi)
        self.USDT = self.create_contract(usdt_adr, erc20_abi)
