from configparser import ConfigParser

import requests
from web3 import Web3


class LiqudityListener:
    def __init__(self, config_file: str):
        self.config = Config(config_file)

    def run(self):
        print(self.config.telegram.api_token, self.config.chain.rpc)
        self.w3 = Web3(Web3.HTTPProvider(self.config.chain.rpc))
        if not self.w3.isConnected():
            exit(f"Connection:", self.w3.isConnected)

    def __create_contract(web3_provider: Web3, adr, abi):
        """Crate interactable contract"""
        try:
            return web3_provider.eth.contract(address=adr, abi=abi)
        except Exception as e:
            print(e)
            exit()

    def __send_to_telegram(bot_token, chat_id="me", message=""):
        api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        try:
            rsp = requests.post(api_url, json={"chat_id": chat_id, "text": message})
            if rsp.status_code != 200:
                print("[-]", rsp.json()["description"])
        except Exception as err:
            print("[-]", err)


class Pairs:
    def __init__(self):
        self.old = "0x0"
        self.new = "0xdEaD"


class Config:
    def __init__(self, conf_file: str):
        self.telegram, self.chain = self.__read_config(conf_file)

    def __read_config(self, conf_file):
        cfg = ConfigParser()
        try:
            cfg.read(conf_file)

            telegram = cfg["TELEGRAM"]
            api_token = telegram["BOT_TOKEN"]
            channel_id = telegram["CHANNEL_ID"]

            chain = cfg["CHAIN"]
            rpc = chain["RPC"]
            weth = chain["WETH"]
            f_adr = chain["FACTORY_ADR"]
        except Exception as err:
            exit(err)
        return Telegram(api_token, channel_id), Chain(rpc, weth, f_adr)


class Telegram:
    def __init__(self, api_token, chat_id):
        self.api_token = api_token
        self.chat_id = chat_id


class Chain:
    def __init__(self, rpc, weth, factory_address):
        self.rpc = rpc
        self.weth = (weth,)
        self.factory_address = factory_address


LiqudityListener("conf.ini").run()
