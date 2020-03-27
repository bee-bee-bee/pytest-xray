import json
import logging
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_test_keys = {}


# def _get_xray_marker(item):
#     return item.get_closest_marker(XRAY_MARKER_NAME)


def associate_marker_metadata_for(item, test_key):
    # marker = _get_xray_marker(item)
    # if not marker:
    #     return
    #
    # test_key = marker.kwargs["test_key"]
    _test_keys[item.nodeid] = test_key


def get_test_key_for(item):
    nodeid = item.nodeid.encode("unicode_escape")
    results = _test_keys.get(nodeid.decode())
    if results:
        return results
    return None


class PublishXrayResults:
    def __init__(self, base_url, base64_code, testPlanKey, testExecKey, revision, testEnvironment, version):
        self.base_url = base_url
        self.base64_code = base64_code
        self.testPlanKey = testPlanKey
        self.testExecKey = testExecKey
        self.revision = revision
        self.testEnvironment = testEnvironment
        self.version = version

    def __call__(self, *report_objs):
        for a_dict in self._test_execution_summaries(*report_objs):
            self._post(a_dict)

    def _post(self, a_dict):
        payload = json.dumps(a_dict)
        logger.debug(f"Payload => {payload}")
        url = self.results_url()
        headers = {"Content-Type": "application/json", "Authorization": f"Basic {self.base64_code}"}
        # with open('/Users/hongzhen.bi/data_report/data.json', encoding='utf-8') as f:
        #     res = f.read()
        #     data = json.loads(res)
        resp = requests.post(url, data=payload, headers=headers)
        logger.info(f"Payload => {payload}")
        if not resp.ok:
            logger.error("There was an error from Xray API!")
            logger.error(resp.text)
        else:
            logger.info("Post test execution success!")

    def results_url(self):
        return f"{self.base_url}/rest/raven/1.0/import/execution"

    def _test_execution_summaries(self, *report_objs):
        summaries = {}

        for each in report_objs:
            if not self.testExecKey in summaries:
                summaries[self.testExecKey] = self._create_header(each.start_ts.isoformat(timespec='seconds'),
                                                                  each.end_ts.isoformat(timespec='seconds'),
                                                                  self.testPlanKey,
                                                                  self.testExecKey,
                                                                  self.revision,
                                                                  self.testEnvironment,
                                                                  self.version)
            summaries[self.testExecKey]["tests"].append(each.as_dict())

        return summaries.values()

    def _create_header(self, start_ts, end_ts, testPlanKey, testExecKey, revision, testEnvironment, version):
        if revision:
            description = f"Test Execution for Test Plan {testPlanKey} @{end_ts} with revision of {revision}"
        else:
            description = f"Test Execution for Test Plan {testPlanKey} @{end_ts}"

        report_json = {
            "testExecutionKey": testExecKey,
            "info": {
                "summary": description,
                "description": description,
                "version": version,
                # "user": "",
                "revision": revision,
                "startDate": start_ts,
                "finishDate": end_ts,
                "testPlanKey": testPlanKey,
                "testEnvironments": [testEnvironment],
            },
            "tests": [],
        }
        if not testExecKey:
            report_json.pop('testExecutionKey')
        return report_json
