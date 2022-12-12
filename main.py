import time

import requests

from utils.config import Config
from utils.evm import Evm


class LiqudityListener:
    class _Pair:
        class _Token:
            def __init__(
                self, evm: Evm, token_address: str, erc20_abi, pair_address: str
            ):
                self.address = token_address
                self.contract = evm.create_contract(token_address, erc20_abi)
                try:
                    self.symbol = self.contract.functions.symbol().call()
                    self.wei_liquid = self.contract.functions.balanceOf(
                        pair_address
                    ).call()
                    self.decimals = self.contract.functions.decimals().call()
                except Exception as err:
                    raise (err)

                self.liquid = self.wei_liquid / (10**self.decimals)

        def __init__(self, evm: Evm, address: str, pair_abi, erc20_abi):
            time.sleep(3)  # Wait for stabilizing
            self.address = address
            self.contract = evm.create_contract(address, pair_abi)

            try:
                token0_adr = self.contract.functions.token0().call()
                token1_adr = self.contract.functions.token1().call()
                self.token0 = self._Token(evm, token0_adr, erc20_abi, self.address)
                self.token1 = self._Token(evm, token1_adr, erc20_abi, self.address)
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

    def __init__(self, config_file: str):
        self.config = Config(config_file)
        self.evm = Evm(
            self.config.chain.RPC_ENDPOINT,
            self.config.chain.WETH_ADDRESS,
            self.config.chain.BUSD_ADDRESS,
            self.config.chain.USDT_ADDRESS,
            self.config.chain.ERC20_ABI,
        )

        self.factory_contract = self.evm.create_contract(
            self.config.chain.FACTORY_ADDRESS, self.config.chain.FACTORY_ABI
        )

        try:
            self.all_pairs = self.factory_contract.functions.allPairsLength().call()
        except Exception as err:
            exit(err)
        print("[*] Current:", self.all_pairs)

    def run(self):
        while True:
            try:
                self._core()
            except Exception as err:
                print("[-]", err)
            break

    def _core(self):
        try:
            last_pair = self.factory_contract.functions.allPairsLength().call()
        except Exception as err:
            raise (err)

        if last_pair >= self.all_pairs:
            try:
                self._process(last_pair)
            except Exception as err:
                raise (err)

    def _process(self, last_pair: int):
        for index in range(self.all_pairs - 1, last_pair):
            try:
                pair_adr = self.factory_contract.functions.allPairs(index).call()
                pair = self._Pair(
                    self.evm,
                    pair_adr,
                    self.config.chain.PAIR_ABI,
                    self.config.chain.ERC20_ABI,
                )
            except Exception as err:
                raise (err)

            self._send_to_telegram(pair)
            self.all_pairs = last_pair
            print("[*] Current:", self.all_pairs)

    def _send_to_telegram(self, pair: _Pair):
        api_url = (
            f"https://api.telegram.org/bot{self.config.telegram.bot_token}/sendMessage"
        )
        message = pair.__str__()
        # print(message)
        # return

        try:
            rsp = requests.post(
                api_url,
                json={
                    "chat_id": self.config.telegram.chat_id,
                    "text": message,
                    "parse_mode": "MarkdownV2",
                },
            )
            if rsp.status_code != 200:
                print(
                    f"[-]{pair.address}\n",
                    f"  [?] {rsp.json()['description']}",
                )
            else:
                print("[+]", pair.address)
        except Exception as err:
            print("[-]", err)


if __name__ == "__main__":
    LiqudityListener("conf.ini").run()
