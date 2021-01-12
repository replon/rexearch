import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # This is just for test env
import rexearch

rx = rexearch.Rexearch()
rx.load_json("sample.rules.json")
sample_input = open("sample.input.txt", mode="rt").read()
results = rx.search(sample_input)
for result in results:
    print(result)
