import csv
import json

import rexearch


def write_rule_as_csv(rules, filepath):
    with open(filepath, mode="wt", encoding="utf-8") as ofs:
        fieldnames = ["id", "regex", "target_regex_group", "repr", "tags", "validation", "description"]
        writer = csv.DictWriter(ofs, fieldnames, extrasaction="ignore")
        writer.writeheader()
        for rule in rules:
            if "tags" in rule:
                rule["tags"] = ",".join(rule["tags"])
            writer.writerow(rule)


def write_rule_as_json(rules, filepath, extra_meta=None):
    filtered_rules = []
    for rule in rules:
        filtered_rules.append({k: v for k, v in rule.items() if not k.startswith("__")})

    with open(filepath, mode="wt", encoding="utf-8") as ofs:
        obj = dict()
        if type(extra_meta) is dict:
            obj.update(extra_meta)
        obj.update({"rexearch_version": rexearch.__version__, "rules": filtered_rules})
        json.dump(obj, ofs, ensure_ascii=False, indent=4, default=str)
