from bs4 import BeautifulSoup
from urllib.request import urlopen

def features_table_to_set(table):
    features = [tr for tr in table.find_all("tr") if 'style' not in tr.attrs.keys()]
    return {tuple(td.text.strip() for td in feature.find_all("td")[:5]) for feature in features} # the 5 elements are as follows: Name, Proposal paper id, GCC Version, Clang Version, MSVC Version
     
def get_cpp_features_set(version_label):
    site = BeautifulSoup(urlopen('https://en.cppreference.com/w/cpp/compiler_support').read(), features = 'html.parser')
    core_features, library_features = list(set([th.parent.parent for th in site.find_all("th") if version_label in th.text]))
    return features_table_to_set(core_features) | features_table_to_set(library_features)


from discord_bot_interface import event, command, task, run

@command
def subscribe(version_label, compilers):
    print(f'{version_label} and {compilers}')

run()