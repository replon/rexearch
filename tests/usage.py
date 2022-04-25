import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # This is just for test env
import rexearch  # noqa : E402

def Find_FE():
    return str()

rx = rexearch.Rexearch()
rx.load_json_file("tests/jay.test.rules.json")
sample_input = open("tests/jay.test.input.txt", mode="rt").read()

results = rx.search(sample_input)


hangle_numbers = {'일':1,'이':2,'삼':3,'사':4,'오':5,'육':6,'칠':7,'팔':8,'구':9}

#custom function
def find_FE(price):
  
    #일단위(일~구) 숫자 변환
    tmp = str([hangle_numbers.get(token, token) for token in price])

    

    #숫자와 단위 구분

    #단위 합산


for result in results:
    print(result)