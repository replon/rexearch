import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # This is just for test env
from rexearch import SEARCH_MODE, Rexearch  # noqa : E402

sample_input = open("sample.input.txt", mode="rt").read()

rx_separated_mode = Rexearch(SEARCH_MODE.SEPARATED)
rx_separated_mode.load_json_file("sample.rules.json")

start = time.time()
results_separated = rx_separated_mode.search(sample_input)
end = time.time()

for result in results_separated:
    print(result)
print(f"Separated-mode Search time : {end-start} sec")


rx_unified_mode = Rexearch(SEARCH_MODE.UNIFIED)
rx_unified_mode.load_json_file("sample.rules.json")

start = time.time()
results_unified = rx_unified_mode.search(sample_input)
end = time.time()

assert sorted([str(item) for item in results_separated]) == sorted([str(item) for item in results_unified])

print(f"Unified-mode Search time : {end-start} sec")
