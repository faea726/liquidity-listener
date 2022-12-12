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
        except Exception as err:
            exit(err)
        return self._Telegram(bot_token, channel_id), self._Chain(rpc, weth, f_adr)

    class _Telegram:
        def __init__(self, bot_token, chat_id):
            self.bot_token = bot_token
            self.chat_id = chat_id

    class _Chain:
        def __init__(self, rpc, weth, factory_address):
            self.rpc = rpc
            self.weth = (weth,)
            self.factory_address = factory_address
