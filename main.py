import time

import requests

from utils.config import Config
from utils.evm import Evm


class LiqudityListener:
    class _Pair:
        def __init__(self, evm: Evm, address: str, pair_abi, erc20_abi):
            time.sleep(3)  # Wait for stabilizing
            self.address = address
            contract = evm.create_contract(address, pair_abi)

            try:
                self.token0 = evm.create_contract(
                    str(contract.functions.token0().call()), erc20_abi
                )
                self.token1 = evm.create_contract(
                    str(contract.functions.token1().call()), erc20_abi
                )

                self.token0_symbol = self.token0.functions.symbol().call()
                self.token1_symbol = self.token1.functions.symbol().call()

                self.token0_decimals = self.token0.functions.decimals().call()
                self.token1_decimals = self.token1.functions.decimals().call()

                self.token0_wei_balance = self.token0.functions.balanceOf(
                    self.address
                ).call()
                self.token1_wei_balance = self.token1.functions.balanceOf(
                    self.address
                ).call()
            except Exception as err:
                raise (err)

            self.token0_balance = self.token0_wei_balance / (10**self.token0_decimals)
            self.token1_balance = self.token1_wei_balance / (10**self.token1_decimals)

        def __str__(self):
            return (
                f"Pair: `{self.address}`\n\n"
                + f"Token0: `{self.token0.address}`\n"
                + f"Symbol: {self.token0_symbol}\n"
                + f"Decimals: {self.token0_decimals}\n"
                + f"Liquid: `{self.token0_balance}`\n\n"
                + f"Token1: `{self.token1.address}`\n"
                + f"Symbol: {self.token1_symbol}\n"
                + f"Decimals: {self.token1_decimals}\n"
                + f"Liquid: `{self.token1_balance}`"
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

    def _core(self):
        try:
            last_pair = self.factory_contract.functions.allPairsLength().call()
        except Exception as err:
            raise (err)

        if last_pair > self.all_pairs:
            try:
                self._process(last_pair)
            except Exception as err:
                raise (err)

    def _process(self, last_pair: int):
        for index in range(self.all_pairs, last_pair):
            pair_adr = self.factory_contract.functions.allPairs(index).call()
            pair = self._Pair(
                self.evm,
                pair_adr,
                self.config.chain.PAIR_ABI,
                self.config.chain.ERC20_ABI,
            )

            self._send_to_telegram(pair)
            self.all_pairs = last_pair
            print("[*] Current:", self.all_pairs)

    def _send_to_telegram(self, pair: _Pair):
        api_url = (
            f"https://api.telegram.org/bot{self.config.telegram.bot_token}/sendMessage"
        )

        if (
            pair.token0.address != self.evm.WETH.address
            or pair.token0.address != self.evm.BUSD.address
            or pair.token0.address != self.evm.USDT.address
            or pair.token1.address != self.evm.WETH.address
            or pair.token1.address != self.evm.BUSD.address
            or pair.token1.address != self.evm.USDT.address
        ):
            print(f"[?] {pair.address}")
            return

        if (
            pair.token0_balance <= self.config.telegram.min_liq
            or pair.token1_balance <= self.config.telegram.min_liq
        ):
            print(f"[<] {pair.address}")
            return

        message = pair.__str__()

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
