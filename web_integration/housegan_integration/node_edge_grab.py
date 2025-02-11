edges=[
{"from": 0, "to": 3, id: '3275050c-e94a-4898-8aa5-58020d9c544d'},
{"from": 0, "to": 1, id: '337387d7-3637-4787-af6c-a6c8f8e01dd2'},
{"from": 3, "to": 1, id: '882081db-565e-4c0a-9747-2c05b7a1c5a0'},
{"from": 3, "to": 2, id: '9083819d-3798-42d8-b16d-aeefbd62beae'},
{"from": 7, "to": 2, id: '2538b228-66c7-4994-b14e-1447e7ce4fe9'},
{"from": 4, "to": 2, id: 'ea03080d-0a46-41ec-bdf0-777d153477cf'}
]

edgeList = []

# def edgefromroom(edge,node):

nodes=[0,1,2,3,4,5,16,16,16,16,16,16,14]

node=6

for edge in range(node):
    for j in range(edge+1,node):
        to_app = -1
        for e in edges:
            if (e["from"]==edge and e["to"]==j) or (e["to"]==edge and e["from"]==j) :
                to_app = 1
                break
        edgeList.append([edge,to_app,j])

print(edgeList)



