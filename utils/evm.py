import requests
from web3 import Web3


class Evm:
    """EVM helper"""

    def __init__(
        self,
        http_rpc_endpoint: str,
        factory_address: str,
        checker_address: str,
        weth_adr: str,
        busd_adr: str,
        usdt_adr: str,
        factory_abi,
        checker_abi,
        erc20_abi,
    ):
        self.web3 = Web3(Web3.HTTPProvider(http_rpc_endpoint))

        self.FACTORY = self.create_contract(factory_address, factory_abi)
        self.CHECKER = self.create_contract(checker_address, checker_abi)

        self.WETH = self.create_contract(weth_adr, erc20_abi)
        self.BUSD = self.create_contract(busd_adr, erc20_abi)
        self.USDT = self.create_contract(usdt_adr, erc20_abi)

        self.VALID_LIST = [self.WETH.address, self.BUSD.address, self.USDT.address]

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
        self.address = address
        self.contract = evm.create_contract(address, pair_abi)
        self.valid_list = evm.VALID_LIST

        try:
            token0_adr = self.contract.functions.token0().call()
            token1_adr = self.contract.functions.token1().call()
            self.token0 = Token(evm, token0_adr, erc20_abi, self.address)
            self.token1 = Token(evm, token1_adr, erc20_abi, self.address)
            self.is_honeypot = self._check_honeypot(evm)
        except Exception as err:
            raise (err)

    def _check_honeypot(self, evm: Evm):
        self.is_honeypot = True
        if (
            self.token0.address not in self.valid_list
            and self.token1.address not in self.valid_list
        ):
            return True

        self.poocoin_url = "https://poocoin.app/tokens/"

        if self.token0.address not in self.valid_list and not self._is_honeypot(
            evm, self.token0.address
        ):
            self.poocoin_url += str(self.token0.address)
            return False

        if not self._is_honeypot(evm, self.token1.address):
            self.poocoin_url += str(self.token1.address)
            return False

        return True

    def _is_honeypot(self, evm: Evm, token_address: str):
        try:
            [
                buy_estimate,
                buy_real,
                sell_estimate,
                sell_real,
                self.buyable,
                _,
                self.sellable,
            ] = evm.CHECKER.functions.getTokenInformations(token_address).call()
        except Exception as err:
            return True

        if not self.buyable and not self.sellable:
            return True

        self.buy_tax = round(((buy_estimate - buy_real) / buy_estimate) * 100, 2)
        self.sell_tax = round(((sell_estimate - sell_real) / sell_estimate) * 100, 2)

        return False

    def serialize(self):
        """Serialize data to telegram message"""
        if self.is_honeypot:
            return ""

        return (
            f"Pair: <code>{self.address}</code>\n\n"
            + f"Token0: <a href='https://bscscan.com/address/{self.token0.address}'>{self.token0.address}</a>\n"
            + f"Symbol: <b>{self.token0.symbol}</b>\n"
            + f"Decimals: <code>{self.token0.decimals}</code>\n"
            + f"Liquid: <code>{self.token0.liquid}</code>\n\n"
            + f"Token1: <a href='https://bscscan.com/address/{self.token1.address}'>{self.token1.address}</a>\n"
            + f"Symbol: <b>{self.token1.symbol}</b>\n"
            + f"Decimals: <code>{self.token1.decimals}</code>\n"
            + f"Liquid: <code>{self.token1.liquid}</code>\n\n"
            + f"<a href='{self.poocoin_url}'><b>Poocoin link</b></a>\n"
            + f"Buy Tax: <code>{self.buy_tax}</code>, Sell Tax: <code>{self.sell_tax}</code>"
        )
