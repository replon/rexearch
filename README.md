# Rexearch

Regular Expression Search

- A Keyword-search Tool based on Regular Expressions(Regex)
- Support rich rules to extract text spans and attach tags and get representative words.

## Usage

### Define Rules

JSON Example
```json
[
{"regex": "(Bob )?Dylan", "repr": "Bob Dylan"},
{"id": "001", "regex": "(N|n)ame ?: ?([a-zA-Z ]+)", "target_regex_group": 2, "categories": ["PERSON_NAME"]}
]
```
**Rexearch** reads a JSON rule list from your own file. a `rule` may contain following key-values

- **regex** (str) - Whole Regular Expression that you want to search. **Mandatory**.
- **target_regex_group** (int) - The target group number that you want to extract as `raw`. You may want to extract just some part of whole expression.
- **categories** (list of str) - This will put some additional tags on the rule.
- **id** (str) - Set `rule_id` if it needed
- **repr** (str or f-string) - Representative word of this word. You can also write f-string using `{}` and `group(int)` in it. For example, "{group(2)} Month" will generate proper representation based on the `Match.group` object. 

### Search Them All
```python
import rexearch

rx = rexearch.Rexearch()
rx.load_json_file("sample.rexearch.json")
sample_input = open("sample_input.txt", mode="rt").read()
results = rx.search(sample_input)

for result in results:
    print(result)
```
```text
{'raw': 'Bob Dylan', 'start': 0, 'end': 9, 'repr': 'Bob Dylan'}
{'raw': 'Dylan', 'start': 178, 'end': 183, 'repr': 'Bob Dylan'}
{'raw': 'Dylan', 'start': 646, 'end': 651, 'repr': 'Bob Dylan'}
{'raw': 'Bob Dylan', 'start': 731, 'end': 740, 'repr': 'Bob Dylan'}
{'raw': 'Dylan', 'start': 811, 'end': 816, 'repr': 'Bob Dylan'}
{'raw': 'John Smith', 'start': 935, 'end': 945, 'rule_id': 'sample.rule.001', 'categories': ['PERSON_NAME']}
{'raw': 'Dongwook Lee', 'start': 1012, 'end': 1024, 'rule_id': 'sample.rule.001', 'categories': ['PERSON_NAME']}
{'raw': 'Sarah Connor', 'start': 1091, 'end': 1103, 'rule_id': 'sample.rule.001', 'categories': ['PERSON_NAME']}
{'raw': 'Good', 'start': 999, 'end': 1003, 'repr': 'Positive', 'rule_id': 'sample.rule.002', 'categories': ['RATE', 'EMOTION']}
{'raw': 'Great', 'start': 1077, 'end': 1082, 'repr': 'Positive', 'rule_id': 'sample.rule.002', 'categories': ['RATE', 'EMOTION']}
{'raw': '10,000 Dollars', 'start': 888, 'end': 902, 'repr': '$10000', 'rule_id': 'sample.rule.003', 'categories': ['PRICE']}
```

### Set Search Mode
```python
from rexearch import Rexearch, SEARCH_MODE

rx = Rexearch(mode=SEARCH_MODE.SEPARATED)
```

- `SEARCH_MODE.SEPARATED` : Default mode. Search one by one.
- `SEARCH_MODE.UNIFIED` : This mode internally merge the regular expressions with '|' and run a single search. The result should be the same with the default.
- `SEARCH_MODE.MULTI_THREAD` : This mode creates threads for each rule and run concurrently.

*Note - In many cases, the default(separated) mode is faster than others because of handling time.*

### Inject Custom Functions

You can inject your own python function into `rexearch.custom_functions` dict. They can be called by f-string of your `repr` definition

Example
```python
from rexearch import Rexearch
import time
import json

# Define custom function
def get_ctime_str():
    return time.ctime()[4:]

rxch = Rexearch()
rxch.custom_functions["now"] = get_ctime_str # inject custom function 'now'

# in 'repr' you can call a function inside.
json_str = """[
    {
        "regex": "[cC]urrent [tT]ime", 
        "repr":"{custom_function['now']()}",
        "categories":["DATETIME"]
    }
]"""

rxch.load(json.loads(json_str))
input_text = "I'm checking the current time."
result = rxch.search(input_text)
print(result)
```
```text
[{'raw': 'current time', 'start': 17, 'end': 29, 'repr': 'Jan 14 17:35:44 2021', 'categories': ['TIME']}]
```

### Set Validations to Filter Your Results

You can add `validation` of each rule. Rexearch will ignore the match if the validation is failed. It finds your validation function name in `rexearch.custom_functions` dict. Or you can simply write a python *lambda* function.

Example
```python
from rexearch import Rexearch
import json

# Define validation function
def check_id(item):
    if item["raw"] in ["replon87", "dylan", "awesome_id", "supersonic", "Dongwook"]:
        return True
    else:
        return False


rxch = Rexearch()
rxch.custom_functions["check_id"] = check_id

# set 'validation' as custom_function name or lambda function
json_str = """[
{"regex" : "(id)|(ID) ?: ?([_\\\\-0-9a-zA-Z]{2,})", "target_regex_group":3, "categories":["ID"], "validation":"check_id"},
{"regex" : "[aA][gG][eE] ?: ?([1-9][0-9]*)", "target_regex_group":1, "categories":["AGE"], "validation":"lambda x: int(x['raw'])>=15"}]"""

rxch.load(json.loads(json_str))

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
```
```text
[{'raw': '55', 'start': 131, 'end': 133, 'categories': ['AGE']}, {'raw': '25', 'start': 163, 'end': 165, 'categories': ['AGE']}, {'raw': 'supersonic', 'start': 59, 'end': 69, 'categories': ['ID']}, {'raw': 'replon87', 'start': 86, 'end': 94, 'categories': ['ID']}]
```

## Updates

### Version 0.1

- (0.1.0) First runnable. Only supports `SEARCH_MODE.SEPARATE` mode.
- (0.1.1) Rename function `load_json` to `load_json_file`, Added basic tests
- (0.1.2) Support mode `SEARCH_MODE.UNIFIED`
- (0.1.3) Support mode `SEARCH_MODE.MULTI_THREAD`
- (0.1.4) Support `custom_functions` and `validation`
