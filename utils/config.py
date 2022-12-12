import json
from configparser import ConfigParser


class Config:
    """Config for app"""

    def __init__(self, conf_file: str):
        self.telegram, self.chain = self._read_config(conf_file)

    def _read_config(self, conf_file):
        """Red config from file

        Args:
            conf_file (str): config file name

        Returns:
            _Telegram, _Chain: Config instance
        """
        cfg = ConfigParser()
        try:
            cfg.read(conf_file)

            telegram = cfg["TELEGRAM"]
            bot_token = telegram["BOT_TOKEN"]
            channel_id = telegram["CHANNEL_ID"]

            chain = cfg["CHAIN"]
            rpc = chain["RPC"]
            weth = chain["WETH"]
            f_adr = chain["FACTORY_ADR"]
            factory_abi_path = chain["FACTORY_ABI_PATH"]
            erc20_abi_path = chain["ERC20_ABI_PATH"]
            pair_abi_path = chain["PAIR_ABI_PATH"]
        except Exception as err:
            exit(err)
        return self._Telegram(bot_token, channel_id), self._Chain(
            rpc, weth, f_adr, erc20_abi_path, factory_abi_path, pair_abi_path
        )

    class _Telegram:
        def __init__(self, bot_token, chat_id):
            self.bot_token = bot_token
            self.chat_id = chat_id

    class _Chain:
        def __init__(
            self,
            rpc,
            weth,
            factory_address,
            erc20_abi_path,
            factory_abi_path,
            pair_abi_path,
        ):
            self.rpc = rpc
            self.weth = (weth,)
            self.factory_address = factory_address
            try:
                self.factory_abi = json.load(open(factory_abi_path))
                self.erc20_abi = json.load(open(erc20_abi_path))
                self.pair_abi = json.load(open(pair_abi_path))
            except Exception as err:
                exit(err)
