import time

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


class Token:
    def __init__(self, evm: Evm, token_address: str, erc20_abi, pair_address: str):
        self.address = token_address
        self.contract = evm.create_contract(token_address, erc20_abi)
        try:
            self.symbol = self.contract.functions.symbol().call()
            self.wei_liquid = self.contract.functions.balanceOf(pair_address).call()
            self.decimals = self.contract.functions.decimals().call()
        except Exception as err:
            raise (err)

        self.liquid = self.wei_liquid / (10**self.decimals)


class Pair:
    def __init__(self, evm: Evm, address: str, pair_abi, erc20_abi):
        time.sleep(3)  # Wait for stabilizing
        self.address = address
        self.contract = evm.create_contract(address, pair_abi)

        try:
            token0_adr = self.contract.functions.token0().call()
            token1_adr = self.contract.functions.token1().call()
            self.token0 = Token(evm, token0_adr, erc20_abi, self.address)
            self.token1 = Token(evm, token1_adr, erc20_abi, self.address)
        except Exception as err:
            raise (err)

    def __str__(self):
        return (
            f"Pair: `{self.address}`\n\n"
            + f"Token0: `{self.token0.address}`\n"
            + f"Symbol: {self.token0.symbol}\n"
            + f"Decimals: {self.token0.decimals}\n"
            + f"Liquid: `{self.token0.liquid}`\n\n"
            + f"Token1: `{self.token1.address}`\n"
            + f"Symbol: {self.token1.symbol}\n"
            + f"Decimals: {self.token1.decimals}\n"
            + f"Liquid: `{self.token1.liquid}`"
        )
