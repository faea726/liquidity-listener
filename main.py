import requests

from utils.config import Config
from utils.evm import Evm


class LiqudityListener:
    def __init__(self, config_file: str):
        self.config = Config(config_file)
        self.evm = Evm(self.config.chain.rpc)

    def run(self):
        print(self.config.telegram.bot_token, self.config.chain.rpc)

    def _send_to_telegram(self, message=""):
        api_url = (
            f"https://api.telegram.org/bot{self.config.telegram.bot_token}/sendMessage"
        )

        try:
            rsp = requests.post(
                api_url, json={"chat_id": self.config.telegram.chat_id, "text": message}
            )
            if rsp.status_code != 200:
                print("[-]", rsp.json()["description"])
        except Exception as err:
            print("[-]", err)

    class _Pairs:
        def __init__(self):
            self.old = "0x0"
            self.new = "0xdEaD"


if __name__ == "__main__":
    LiqudityListener("conf.ini").run()
