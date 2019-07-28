import pygsheets

client = pygsheets.authorize('/home/sanya/PycharmProjects/some_task/credentials.json')
# sheet = client.sheet.get('1a5eJDqckUPqrwI0ILMKsyuRInstHArjNo2nqlljV4JE')
# print(client.spreadsheet_titles())
sheet = client.open_by_key('1a5eJDqckUPqrwI0ILMKsyuRInstHArjNo2nqlljV4JE')
worksheet1 = sheet.worksheet(property='title', value='Лист1')
print(worksheet1.__dict__)

cell = pygsheets.Cell(pos=(3, 5), worksheet=worksheet1)
print(cell)
print(cell.value)
cell.value = 'alec'
print(cell.value)



