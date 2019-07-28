import jira.client
from jira.client import JIRA
import re

options = {'server': 'http://jira.rescrypto.pro/'}
connect = JIRA(options, basic_auth=('oleksandr.mateik', 'Cvdovdmav89'))

print(connect.projects())
# print(connect.project(10200))
issues_in_proj = connect.search_issues('issuetype=Task', maxResults=None)
# print(issues_in_proj)

issue = connect.issue('BI-45')

summary = issue.fields.summary
print(summary)

comments_a = issue.fields.comment.comments
print(comments_a)
comment = connect.comment('BI-45', '10345')
#
capacity = issue.raw['fields']['comment']
print(capacity)
comments = []
for i in capacity['comments']:
    print(i['body'])




# connect.assign_issue(issue, )

# for issue in connect.search_issues('reporter = currentUser() order by created desc', maxResults=3):
#     print('{}: {} -- {}'.format(issue.key, issue.fields.summary, issue.fields.description))

# issue.update(
#     summary="Test done", description='Changed the summary to be different.')

# new_issue = connect.create_issue(
# project='10200', summary='Test',description='researching working with jira api', issuetype={'name': 'Task'}
# )

#OR
# issue_dict = {
#     'project': {'id': 123},
#     'summary': 'New issue from jira-python',
#     'description': 'Look into this one',
#     'issuetype': {'name': 'Bug'},
# }
# new_issue = jira.create_issue(fields=issue_dict)

# connect.add_comment(issue, 'Done')
