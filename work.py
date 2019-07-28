import pygsheets
from jira.client import JIRA

options = {'server': 'http://jira.rescrypto.pro/'}
connect = JIRA(options, basic_auth=('oleksandr.mateik', 'Cvdovdmav89'))

# issue_dict = {
#     'project': {'id': 10200},
#     'summary': 'New issue from jira-python',
#     'description': 'Look into this one',
#     'issuetype': {'name': 'Bug'},
# }
#
# new_issue = connect.create_issue(fields=issue_dict)

issue = connect.issue('BI-45')
print(issue)

summary = issue.fields.summary
print(summary)

client = pygsheets.authorize('/home/sanya/PycharmProjects/some_task/credentials.json')
# sheet = client.sheet.get('1a5eJDqckUPqrwI0ILMKsyuRInstHArjNo2nqlljV4JE')
# print(client.spreadsheet_titles())
sheet = client.open_by_key('1a5eJDqckUPqrwI0ILMKsyuRInstHArjNo2nqlljV4JE')
worksheet1 = sheet.worksheet(property='title', value='Лист1')

cell1 = pygsheets.Cell(pos=(1, 1), worksheet=worksheet1)
cell2 = pygsheets.Cell(pos=(1, 2), worksheet=worksheet1)
cell1.value = str(issue.raw['fields']['summary'])
cell2.value = str(issue.raw['fields']['description'])



