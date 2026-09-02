import json

src_list = list()
results_list = list()
new_list = list()
# done_list = list()

with open("missing_data_lastchance.jsonl", "r") as f:
    for line in [x.strip() for x in f]:
        src_list.append(json.loads(line))

with open("results.jsonl", "r") as f:
    for line in [x.strip() for x in f]:
        results_list.append(json.loads(line))


done_list = [x for x in results_list if x is not None and x.get("count", 0 ) > 0]

for item in src_list:
    if item["result"] not in [x["result"] for x in done_list]:
        print(item)
    
    

# for item in [x for x in results_list if x is not None and x.get("count", 0 ) > 0]:
    

