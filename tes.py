from googleapiclient.errors import HttpError
from own_jira.client import JIRA
import pygsheets
import datetime
import maya


class GetJiraData:
    def __init__(self):
        # connect to own_jira api
        self.options = {'server': 'http://jira.rescrypto.pro/'}
        self.jira_connect = JIRA(self.options, basic_auth=('oleksandr.mateik', 'Cvdovdmav89'))

        # connect to google sheets
        self.client = pygsheets.authorize('/home/sanya/PycharmProjects/some_task/credentials.json')
        self.sheet = self.client.open_by_key('1a5eJDqckUPqrwI0ILMKsyuRInstHArjNo2nqlljV4JE')

        # self.worksheet = self.sheet.worksheet(property='title', value='Лист1')
        self.record_place = None
        self.type_of_issue = None
        self.priority = None
        self.issue_description = None
        self.name_of_project = None
        self.add_tab_sheet = None
        self.count_missing_rows = 2

    def create_data_sheets(self):
        while True:
            try:
                project_name_or_id = input('input id or key of project  ')
                jira_project = self.jira_connect.project(project_name_or_id)

                # get boards list by project and print it
                boards = self.jira_connect.boards()
                for i in boards:
                    print('Board: name - {}, id - {}'.format(i.name, i.id))

                # checking if board in project
                while True:
                    board_id = int(input('Input id board '))
                    matches = list(filter(lambda board: board.id == board_id, boards))
                    if matches:
                        break

                # choose board id and record issues to spreadsheet
                issues = self.jira_connect.issues_by_board(board_id)

                # filter issues by type --> or view all issues
                while True:
                    choose_type = input('choose the type or press "rec" to record all issues ')
                    if choose_type == "rec":
                        break
                    else:
                        issues = list(
                            filter(lambda type_issue: type_issue.fields.issuetype.name == choose_type, issues))
                        break

                while True:
                    choose_period = input('Do you want to record for the particular period?  press Y/N  ').lower()
                    if choose_period == 'n' and not 'y':
                        break
                    else:
                        start_from = input('Enter from date 2019-07-01 - ')
                        end_to = input('Enter to date 2019-07-04 - ')
                        issues = list(
                            filter(lambda date_issue: start_from <= maya.parse(
                                date_issue.fields.created).date.isoformat() <= end_to, issues))
                    break

                # record name of project
                self.add_tab_sheet = self.sheet.add_worksheet(
                    '; '.join([jira_project.name, matches[0].name, str(datetime.datetime.now())])
                )

                # headers for spreadsheet
                fields = [
                    {
                        'name': 'summary',
                        'default': 'noname',
                    },
                    {
                        'name': 'priority',
                        'default': 'noname',
                    },
                    {
                        'name': 'issuetype',
                        'default': 'noname',
                    },
                    {
                        'name': 'description',
                        'default': 'noname',
                    },
                    {
                        'name': 'assignee.name',
                        'default': 'noname',
                    },
                    {
                        'name': 'timespent',
                        'default': 'noname',
                    },
                    {
                        'name': 'aggregatetimespent',
                        'default': 'noname',
                    },
                    {
                        'name': 'resolution',
                        'default': 'noname',
                    },
                    {
                        'name': 'resolutiondate',
                        'default': 'noname',
                    },
                    {
                        'name': 'labels',
                        'default': 'noname',
                    },
                    {
                        'name': 'timeestimate',
                        'default': 'noname',
                    },
                    {
                        'name': 'aggregatetimeoriginalestimate',
                        'default': 'noname',
                    },
                    {
                        'name': 'timeoriginalestimate',
                        'default': 'noname',
                    },
                    {
                        'name': 'status',
                        'default': 'noname',
                    },
                    {
                        'name': 'subtasks',
                        'default': 'noname',
                    },

                ]

                # set headers for each column
                for column_index, value in enumerate(fields):
                    self.record_place = pygsheets.Cell(pos=(1, 1 + column_index),
                                                       worksheet=self.add_tab_sheet)
                    if '.' in value['name']:
                        self.record_place.value = str(value['name'].split('.')[0])
                    else:
                        self.record_place.value = str(value['name'])

                # set data for each issue
                for count, issue in enumerate(issues):
                    for column_index, field in enumerate(fields):
                        self.record_place = pygsheets.Cell(pos=(self.count_missing_rows + count, column_index + 1),
                                                           worksheet=self.add_tab_sheet)
                        value = ''
                        if '.' in field['name']:
                            if 'assignee' in field['name']:
                                value = issue.fields.assignee.name
                        elif 'subtasks' in field['name']:
                            value = len(issue.fields.subtasks)
                        elif 'labels' in field['name']:
                            value = ', '.join(list([label for label in issue.fields.labels]))
                        else:
                            value = getattr(issue.fields, field['name'], field['default'])
                        self.record_place.value = str(value)

            except HttpError:
                print("Probably you have already create tab of spreadsheet")

            except Exception:
                print("You've entered incorrect id or name of project")


runner = GetJiraData()
runner.create_data_sheets()
