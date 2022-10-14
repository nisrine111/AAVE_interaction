from brownie import accounts, network, config, interface
from scripts.helpful_functions import (
    get_account,
    get_lending_pool,
    approve_erc20,
    borrowable_amount,
    get_asset_price,
)
from scripts.get_wrapped_eth import get_weth, LOCAL_ENV, FORKED_ENV
from web3 import Web3


def main():
    account = get_account()
    weth_token_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()

    # get lending pool
    lending_pool = get_lending_pool()
    # approve dai token
    dai_token_address = config["networks"][network.show_active()]["dai_token"]
    AMOUNT = 0.01 * 10 ** 18
    tx = approve_erc20(lending_pool.address, AMOUNT, weth_token_address, account)
    tx.wait(1)
    print("depositing WEth ...")
    # depositing
    depo_tx = lending_pool.deposit(
        weth_token_address, AMOUNT, account.address, 0, {"from": account}
    )
    depo_tx.wait(1)
    print(f"you ve deposited {AMOUNT} amount of weth")

    # eth dai price
    print("let s borrow DAI ...")
    (available_eth_to_borrow, debt) = borrowable_amount(lending_pool, account)
    dai_eth_price = get_asset_price()

    amount_of_dai_to_borrow = available_eth_to_borrow * 0.8 / dai_eth_price

    borrowing_tx = lending_pool.borrow(
        dai_token_address,
        amount_of_dai_to_borrow,
        1,
        0,
        account.address,
        {"from": account},
    )
    borrowing_tx.wait(1)
    print(f" you ve borrowed {amount_of_dai_to_borrow} amount of DAI")

    # approving our DAI
    aprv_tx = approve_erc20(
        lending_pool.address,
        Web3.toWei(amount_of_dai_to_borrow, "ether"),
        dai_token_address,
        account,
    )
    aprv_tx.wait(1)
    repay_tx = lending_pool.repay(
        dai_token_address,
        Web3.toWei(amount_of_dai_to_borrow, "ether"),
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("you ve payed your debt !")
