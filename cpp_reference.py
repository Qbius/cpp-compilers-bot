from bs4 import BeautifulSoup
from urllib.request import urlopen

from random import randint

def features_table_to_set(table):
    features = [tr for tr in table.find_all("tr") if 'style' not in tr.attrs.keys()]
    parse = lambda name, link, gcc, clang, msvc: (("name", name), ("link", link), ("gcc", gcc if randint(1, 100) < 100 else "hehe"), ("clang", clang), ("msvc", msvc))
    return {parse(*[td.text.strip() for td in feature.find_all("td")[:5]]) for feature in features} # the 5 elements are as follows: Name, Proposal paper id, GCC Version, Clang Version, MSVC Version
     
def get_cpp_features_map():
    site = BeautifulSoup(urlopen('https://en.cppreference.com/w/cpp/compiler_support').read(), features = 'html.parser')
    feature_tables = list(set([(th.text.strip(), th.parent.parent) for th in site.find_all("th") if 'feature' in th.text]))
    versions = list(set([name for name, _ in feature_tables]))
    return {version: set().union(*[features_table_to_set(table) for name, table in feature_tables if name == version]) for version in versions}