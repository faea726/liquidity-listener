import time

import requests

from utils.config import Config
from utils.evm import Evm, Pair


class LiqudityListener:
    def __init__(self, config_file: str):
        self.config = Config(config_file)
        self.evm = Evm(
            self.config.chain.RPC_ENDPOINT,
            self.config.chain.BSCSCAN_API_TOKEN,
            self.config.chain.FACTORY_ADDRESS,
            self.config.chain.CHECKER_ADDRESS,
            self.config.chain.WETH_ADDRESS,
            self.config.chain.BUSD_ADDRESS,
            self.config.chain.USDT_ADDRESS,
            self.config.chain.FACTORY_ABI,
            self.config.chain.CHECKER_ABI,
            self.config.chain.ERC20_ABI,
        )

        try:
            self.all_pairs = self.evm.FACTORY.functions.allPairsLength().call()
        except Exception as err:
            exit(err)
        print("[*] Current:", self.all_pairs)

    def run(self):
        while True:
            try:
                self._core()
            except Exception as err:
                print(err)
                pass

    def _core(self):
        try:
            last_pair = self.evm.FACTORY.functions.allPairsLength().call()
        except Exception as err:
            raise (err)

        if last_pair > self.all_pairs:
            try:
                self._process(last_pair)
            except Exception as err:
                raise (err)

    def _process(self, last_pair: int):
        for index in range(self.all_pairs, last_pair):
            try:
                pair_adr = self.evm.FACTORY.functions.allPairs(index).call()
                pair = Pair(
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

    def _send_to_telegram(self, pair: Pair):
        if pair.is_honeypot:
            print(
                f"[!] {pair.token0.symbol} + {pair.token1.symbol} = https://bscscan.com/address/{pair.address}"
            )
            return

        if (
            (
                pair.token0.address == self.evm.WETH.address
                and pair.token0.liquid < self.config.telegram.min_liq_e
            )
            or (
                pair.token1.address == self.evm.WETH.address
                and pair.token1.liquid < self.config.telegram.min_liq_e
            )
            or (
                pair.token0.address in self.evm.VALID_LIST
                and pair.token0.liquid < self.config.telegram.min_liq_u
            )
            or (
                pair.token1.address in self.evm.VALID_LIST
                and pair.token1.liquid < self.config.telegram.min_liq_u
            )
        ):
            print(
                f"[<] {pair.token0.symbol} + {pair.token1.symbol} = https://bscscan.com/address/{pair.address}"
            )
            return

        api_url = (
            f"https://api.telegram.org/bot{self.config.telegram.bot_token}/sendMessage"
        )
        message = pair.serialize()

        try:
            rsp = requests.post(
                api_url,
                json={
                    "chat_id": self.config.telegram.chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
                timeout=3,
            )
            if rsp.status_code != 200:
                print(
                    f"[-]{pair.address}\n",
                    f"  [?] {rsp.json()['description']}",
                )
            else:
                print("[+]", pair.poocoin_url)
        except Exception as err:
            print("[-]", err)


if __name__ == "__main__":
    LiqudityListener("conf.ini").run()
