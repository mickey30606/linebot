import json

with open('./flex_message.json') as f:
    data = json.load(f)

for i in range(0, 3):
    print(i)
    print(data['body']['contents'][i]['contents'][0]['text'])

start = 0
end = 0
result = "12, 22"
result = result.split(',')
start = int(result[0])
end = int(result[1])
print(start)
print(end)
