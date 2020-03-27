import json
import os
from configparser import ConfigParser
import logging

from .models import XrayTestReport
from .utils import PublishXrayResults, associate_marker_metadata_for, get_test_key_for
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

XRAY_PLUGIN = "JIRA_XRAY"
data_formats = {}


def pytest_configure(config):
    ini_config = config.inifile.strpath
    xrayconfig = ConfigParser()
    xrayconfig.read(ini_config)
    try:
        XRAY_API_BASE_URL = xrayconfig.get('xray', 'XRAY_API_BASE_URL')
    except Exception as e:
        raise RuntimeError("Missing XRAY_API_BASE_URL of xray config in pytest.ini", e)

    base64_code = config.getoption("--authentication")
    testPlanKey = config.getoption("--test-plan-key")
    testExecKey = config.getoption("--test-exec-key")
    revision = config.getoption("--revision")
    testEnvironment = config.getoption("--test-environment")
    version = config.getoption("--test-plan-version")
    if not testPlanKey:
        raise RuntimeError("Missing test plan key in pytest command line! Usage: --test-plan-key")
    if not base64_code:
        logger.info("Missing base64 code of Jira username:password, result will not report to Xray. Usage: --authentication")
        return

    plugin = PublishXrayResults(
        base_url=XRAY_API_BASE_URL,
        base64_code=base64_code,
        testPlanKey=testPlanKey,
        testExecKey=testExecKey,
        revision=revision,
        testEnvironment=testEnvironment,
        version=version
    )
    config.pluginmanager.register(plugin, XRAY_PLUGIN)


def pytest_addoption(parser):
    group = parser.getgroup("JIRA Xray integration")
    group.addoption('--authentication', action='store', help='base64 code of Jira username:password to login jira')
    group.addoption('--test-plan-key', action='store', help='test plan key in Jira to attach to. For instance: CCATM-24')
    group.addoption('--test-exec-key', action='store', default="", help='Key of test execution where automated test report is imported. For instance: CCATM-109')
    group.addoption('--revision', action='store', default="", help='revision of the test execution for automated test. For instance: 1.0.2512.3f1fe19')
    group.addoption('--test-environment', action='store', default="", help='test environment. For instance: iOS')
    group.addoption('--test-plan-version', action='store', default="", help='version of the test plan. For instance: v1.0')


def pytest_collection_modifyitems(config, items):
    if not config.getoption('--authentication'):
        return
    data_path = get_data_file_path(config)
    test_keys = load_and_extract_test_keys(data_path)
    if not test_keys:
        return
    for item, test_key in zip(items, test_keys):
        associate_marker_metadata_for(item, test_key)


def pytest_terminal_summary(terminalreporter):
    if not terminalreporter.config.getoption('--authentication'):
        return

    test_reports = []
    temp_reports = {}
    if "passed" in terminalreporter.stats:
        for each in terminalreporter.stats["passed"]:
            test_key = get_test_key_for(each)
            if not test_key:
                continue
            elif test_key in temp_reports.keys():
                temp_reports[test_key]['duration'] += each.duration
            else:
                temp_reports[test_key] = {'duration': each.duration}

    if "failed" in terminalreporter.stats:
        for each in terminalreporter.stats["failed"]:
            test_key = get_test_key_for(each)
            if not test_key:
                continue
            elif test_key in temp_reports.keys():
                temp_reports[test_key]['duration'] += each.duration
                temp_reports[test_key]['longreprtext'] = temp_reports[test_key].get('longreprtext', '') + f'\n{each.longreprtext}'
            else:
                temp_reports[test_key] = {'duration': each.duration}
                temp_reports[test_key] = {'longreprtext': each.longreprtext}

    for k, v in temp_reports.items():
        if v.get('longreprtext'):
            report = XrayTestReport.as_failed(k, v['duration'], v['longreprtext'])
        else:
            report = XrayTestReport.as_passed(k, v['duration'])
        test_reports.append(report)
    publish_results = terminalreporter.config.pluginmanager.get_plugin(XRAY_PLUGIN)

    if not callable(publish_results):
        raise TypeError("Xray plugin is not a callable. Please review 'pytest_configure' hook!")

    publish_results(*test_reports)


def get_data_file_path(config):
    work_dir = str(config.rootdir)
    data_path = config._assertstate.hook.session._initialparts[0][0].strpath.replace(str(os.path.join(work_dir, "tests")),
                                                                                     str(os.path.join(work_dir, 'data')))
    return data_path


def load_and_extract_test_keys(data_file):
    if data_file.endswith('.py'):
        data_file = data_file.replace('.py', '.json')
    with open(data_file, encoding='utf-8') as f:
        data_dict = json.load(f)
    test_keys = []
    for item in data_dict['test']:
        key = item.get('test_key', None)
        test_keys.append(key)
    return test_keys

