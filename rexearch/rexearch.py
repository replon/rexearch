import concurrent.futures
import csv
import json
import re
from enum import Enum

SEARCH_MODE = Enum("SEARCH_MODE", "SEPARATED UNIFIED MULTI_THREAD")


class Rexearch:
    """
    @author Dylan Lee
    @since 0.1.0
    """

    def __init__(self, mode=SEARCH_MODE.SEPARATED, auto_rule_id=False):
        self.mode = mode
        self.auto_rule_id = auto_rule_id
        self.rules = None

        self.unified_regex = None
        self.group_num_to_rule_num = None

        self.custom_functions = dict()

        self.eval_function_hash = dict()

    def load(self, rules):
        self.rules = []
        # Compile rules in advance
        if self.mode is SEARCH_MODE.SEPARATED or self.mode is SEARCH_MODE.MULTI_THREAD:
            for i, rule in enumerate(rules):
                if "regex" not in rule:
                    print(f'Cannot find "regex" field. ignored : {str(rule)}')
                    continue
                if "id" not in rule and self.auto_rule_id:
                    rule["id"] = f"UNNAMED_RULE_{i}"
                rule["__regex_compiled"] = re.compile(rule["regex"])
                self.rules.append(rule)
        elif self.mode is SEARCH_MODE.UNIFIED:
            offset = 0
            self.group_num_to_rule_num = dict()
            unified_regex_str = ""
            for i, rule in enumerate(rules):
                if "regex" not in rule:
                    print(f'Cannot find "regex" field. ignored : {str(rule)}')
                    continue
                if "id" not in rule and self.auto_rule_id:
                    rule["id"] = f"UNNAMED_RULE_{i}"
                unified_regex_str = "|".join([unified_regex_str, "(" + rule["regex"] + ")"])
                rule["__group_offset"] = offset + 1
                self.group_num_to_rule_num[offset + 1] = i
                offset += re.compile(rule["regex"]).groups + 1
                self.rules.append(rule)
            self.unified_regex = re.compile(unified_regex_str)

        if len(self.rules) > 0:
            print(f"{len(self.rules)} rules loaded")
        else:
            raise ValueError("Cannot find rules")

    def load_json_file(self, filepath, encoding="utf-8"):
        with open(filepath, mode="rt", encoding=encoding) as ifs:
            obj = json.load(ifs)
            if "rules" in obj:
                self.load(obj["rules"])
            elif type(obj) is list:
                self.load(obj)
            else:
                raise ValueError(f"Cannot find rules in the file {filepath}")

    def load_csv_file(self, filepath, encoding="utf-8"):
        with open(filepath, mode="rt", encoding=encoding) as ifs:
            reader = csv.DictReader(ifs)
            rules = []
            for row in reader:
                rule = dict()
                if "regex" not in row:
                    continue
                for k, v in row.items():
                    if v == "":
                        continue
                    if k == "tags":
                        v = "".join(v.split()).split(",")
                    elif k == "target_regex_group":
                        v = int(v)
                    rule[k] = v
                rules.append(rule)

            self.load(rules)

    def search(self, input_str: str, return_match_obj=False):
        if self.mode is SEARCH_MODE.SEPARATED:
            result = []
            for i, rule in enumerate(self.rules):
                result.extend(self.__search_by_a_rule(rule, input_str, return_match_obj))

            return result

        elif self.mode is SEARCH_MODE.MULTI_THREAD:
            results = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for i, rule in enumerate(self.rules):
                    futures.append(executor.submit(self.__search_by_a_rule, rule, input_str, return_match_obj))

                for future in futures:
                    results.extend(future.result())

            return results

        elif self.mode is SEARCH_MODE.UNIFIED:
            if return_match_obj:
                print("WARN: return_match_obj=True is NOT supported in SEARCH_MODE.UNIFIED (ignored)")

            result = []
            for match in self.unified_regex.finditer(input_str):
                for group_num, rule_num in self.group_num_to_rule_num.items():
                    group_raw = match.group(group_num)
                    if group_raw is None or group_raw == "":
                        continue

                    item = self.__make_result_item(self.rules[rule_num], match)
                    if item is not None:
                        result.append(item)

            return result

        else:
            raise ValueError(f"Unknown Mode: {self.mode}")

    def __search_by_a_rule(self, rule, input_str, return_match_obj):
        result = []
        for match in rule["__regex_compiled"].finditer(input_str):
            item = self.__make_result_item(rule, match, return_match_obj)
            if item is not None:
                result.append(item)
        return result

    def __make_result_item(self, rule, match, return_match_obj=False):
        offset = rule.get("__group_offset") or 0
        target_regex_group = rule.get("target_regex_group") or 0
        target_regex_group += offset

        raw = match.group(target_regex_group)
        start, end = match.span(target_regex_group)
        item = {"raw": raw, "start": start, "end": end}

        representation = rule.get("repr")

        # Parse representation if '{}' exists in it
        if representation is not None:
            if "{" in representation and "}" in representation:
                group = match.group  # noqa: F841
                custom_function = self.custom_functions  # noqa: F841

                representation = re.sub("(group\\([0-9]+)(\\))", repl="\\1+offset\\2", string=representation)
                # if offset != 0:
                #     representation = re.sub("(group\\([0-9]+)(\\))", repl=f"\\1+{offset}\\2", string=representation)

                lambda_str = 'lambda group, custom_function, offset: f"' + representation + '"'
                if lambda_str not in self.eval_function_hash:
                    self.eval_function_hash[lambda_str] = eval(lambda_str)

                representation = self.eval_function_hash[lambda_str](group, custom_function, offset)
                # representation = eval('f"' + representation + '"')

            item["repr"] = representation

        rule_id = rule.get("id")
        if rule_id is not None:
            item["rule_id"] = rule_id

        tags = rule.get("tags")
        if tags is not None:
            item["tags"] = tags

        if return_match_obj:
            if self.mode is SEARCH_MODE.UNIFIED:
                print("WARN: return_match_obj=True is NOT supported in SEARCH_MODE.UNIFIED (ignored)")
            else:
                item["match"] = match

        if rule.get("validation") is not None:
            if rule["validation"].startswith("lambda "):
                lambda_func = eval(rule["validation"])
                valid = lambda_func(item)
            elif rule["validation"] not in self.custom_functions:
                raise ValueError(f"No such custom function: {rule['validation']}")
            else:
                valid = self.custom_functions[rule["validation"]](item)

            if valid is None or valid is False:
                return None

        return item
