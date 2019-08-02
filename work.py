import pygsheets
import datetime

from lib.own_jira.client import JIRA
from settings import environment


class Jira:
    def __init__(self, login, password, server='http://jira.rescrypto.pro/'):
        # connect to own_jira api
        self.options = {'server': server}
        self.connection = JIRA(self.options, basic_auth=(login, password))

        # variables for work with data
        self.jql = ''
        self.issues_type = ['task', 'story', 'epic', 'bug']
        self.board_id = None

    def add_to_jql(self, jql_str, new_str, type_concat='and'):
        self.jql = ' '.join([jql_str, type_concat, new_str]) if jql_str else new_str

    def get_boards(self):
        return self.connection.boards()
    
    def issues_by_board(self, board_id, jql=None):
        if jql is None:
            jql = self.jql
        return self.connection.issues_by_board(board_id, jql=jql)


class Spreadsheet:
    def __init__(self, spreadsheet_log):

        # connect to google sheets
        self.client = pygsheets.authorize('./credentials.json')
        self.sheet = self.client.open_by_key(spreadsheet_log)

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
        self.last_worksheet = None

    def create_worksheet(self, name=None):
        if name is None:
            name = str(datetime.datetime.now())
        self.last_worksheet = self.sheet.add_worksheet(name)
        return self.last_worksheet

    def record(self, data=None, worksheet=None, start_row=1):
        if data is None:
            data = []

        if worksheet is None:
            worksheet = self.last_worksheet or self.create_worksheet()

        # record headers for each column
        for column_index, value in enumerate(self.fields):
            record_place = pygsheets.Cell(pos=(start_row, 1 + column_index), worksheet=worksheet)
            record_place.value = str(value['name'])

        # record data for each issue
        start_row += 1
        for count, issue in enumerate(data):
            for column_index, field in enumerate(self.fields):
                record_place = pygsheets.Cell(pos=(start_row + count, column_index + 1), worksheet=worksheet)
                value = ''
                if 'assignee' in field['name']:
                    value = issue.fields.assignee.name
                elif 'subtasks' in field['name']:
                    value = len(issue.fields.subtasks)
                elif 'labels' in field['name']:
                    value = ', '.join(label for label in issue.fields.labels)
                else:
                    value = getattr(issue.fields, field['name'], field['default'])
                record_place.value = str(value)


class Recorder:
    def __init__(self, place_source, place_record, count=5):
        self._place_source = place_source
        self._place_record = place_record

        self.count = count

        self.project = self.get_project()
        self.board = self.get_board()

        self.filters()
        self.data = self.get_data()

        self.record()

    # getting project
    def get_project(self, count=0):
        try:
            project_name_or_id = input('input id or key of project  ')
            return self._place_source.connection.project(project_name_or_id)
        except Exception as error:
            print(error.args.__getitem__(1))
            if count < self.count:
                return self.get_project(count + 1)
            else:
                print('limit')

    # getting and validate board
    def get_board(self, count=0):
        boards = self._place_source.get_boards()
        for i in boards:
            print('Board: name - {}, id - {}'.format(i.name, i.id))
        while count < self.count:
            board_id = int(input('Input id board '))
            matches = list(filter(lambda board: board.id == board_id, boards))
            if matches:
                return matches[0]
            count += 1

        print('limit')

    def filters(self):
        self.type_filter()
        self.date_filter()

    def get_data(self):
        return self._place_source.issues_by_board(self.board.id)

    def type_filter(self):
        while True:
            choose_type = input(
                'choose the type from %s or press "all" to record all issues ' % self._place_source.issues_type).lower()
            if choose_type == "all":
                break
            elif choose_type in self._place_source.issues_type:
                self._place_source.add_to_jql(self._place_source.jql, 'issuetype=%s' % choose_type)
                break
            else:
                print('choose thr correct type')

    def date_filter(self):
        while True:
            choose_period = input('Do you want to record for the particular period?  press Y/N  ').lower()
            try:
                if choose_period == 'n':
                    break
                elif choose_period == 'y':
                    start_from = input('Enter from date 2019-07-01 - ')
                    end_to = input('Enter to date 2019-07-04 - ')
                    # todo check date format
                    self._place_source.add_to_jql(self._place_source.jql, 'created>=%s' % start_from)
                    self._place_source.add_to_jql(self._place_source.jql, 'created<=%s' % end_to)
                    break
                else:
                    print("please, press Y or N")
            except Exception as error:
                print(error)

    def record(self):
        worksheet = self._place_record.create_worksheet(
            '; '.join([self.project.name, self.board.name, str(datetime.datetime.now())]))
        self._place_record.record(self.data, worksheet)


jira = Jira(environment.JIRA_LOGIN, environment.JIRA_PASSWORD)
spreadsheet = Spreadsheet(environment.SPREADSHEET_AUTH)
mediator_run = Recorder(jira, spreadsheet)
