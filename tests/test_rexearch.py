import json

from rexearch import Rexearch


def test_list_load():
    json_str = """[
    {"regex" : "(Bob )?Dylan", "repr": "Bob Dylan"},
    {"id": "MY_ID", "regex": "(N|n)ame ?: ?([a-zA-Z ]+)",
    "target_regex_group": 2,"categories": ["PERSON_NAME"]}
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
    name_results = list([item for item in results if "categories" in item and "PERSON_NAME" in item["categories"]])
    assert len(name_results) == 2

    names = set([item["raw"] for item in name_results])
    assert names == {"Dongwook Lee", "Jason"}
