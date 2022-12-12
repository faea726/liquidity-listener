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
            min_liq_e = int(telegram["MIN_LIQUID_E"])
            min_liq_u = int(telegram["MIN_LIQUID_U"])

            chain = cfg["CHAIN"]

            RPC_ENDPOINT = chain["RPC"]
            FACTORY_ADDRESS = chain["FACTORY_ADDRESS"]
            WETH_ADDRESS = chain["WETH_ADDRESS"]
            BUSD_ADDRESS = chain["BUSD_ADDRESS"]
            USDT_ADDRESS = chain["USDT_ADDRESS"]

            factory_abi_path = chain["FACTORY_ABI_PATH"]
            erc20_abi_path = chain["ERC20_ABI_PATH"]
            pair_abi_path = chain["PAIR_ABI_PATH"]
        except Exception as err:
            exit(err)
        return self._Telegram(bot_token, channel_id, min_liq_e, min_liq_u), self._Chain(
            RPC_ENDPOINT,
            FACTORY_ADDRESS,
            WETH_ADDRESS,
            BUSD_ADDRESS,
            USDT_ADDRESS,
            erc20_abi_path,
            factory_abi_path,
            pair_abi_path,
        )

    class _Telegram:
        def __init__(self, bot_token, chat_id, min_liq_e, min_liq_u):
            self.bot_token = bot_token
            self.chat_id = chat_id
            self.min_liq_e = min_liq_e
            self.min_liq_u = min_liq_u

    class _Chain:
        def __init__(
            self,
            rpc_endpoint,
            factory_address,
            weth_address,
            busd_address,
            usdt_address,
            erc20_abi_path,
            factory_abi_path,
            pair_abi_path,
        ):
            self.RPC_ENDPOINT = rpc_endpoint
            self.FACTORY_ADDRESS = factory_address

            self.WETH_ADDRESS = weth_address
            self.BUSD_ADDRESS = busd_address
            self.USDT_ADDRESS = usdt_address
            try:
                self.FACTORY_ABI = json.load(open(factory_abi_path))
                self.ERC20_ABI = json.load(open(erc20_abi_path))
                self.PAIR_ABI = json.load(open(pair_abi_path))
            except Exception as err:
                exit(err)
