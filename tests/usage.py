import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # This is just for test env
import rexearch  # noqa : E402

def Find_FE():
    return str()

rx = rexearch.Rexearch()
rx.load_json_file("tests/jay.test.rules.json")
sample_input = open("tests/jay.test.input.txt", mode="rt").read()
rx.custom_functions["Find_FE"] = Find_FE


results = rx.search(sample_input)



for result in results:
    print(result)