import json
import time

from rexearch import SEARCH_MODE, Rexearch


def test_list_load():
    json_str = """[
    {"regex" : "(Bob )?Dylan", "repr": "Bob Dylan"},
    {"id": "MY_ID", "regex": "(N|n)ame ?: ?([a-zA-Z ]+)",
    "target_regex_group": 2,"tags": ["PERSON_NAME"]}
    ]"""
    rxch = Rexearch()
    assert rxch.rules is None
    rxch.load(json.loads(json_str))
    assert len(rxch.rules) == 2
    return rxch


def test_json_file_load():
    rxch = Rexearch()
    assert rxch.rules is None
    rxch.load_json_file("tests/sample.rules.json")
    assert len(rxch.rules) > 0
    return rxch


def test_search_and_get_repr():
    rxch = test_list_load()
    results = rxch.search(
        "In June 1961, Dylan had signed an agreement with Roy Silver. In 1962, Grossman paid Silver 10,000 Dollars to "
        "become sole manager. "
    )

    assert len(results) == 1
    assert results[0]["repr"] == "Bob Dylan"


def test_extract_target_raw():
    rxch = test_list_load()
    results = rxch.search(
        """Name:Dongwook Lee
        name : Jason
        NAME:Albert Grossman
        Dylan made two important career moves in August 1962: he legally changed his name to Bob Dylan,
        and signed a management contract with Albert Grossman.
        """
    )
    name_results = list([item for item in results if "tags" in item and "PERSON_NAME" in item["tags"]])
    assert len(name_results) == 2

    names = set([item["raw"] for item in name_results])
    assert names == {"Dongwook Lee", "Jason"}


def test_unified_search():
    rxch = Rexearch(mode=SEARCH_MODE.UNIFIED)
    rxch.load_json_file("tests/sample.rules.json")
    assert len(rxch.rules) > 0
    results = rxch.search(
        "In June 1961, Dylan had signed an agreement with Roy Silver. In 1962, Grossman paid Silver 10,000 Dollars to "
        "become sole manager. "
    )
    assert len(results) == 2
    for item in results:
        if item["raw"] == "Dylan":
            assert item["start"] == 14
        elif item["raw"] == "10,000 Dollars":
            assert item["start"] == 91
        else:
            assert False

    return rxch


def test_same_result():
    sample_input = open("tests/sample.input.txt", mode="rt").read()

    rxch_separated = Rexearch(mode=SEARCH_MODE.SEPARATED)
    rxch_separated.load_json_file("tests/sample.rules.json")

    rxch_unified = Rexearch(mode=SEARCH_MODE.UNIFIED)
    rxch_unified.load_json_file("tests/sample.rules.json")

    rxch_multi_thread = Rexearch(mode=SEARCH_MODE.MULTI_THREAD)
    rxch_multi_thread.load_json_file("tests/sample.rules.json")

    results_separated = rxch_separated.search(sample_input)
    results_unified = rxch_unified.search(sample_input)
    results_multi_thread = rxch_multi_thread.search(sample_input)

    assert sorted([str(item) for item in results_separated]) == sorted([str(item) for item in results_unified])
    assert sorted([str(item) for item in results_separated]) == sorted([str(item) for item in results_multi_thread])


def test_valid_check():
    json_str = """[
    {"regex" : "[aA][gG][eE] ?: ?([1-9][0-9]*)", "target_regex_group":1, "tags":["AGE"], "validation":"lambda x: int(x['raw'])>=15"},
    {"regex" : "(id)|(ID) ?: ?([_\\\\-0-9a-zA-Z]{2,})", "target_regex_group":3, "tags":["ID"], "validation":"check_id"}]"""

    def check_id(item):
        if item["raw"] in ["replon87", "dylan", "awesome_id", "supersonic", "Dongwook"]:
            return True
        else:
            return False

    rxch = Rexearch()
    rxch.load(json.loads(json_str))
    assert len(rxch.rules) == 2

    rxch.custom_functions["check_id"] = check_id
    input_text = """
    Name: John
    Name: dylan
    Name: Dongwook
    ID: supersonic (valid)
    ID: replon87 (valid)
    ID: invalid_id
    Age: 55 (valid)
    Age: 12
    Age: 25 (valid)
    """
    result = rxch.search(input_text)
    print(result)
    assert len(result) == 4


def test_custom_function():
    json_str = """[
    {"regex": "[cC]urrent [tT]ime", "repr":"{custom_function['now']()}", "tags":["DATETIME"]}
    ]"""

    def get_ctime_str():
        return time.ctime()[4:]

    rxch = Rexearch()
    rxch.load(json.loads(json_str))
    assert len(rxch.rules) == 1

    rxch.custom_functions["now"] = get_ctime_str

    input_text = "I'm checking the current time."
    result = rxch.search(input_text)
    print(result)
    assert len(result) == 1
