import warnings

from jira.client import JIRA, Issue, translate_resource_args, ResultList
from jira.resources import Board, GreenHopperResource


class JIRA(JIRA):
    def issues_by_board(self, board_id, jql=None):
        print(jql)
        params = {}
        if jql:
            params['jql'] = jql

        # todo remove replace
        r_json = self._get_json('board/%s/issue/' % board_id,
                                params=params,
                                base=self.AGILE_BASE_URL.replace('{agile_rest_path}', 'agile'))
        return [Issue(self._options, self._session, raw_issues_json) for raw_issues_json in r_json['issues']]

    @translate_resource_args
    def boards(self, startAt=0, maxResults=50, type=None, name=None, boardKeyOrId=None):
        """Get a list of board resources.

        :param startAt: The starting index of the returned boards. Base index: 0.
        :param maxResults: The maximum number of boards to return per page. Default: 50
        :param type: Filters results to boards of the specified type. Valid values: scrum, kanban.
        :param name: Filters results to boards that match or partially match the specified name.
        :rtype: ResultList[Board]

        When old GreenHopper private API is used, paging is not enabled and all parameters are ignored.
        """
        params = {}
        if type:
            params['type'] = type
        if name:
            params['name'] = name
        if boardKeyOrId:
            params['projectKeyOrId'] = boardKeyOrId

        if self._options['agile_rest_path'] == GreenHopperResource.GREENHOPPER_REST_PATH:
            # Old, private API did not support pagination, all records were present in response,
            #   and no parameters were supported.
            if startAt or maxResults or params:
                warnings.warn('Old private GreenHopper API is used, all parameters will be ignored.', Warning)

            r_json = self._get_json('rapidviews/list', base=self.AGILE_BASE_URL)
            boards = [Board(self._options, self._session, raw_boards_json) for raw_boards_json in r_json['views']]
            return ResultList(boards, 0, len(boards), len(boards), True)
        else:
            return self._fetch_pages(Board, 'values', 'board', startAt, maxResults, params, base=self.AGILE_BASE_URL)
