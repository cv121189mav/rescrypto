from own_jira.client import JIRA
import pygsheets
import datetime


class Jira:
    def __init__(self, mediator, login, password, server='http://jira.rescrypto.pro/'):
        self.mediator = mediator

        # connect to own_jira api
        self.options = {'server': server}
        self.connection = JIRA(self.options, basic_auth=(login, password))

        # variables for work with data
        self.jql = ''
        self.issues_type = ['task', 'story', 'epic', 'bug']
        self.board_id = None


class Spreadsheet:
    def __init__(self, mediator):
        self.mediator = mediator

        # connect to google sheets
        self.client = pygsheets.authorize('/home/sanya/PycharmProjects/some_task/credentials.json')
        self.sheet = self.client.open_by_key('1a5eJDqckUPqrwI0ILMKsyuRInstHArjNo2nqlljV4JE')

        # headers for spreadsheet
        self.fields = [
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


class Mediator:
    def __init__(self):
        self._jira = Jira(self, 'oleksandr.mateik', 'Cvdovdmav89')
        self._spreadsheets_ = Spreadsheet(self)

        # variables for recording
        self.count_missing_rows = 2
        self.project = self.get_project()
        self.validate_boards = self.boards_validate()
        self.type_date_filter = self.type_date_filter()
        self.record = self.record()

    # getting project
    def get_project(self):
        try:
            project_name_or_id = input('input id or key of project  ')
            return self._jira.connection.project(project_name_or_id)
        except Exception as error:
            print(error.args.__getitem__(1))
            return self.get_project()

    # getting and validate board
    def boards_validate(self):
        for i in self._jira.connection.boards():
            print('Board: name - {}, id - {}'.format(i.name, i.id))
        while True:
            self._jira.board_id = int(input('Input id board '))
            matches = list(filter(lambda board: board.id == self._jira.board_id, self._jira.connection.boards()))
            if matches:
                return matches

    @staticmethod
    def add_to_jql(jql_str, new_str, type_concat='and'):
        return ' '.join([jql_str, type_concat, new_str]) if jql_str else new_str

    # filter issues by type or get all
    # filter issues by date or get all
    def type_date_filter(self):
        while True:
            choose_type = input(
                'choose the type from %s or press "rec" to record all issues ' % self._jira.issues_type)
            if choose_type.lower() == "rec":
                break
            elif choose_type in self._jira.issues_type:
                self._jira.jql = self.add_to_jql(self._jira.jql, 'issuetype=%s' % choose_type)
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
                    self._jira.jql = self.add_to_jql(self._jira.jql, 'created>=%s' % start_from)
                    self._jira.jql = self.add_to_jql(self._jira.jql, 'created<=%s' % end_to)
                    break
                else:
                    print("please, press Y or N")
            except Exception as error:
                print(error)

        # list of issues
        self.issues = self._jira.connection.issues_by_board(self._jira.board_id, jql=self._jira.jql)

        # create tab's name
        self.add_tab_sheet = self._spreadsheets_.sheet.add_worksheet(
            '; '.join([self.project.name, self.validate_boards[0].name, str(datetime.datetime.now())])
        )

    def record(self):
        # record headers for each column
        for column_index, value in enumerate(self._spreadsheets_.fields):
            self.record_place = pygsheets.Cell(pos=(1, 1 + column_index),
                                               worksheet=self.add_tab_sheet)
            self.record_place.value = str(value['name'])

        # record data for each issue
        for count, issue in enumerate(self.issues):
            for column_index, field in enumerate(self._spreadsheets_.fields):
                self.record_place = pygsheets.Cell(
                    pos=(self.count_missing_rows + count, column_index + 1), worksheet=self.add_tab_sheet)
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


mediator_run = Mediator()
