import concurrent.futures
import json
import re
from enum import Enum

SEARCH_MODE = Enum("SEARCH_MODE", "SEPARATED UNIFIED MULTI_THREAD")


class Rexearch:
    def __init__(self, mode=SEARCH_MODE.SEPARATED, auto_rule_id=False):
        self.mode = mode
        self.auto_rule_id = auto_rule_id
        self.rules = None

        self.unified_regex = None
        self.group_num_to_rule_num = None

        self.custom_functions = dict()

    def load(self, rules):
        self.rules = rules
        # Compile rules in advance
        if self.mode is SEARCH_MODE.SEPARATED or self.mode is SEARCH_MODE.MULTI_THREAD:
            for i, rule in enumerate(self.rules):
                if "id" not in rule and self.auto_rule_id:
                    rule["id"] = f"UNNAMED_RULE_{i}"
                rule["regex_compiled"] = re.compile(rule["regex"])
        if self.mode is SEARCH_MODE.UNIFIED:
            offset = 0
            self.group_num_to_rule_num = dict()
            unified_regex_str = ""
            for i, rule in enumerate(self.rules):
                if "id" not in rule and self.auto_rule_id:
                    rule["id"] = f"UNNAMED_RULE_{i}"
                unified_regex_str = "|".join([unified_regex_str, "(" + rule["regex"] + ")"])
                rule["group_offset"] = offset + 1
                self.group_num_to_rule_num[offset + 1] = i
                offset += re.compile(rule["regex"]).groups + 1
            self.unified_regex = re.compile(unified_regex_str)

    def load_json_file(self, filepath, encoding="utf-8"):
        with open(filepath, mode="rt", encoding=encoding) as ifs:
            self.load(json.load(ifs))

    def search(self, input_str: str, return_match_obj=False):
        if self.mode is SEARCH_MODE.SEPARATED:
            result = []
            for i, rule in enumerate(self.rules):
                result.extend(self.__search(rule, input_str, return_match_obj))

            return result

        elif self.mode is SEARCH_MODE.UNIFIED:
            result = []
            for match in self.unified_regex.finditer(input_str):
                for group_num, rule_num in self.group_num_to_rule_num.items():
                    whole_raw = match.group(group_num)
                    if whole_raw is None or whole_raw == "":
                        continue

                    rule = self.rules[rule_num]
                    offset = rule["group_offset"]
                    target_regex_group = rule.get("target_regex_group") or 0
                    target_regex_group += offset
                    raw = match.group(target_regex_group)
                    representation = rule.get("repr")
                    categories = rule.get("categories")
                    rule_id = rule.get("id")

                    # Parse representation if '{}' exists in it
                    representation_out = representation
                    if representation is not None and "{" in representation and "}" in representation:
                        group = match.group  # noqa: F841
                        custom_function = self.custom_functions  # noqa: F841
                        representation = re.sub("(group\\([0-9]+)(\\))", repl=f"\\1+{offset}\\2", string=representation)
                        representation_out = eval('f"' + representation + '"')

                    start, end = match.span(target_regex_group)
                    item = {"raw": raw, "start": start, "end": end}

                    # Additional metadata
                    if representation_out is not None:
                        item["repr"] = representation_out
                    if rule_id is not None:
                        item["rule_id"] = rule_id
                    if categories is not None:
                        item["categories"] = categories

                    if return_match_obj:
                        print("WARN: return_match_obj is NOT supported in Unified mode (ignored)")

                    result.append(item)

            return result

        elif self.mode is SEARCH_MODE.MULTI_THREAD:
            results = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for i, rule in enumerate(self.rules):
                    futures.append(executor.submit(self.__search, rule, input_str, return_match_obj))

                for future in futures:
                    results.extend(future.result())

            return results

        else:
            raise ValueError(f"Unknown Mode: {self.mode}")

    def __search(self, rule, input_str, return_match_obj):
        result = []
        target_regex_group = rule.get("target_regex_group") or 0
        representation = rule.get("repr")
        categories = rule.get("categories")
        rule_id = rule.get("id")

        for match in rule["regex_compiled"].finditer(input_str):
            raw = match.group(target_regex_group)

            # Parse representation if '{}' exists in it
            representation_out = representation
            if representation is not None and "{" in representation and "}" in representation:
                group = match.group  # noqa: F841
                custom_function = self.custom_functions  # noqa: F841
                representation_out = eval('f"' + representation + '"')

            start, end = match.span(target_regex_group)
            item = {"raw": raw, "start": start, "end": end}

            # Additional metadata
            if representation_out is not None:
                item["repr"] = representation_out
            if rule_id is not None:
                item["rule_id"] = rule_id
            if categories is not None:
                item["categories"] = categories

            if return_match_obj:
                item["match"] = match

            result.append(item)

        return result
