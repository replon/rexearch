import json
import re
from enum import Enum

SEARCH_MODE = Enum("SEARCH_MODE", "SEPARATED UNIFIED MULTI_THREAD")


class Rexearch:
    def __init__(self, mode=SEARCH_MODE.SEPARATED, auto_rule_id=False):
        self.mode = mode
        self.auto_rule_id = auto_rule_id
        self.rules = None

    def load(self, rules):
        self.rules = rules
        # Compile rules in advance
        if self.mode is SEARCH_MODE.SEPARATED:
            for i, rule in enumerate(self.rules):
                if "id" not in rule and self.auto_rule_id:
                    rule["id"] = f"UNNAMED_RULE_{i}"
                rule["regex_compiled"] = re.compile(rule["regex"])

    def load_json_file(self, filepath, encoding="utf-8"):
        with open(filepath, mode="rt", encoding=encoding) as ifs:
            self.load(json.load(ifs))

    def search(self, input_str: str, return_match_obj=False):
        if self.mode is SEARCH_MODE.SEPARATED:
            result = []
            for i, rule in enumerate(self.rules):
                target_regex_group = rule.get("target_regex_group") or 0
                representation = rule.get("repr")
                categories = rule.get("categories")
                rule_id = rule.get("id")

                for match in rule["regex_compiled"].finditer(input_str):
                    raw = match.group(target_regex_group)

                    # Parse representation if '{}' exists in it
                    if representation is not None and "{" in representation and "}" in representation:
                        group = match.group  # noqa: F841
                        representation = eval('f"' + representation + '"')

                    start, end = match.span(target_regex_group)
                    item = {"raw": raw, "start": start, "end": end}

                    # Additional metadata
                    if representation is not None:
                        item["repr"] = representation
                    if rule_id is not None:
                        item["rule_id"] = rule_id
                    if categories is not None:
                        item["categories"] = categories

                    if return_match_obj:
                        item["match"] = match

                    result.append(item)

            return result

        elif self.mode is SEARCH_MODE.UNIFIED:
            raise NotImplementedError(f"Unsupported Mode: {self.mode}")

        elif self.mode is SEARCH_MODE.MULTI_THREAD:
            raise NotImplementedError(f"Unsupported Mode: {self.mode}")

        else:
            raise ValueError(f"Unknown Mode: {self.mode}")
