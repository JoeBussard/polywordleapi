#!/bin/python
# copyright 2022 joe bussard

import json

common_words = []
all_words = []

common_dict = {}
all_dict = {}

with open('all-fives') as f:
  common_data = f.read()
  for x in common_data.split():
    common_words += [x]

for i in range(len(common_words)):
  common_dict[i] = common_words[i]

for i in range((len(common_dict)-10), len(common_dict)):
  print(i, common_dict[i])

if '3070' in common_dict:
  print(common_dict[3070])

print(common_dict)
print(json.dumps(common_dict))

json_string = json.dumps(common_dict)

with open('all_words.json', 'w') as outfile:
  json.dump(common_dict, outfile)

with open('json_data.json') as infile:
  data = json.load(infile)
  print(data['1'])


