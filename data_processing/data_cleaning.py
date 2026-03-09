import re

import numpy as np
import pandas as pd
from pandas import isna
from ast import literal_eval
from urllib.parse import urlparse



def clean_text(to_clean):
    if not isinstance(to_clean, str) or len(to_clean) == 0:
        return to_clean
    # Substitute all non-printable ASCII characters(see: https://www.ascii-code.com/) with spaces(to avoid words junction).
    cleaned = re.sub(r'[^ -~]|_', " ", to_clean)
    cleaned = re.sub(r'<.*>', " ", cleaned)
    cleaned = re.sub(r'\s+', " ", cleaned).strip()

    # if most of the initial string was cleaned, consider it corrupted and substitute with empty string
    if (len(cleaned) / len(to_clean)) < 0.45:
        return ""

    return cleaned


def convert_to_json(string):
    if isna(string) or not isinstance(string, str):
        return None

    try:
        return literal_eval(string)
    except (ValueError, SyntaxError):
        return {}


def reformat_messy_dict(messy_dict):
    """
    Restructures dictionaries where key-value pairs are embedded
    within the strings of the dict keys and values.
    """

    if not isinstance(messy_dict, dict):
        return np.nan

    clean_dict = {}

    for k, v in messy_dict.items():
        # 1. Clean up non-breaking spaces and stripping whitespace
        k = k.replace('\xa0', ' ').strip()
        v = v.replace('\xa0', ' ').strip()

        # Helper to split "Key: Value" strings
        def split_pair(s):
            if ':' in s:
                parts = s.split(':', 1)
                return parts[0].strip(), parts[1].strip()
            return None, s

        k_key, k_val = split_pair(k)
        v_key, v_val = split_pair(v)

        # Case 1: Both dict-key and dict-value contain their own pairs
        # Example: {'Includes: Bolts': 'Item: Bushing'}
        if k_key and v_key:
            clean_dict[k_key] = k_val
            clean_dict[v_key] = v_val

        elif not k_key:
            clean_dict[k] = v_val

        else:
            if k_key: clean_dict[k_key] = k_val
            if v_key: clean_dict[v_key] = v_val
            elif not v_key and not k_key: clean_dict[k] = v

    return clean_dict


def parse_list_to_dict(input_list):
    if not isinstance(input_list, list):
        return np.nan

    final_dict = {}
    for item in input_list:
        for key, value in item.items():
            # Optional: Clean up the '[value]' format to just 'value'
            clean_value = value.strip('[]')
            final_dict[key] = clean_value

    return final_dict


def parse_web_url(row):
    url = row["url"]
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    name = domain.replace('www.', '')
    name = name.split('.')[0]
    display_name = name.replace('-', ' ')

    return display_name, domain