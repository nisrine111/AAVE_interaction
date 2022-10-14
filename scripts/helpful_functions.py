from brownie import accounts, network, config, interface
from web3 import Web3


LOCAL_ENV = ["development"]
FORKED_ENV = ["mainnet-fork", "mainnet-fork-dev"]


def get_account(id=None, index=None):
    if network.show_active() in LOCAL_ENV or network.show_active() in FORKED_ENV:
        return accounts[0]
    if id:
        return accounts.load(id)
    if index:
        return accounts[index]
    else:
        return accounts.add(config["wallets"]["from_key"])


def get_lending_pool():
    addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def approve_erc20(spender, amount, erc20_address, account):

    print("approving ERC20 token ...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("ERC20 token approved!")
    return tx


def get_asset_price():

    if network.show_active() == "goerli":
        # dai-usd
        price_feed_dai_usd = interface.AggregatorV3Interface(
            config["networks"][network.show_active()]["dai_usd_price_feed"]
        )
        dai_usd = price_feed_dai_usd.latestRoundData()[1]
        dai_usd_price = Web3.fromWei(dai_usd, "ether")
        # eth-usd
        price_feed_eth_usd = interface.AggregatorV3Interface(
            config["networks"][network.show_active()]["eth_usd_price_feed"]
        )
        eth_usd = price_feed_eth_usd.latestRoundData()[1]
        eth_usd_price = Web3.fromWei(eth_usd, "ether")

        # ratio
        dai_eth_price = dai_usd_price / eth_usd_price
        print(f" the DAI/ETH price is {dai_eth_price}")
        return float(dai_eth_price)
    else:
        price_feed = interface.AggregatorV3Interface(
            config["networks"][network.show_active()]["dai_eth_price_feed"]
        )
        dai_eth = price_feed.latestRoundData()[1]
        dai_eth_price = Web3.fromWei(dai_eth, "ether")
        print(f" the DAI/ETH price is {dai_eth_price}")
        return float(dai_eth_price)


def borrowable_amount(lending_pool, account):

    (
        totalCollateralETH,
        totalDebtETH,
        availableBorrowsETH,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = lending_pool.getUserAccountData(account.address)
    available_eth_to_borrow = Web3.fromWei(availableBorrowsETH, "ether")
    debt = Web3.fromWei(totalDebtETH, "ether")
    print(f" you can borrow {available_eth_to_borrow}  amount of ETH ")
    print(f" you have {debt} amount of debt")

    return (float(available_eth_to_borrow), float(debt))
