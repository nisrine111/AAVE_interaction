from brownie import accounts,network,config,interface
from scripts.helpful_functions import LOCAL_ENV,FORKED_ENV, get_account


# in this fuction we deposit eth and we mint weth
def get_weth():
    account= get_account()
    weth= interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx= weth.deposit({'from':account, 'value': 0.1*10**18})
    tx.wait(1)
    print( ' you now have 0.1 worth of weth !')


def main():
    get_weth()