# Liquidity listener

Listen to PancakeSwap liquidity to detect new pair added.

Send notification to telegram when detect new pair.

## Installation and Usage

### Installation

Use [PIP](https://pypi.org/project/pip/) to install requirements

```bash
pip install -r requirements.txt
```

### Usage

Copy `conf.ini-sample` to new file named `conf.ini`. Modify your config there.

_See [Files Structure](#files-structure) for more information._

Then start app

```bash
python main.py
```

## Files Structure

```
.
├── .gitignore
├── abi
│   ├── erc20.json
│   ├── factory.json
│   └── pair.json
├── conf.ini (your config file)
├── conf.ini-sample
├── main.py
├── README.md
├── requirements.txt
└── utils
    ├── __init__.py
    ├── config.py
    └── evm.py
```

## Feedback

If you have any feedback, please open an issue.

## License

[MIT](LICENSE)
