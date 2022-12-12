import requests

from utils.config import Config
from utils.evm import Evm


class LiqudityListener:
    def __init__(self, config_file: str):
        self.config = Config(config_file)
        self.evm = Evm(self.config.chain.rpc)
        self.factory_contract = self.evm.create_contract(
            self.config.chain.factory_address, self.config.chain.factory_abi
        )
        try:
            self.all_pairs = self.factory_contract.functions.allPairsLength().call()
        except Exception as err:
            exit(err)

    def run(self):
        while True:
            self._core()

    def _core(self):
        try:
            last_pair = self.factory_contract.functions.allPairsLength().call()
        except Exception as err:
            exit(err)

        if last_pair > self.all_pairs:
            print(last_pair)
            self.all_pairs = last_pair

    def _send_to_telegram(self, message=""):
        api_url = (
            f"https://api.telegram.org/bot{self.config.telegram.bot_token}/sendMessage"
        )

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
                print("[-]", rsp.json()["description"])
        except Exception as err:
            print("[-]", err)


if __name__ == "__main__":
    LiqudityListener("conf.ini").run()
