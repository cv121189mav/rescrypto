from googleapiclient.errors import HttpError
from own_jira.client import JIRA
import pygsheets
import datetime
import maya


class ConnectJiraData:
    def __init__(self):
        # connect to own_jira api
        self.options = {'server': 'http://jira.rescrypto.pro/'}
        self.jira_connect = JIRA(self.options, basic_auth=('oleksandr.mateik', 'Cvdovdmav89'))

        # connect to google sheets
        self.client = pygsheets.authorize('/home/sanya/PycharmProjects/some_task/credentials.json')
        self.sheet = self.client.open_by_key('1a5eJDqckUPqrwI0ILMKsyuRInstHArjNo2nqlljV4JE')

        # self.worksheet = self.sheet.worksheet(property='title', value='Лист1')
        self.record_place = None
        self.priority = None
        self.issue_description = None
        self.name_of_project = None
        self.add_tab_sheet = None
        self.count_missing_rows = 2
        self.issues_type = ['task', 'story', 'epic', 'bug']


    def create_data_sheets(self):
        while True:
            try:
                project_name_or_id = input('input id or key of project  ')
                jira_project = self.jira_connect.project(project_name_or_id)

                # get boards list by project and print it
                boards = self.jira_connect.boards()
                for i in boards:
                    print('Board: name - {}, id - {}'.format(i.name, i.id))

                # checking if board in project and choose board id and record issues to spreadsheet
                while True:
                    board_id = int(input('Input id board '))
                    matches = list(filter(lambda board: board.id == board_id, boards))
                    if matches:
                        break

                jql = ''

                def add_to_jql(jql_str, new_str, type_concat='and'):
                    return ' '.join([jql_str, type_concat, new_str]) if jql_str else new_str

                # filter issues by type --> or view all issues
                while True:
                    choose_type = input(
                        'choose the type from %s or press "rec" to record all issues ' % self.issues_type)
                    if choose_type.lower() == "rec":
                        break
                    elif choose_type in self.issues_type:
                        jql = add_to_jql(jql, 'issuetype=%s' % choose_type)
                        break
                    else:
                        print('choose thr correct type')

                while True:
                    choose_period = input('Do you want to record for the particular period?  press Y/N  ')
                    try:
                        if choose_period.lower() == 'n':
                            break
                        elif choose_period.lower() == 'y':
                            start_from = input('Enter from date 2019-07-01 - ')
                            end_to = input('Enter to date 2019-07-04 - ')
                            # todo check date format
                            jql = add_to_jql(jql, 'created>=%s' % start_from)
                            jql = add_to_jql(jql, 'created<=%s' % end_to)
                            break
                        else:
                            print("please, press Y or N")
                    except Exception as error:
                        print(error)

                issues = self.jira_connect.issues_by_board(board_id, jql=jql)

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
                        'name': 'assignee',
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
                    self.record_place.value = str(value['name'])

                # set data for each issue
                for count, issue in enumerate(issues):
                    for column_index, field in enumerate(fields):
                        self.record_place = pygsheets.Cell(pos=(self.count_missing_rows + count, column_index + 1),
                                                           worksheet=self.add_tab_sheet)
                        value = ''
                        if 'assignee' in field['name']:
                            value = issue.fields.assignee.name
                        elif 'subtasks' in field['name']:
                            value = len(issue.fields.subtasks)
                        elif 'labels' in field['name']:
                            value = ', '.join(label for label in issue.fields.labels)
                        else:
                            value = getattr(issue.fields, field['name'], field['default'])
                        self.record_place.value = str(value)

            except HttpError:
                print("Probably you have already create tab of spreadsheet")

            except Exception:
                print("You've entered incorrect id or name of project")


runner = ConnectJiraData()
runner.create_data_sheets()
