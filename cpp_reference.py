from bs4 import BeautifulSoup
from urllib.request import urlopen

from random import randint

def features_table_to_set(table):
    features = [tr for tr in table.find_all("tr") if 'style' not in tr.attrs.keys()]
    parse = lambda name, link, gcc, clang, msvc: (("name", name), ("link", link), ("gcc", gcc), ("clang", clang), ("msvc", msvc))
    return {parse(*[td.text.strip() for td in feature.find_all("td")[:5]]) for feature in features}

def get_cpp_features_map():
    site = BeautifulSoup(urlopen('https://en.cppreference.com/w/cpp/compiler_support').read(), features = 'html.parser')
    feature_tables = list(set([(th.text.strip(), th.parent.parent) for th in site.find_all("th") if 'feature' in th.text]))
    versions = list(set([name for name, _ in feature_tables]))
    return {version: set().union(*[features_table_to_set(table) for name, table in feature_tables if name == version]) for version in versions}

def find_difference(diff, ffid):
    to_map = lambda dffd: {(name[1], link[1]): {gcc, clang, msvc} for name, link, gcc, clang, msvc in dffd}
    diff_map, ffid_map = to_map(diff), to_map(ffid)
    specific_differences = [(*key, diff_map[key] - ffid_map[key], ffid_map[key] - diff_map[key]) for key in diff_map.keys()]
    return [f'[{name}](https://wg21.link/{link}): now on {", ".join([f"{compiler} {ver}" for compiler, ver in newvers])}, previously: {", ".join([f"{compiler} {ver}" for compiler, ver in oldvers if ver])}' for name, link, newvers, oldvers in specific_differences]

def compare_to_current(old_features):
    new_features = get_cpp_features_map()
    difference_map = {version: find_difference(new_fts - old_fts, old_fts - new_fts) for (version, new_fts), old_fts in zip(new_features.items(), old_features.values()) if new_fts - old_fts}
    return '\n\n'.join(['\n'.join([f'{version}:', *diff_list]) for version, diff_list in difference_map.items()])