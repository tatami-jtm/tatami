import sys
import os.path as osp
import xml.etree.ElementTree as ET

RULESETS_PATH = osp.join(osp.dirname(osp.abspath(__file__)), "rulesets")

def get_all_lists():
    with open(osp.join(RULESETS_PATH, "registry.txt")) as f:
        registered_lists = f.read().strip().split("\n")
    
    return registered_lists


def load_list_xml(filename):
    with open(osp.join(RULESETS_PATH, f"{filename}.xml")) as f:
        ruleset = f.read()
    
    return ET.fromstring(ruleset)