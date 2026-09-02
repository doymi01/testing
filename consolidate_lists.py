import json

src_list = list()
results_list = list()
new_list = list()
done_set = set()

# Helper function to turn a dict into a hashable tuple
def make_hashable(d):
    return tuple(sorted(d.items()))

# 1. Read source data
with open("missing_data_lastchance.jsonl", "r") as f:
    for line in f:
        stripped = line.strip()
        if stripped:
            src_list.append(json.loads(stripped))

# 2. Build the set using standardized JSON strings
with open("results.jsonl", "r") as f:
    for line in f:
        stripped = line.strip()
        if stripped:
            x = json.loads(stripped)
            if x is not None and x.get("count", 0) > 0:
                # sort_keys=True guarantees identical dicts/lists stringify exactly the same
                hashable_str = json.dumps(x["result"], sort_keys=True)
                done_set.add(hashable_str)

# 3. Blazing fast lookup loop
for item in src_list:
    item_str = json.dumps(item["result"], sort_keys=True)
    if item_str not in done_set:
        new_list.append(item)

# Optional: Print how many items were found to verify it worked
with open("new_missing_data.jsonl", "w") as f:
    for item in new_list:
        f.write(json.dumps(item) + "\n")
print(f"Filtered down to {len(new_list)} new items.")
# for item in [x for x in results_list if x is not None and x.get("count", 0 ) > 0]:
    

