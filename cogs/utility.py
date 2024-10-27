import sys
import os
import random


countries = ["eg", "it"]
proxies = [
    "socks5://customer-AlmavivaScript1337_iwH5v:1nsjo4c1ucup58sA_@pr.oxylabs.io:7777",
    "socks5://b8pb7rusmp1hwbj:1nsjo4c1ucup58s@rp.proxyscrape.com:6060",
    "socks5://h6gpTLfsq8tdFOnF:1nsjo4c1ucup58s@geo.iproyal.com:32325",
    "socks5://user_650e19,type_residential:c6cbcc@portal.anyip.io:1080",
    # "socks5://lumi-AlmavivaScript_area:7hpLjYhIGyEI4KuV@eu.lumiproxy.com:5888",
    "socks5://package-10001:ZZc3kDJUcbq5vIxA@rotating.proxyempire.io:5000",
]

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def generate_random_str():
    string = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    return "".join(random.choice(string) for _ in range(8))


def rotate_proxy(async_session=False):
    try:
        random_proxy = random.choice(proxies).format(random.choice(countries))
    except Exception as e:
        random_proxy = random.choice(proxies)
    
    if async_session:
        return random_proxy
    return {
        "http": random_proxy,
        "https": random_proxy,
    }
