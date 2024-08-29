import logging
import os
import pytest
import subprocess
import rq_dashboard

from redis import Redis
from rq import Queue, get_current_job, Connection, Worker
from rq.job import Job, JobStatus
from dataclasses import dataclass
from flask import Flask, render_template, jsonify
from flask import redirect, request, url_for
from flask_bootstrap import Bootstrap

from _pytest.reports import TestReport
from constants import PROJECT_NAME, autotest_path, TESTRAIL_USERNAME, TESTRAIL_PASSWORD, polygon_devices, \
    report_dir_path, root_dir, junit_report_path, junit_file_template

logging.basicConfig(
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    format="[%(levelname)s]: %(asctime)s %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

app = Flask(__name__)
Bootstrap(app)

redis = Redis(host='localhost', port=6379, db=0)
q = Queue(connection=redis, default_timeout=7200)

app.config['RQ_DASHBOARD_REDIS_URL'] = "redis://localhost:6379"
# setup rq dashboard
app.config.from_object(rq_dashboard.default_settings)
rq_dashboard.web.setup_rq_connection(app)
app.register_blueprint(rq_dashboard.blueprint, url_prefix='/dashboard')

autotest_path = os.path.join(root_dir, autotest_path)

# shared synchronized dictionary that can be updated by multiple processes,
# structure is {device_id: testrun_progress_in_percentage}
shared_test_result = {}


@app.route("/progress_report/<job_key>", methods=["GET"])
def progress_report(job_key):
    job = Job.fetch(job_key, connection=redis)
    dev_id = job.meta.get('dev_id', '')
    progress = job.meta.get('progress', 0)
    test_suite = job.meta.get('test_suite', '')
    logging.info(f'DEVICE ID IN PROGRESS_REPORT IS {dev_id}')
    if job.is_finished:
        logging.info(F'JOB {job_key} IS FINISHED')
        if job.meta.get('failed_tests', 0) != 0:
            return render_template("progress_bar.html", dev_id=dev_id, progress=100, polling=False, job_key=job_key,
                                   fail=True)
        return render_template("progress_bar.html", dev_id=dev_id, progress=100, polling=False, job_key=job_key)
    if job.get_status() == "failed":
        return render_template("progress_bar.html", dev_id=dev_id, progress=100, polling=False, job_key=job_key)
    else:
        print(f'Progress on {job_key} is {progress}')
        return render_template("progress_bar.html", progress=int(progress), polling=True, job_key=job_key,
                               dev_id=dev_id, test_suite=test_suite)


@dataclass
class TestStatus:
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0


class Progress:
    '''
    Progress class is used to display testrun progress on the main page. This is considered as Pytest plugin.
    '''

    def __init__(self):
        self.test_status = TestStatus()
        self.progress = 0
        self.job = get_current_job()

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtestloop(self, session):
        # Count the number of tests that will actually be run
        self.test_status.total_tests = session.testscollected

    def pytest_runtest_logreport(self, report: TestReport):
        if report.when == 'setup':
            if report.failed:
                self.test_status.failed_tests += 1
        if report.when == 'call':
            if report.passed:
                self.test_status.passed_tests += 1
            elif report.failed:
                self.test_status.failed_tests += 1
            elif report.skipped:
                self.test_status.skipped_tests += 1
        if report.when == 'teardown':
            if report.failed:
                self.test_status.failed_tests += 1

        self.percentage = int(
            ((self.test_status.passed_tests + self.test_status.failed_tests) / self.test_status.total_tests) * 100)

        logging.debug(f'Test progress: {self.percentage}%')
        logging.debug(f'Tests passed: {self.test_status.passed_tests}')
        logging.debug(f'Tests failed: {self.test_status.failed_tests}')
        logging.debug(f'Tests skipped: {self.test_status.skipped_tests}')
        logging.debug(f'Tests planned: {self.test_status.total_tests}')

        self.job.meta['progress'] = self.percentage
        self.job.save_meta()

    def pytest_sessionfinish(self, exitstatus):
        self.job.meta['progress'] = 100
        self.job.meta['completed'] = True
        self.job.meta['exitstatus'] = exitstatus
        self.job.meta['failed_tests'] = self.test_status.failed_tests
        self.job.set_status(JobStatus.FINISHED)
        self.job.save_meta()


# generate database and display its data  on main page
def get_folder_names(directory):
    '''
    method to list all subdirectories in a given directory, excluding those starting with '__' (e.g. __pycache__)
    this is mainly used
    '''
    # behold the power of list comprehension
    return [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d)) and not d.startswith('__')]


@app.route('/')
def home():
    return redirect(url_for('api'))


@app.route("/api")
def api() -> str:
    test_list = get_folder_names(os.path.join(autotest_path, 'api_tests'))
    intercoms = polygon_devices
    return render_template('base.html', intercoms=intercoms, testruns=test_list, test_suite='api')


@app.route("/regression")
def regression() -> str:
    test_list = get_folder_names(os.path.join(autotest_path, 'regression_tests'))
    intercoms = polygon_devices
    return render_template('base.html', intercoms=intercoms, testruns=test_list, test_suite='regression')


@app.route("/smoke")
def smoke() -> str:
    test_list = get_folder_names(os.path.join(autotest_path, 'smoke_test'))
    intercoms = polygon_devices
    return render_template('base.html', intercoms=intercoms, testruns=test_list, test_suite='smoke')


@app.route("/gandalf")
def gandalf() -> str:
    test_list = get_folder_names(os.path.join(autotest_path, 'gandalf_tests'))
    test_list.remove('page')  # removal of module containing page objects
    intercoms = polygon_devices
    return render_template('base.html', intercoms=intercoms, testruns=test_list, test_suite='gandalf')


@app.route("/custom")
def custom() -> str:
    test_list = []
    test_folders = ['api_tests', 'regression_tests']
    for folder in test_folders:
        test_list.append(f'{folder}{os.sep}all')
        for test_suite in get_folder_names(os.path.join(autotest_path, folder)):
            test_list.append(f'{folder}{os.sep}{test_suite}')
    test_list.append(f'smoke_tests{os.sep}all')
    return render_template('base.html', add_device_button=True, testruns=test_list, test_suite='custom')


# #### start test run on chosen device ###

@app.route("/run_tests", methods=["POST"])
def run_tests():
    logging.info("Starting python tests")
    pytestArgs: list[str] = ['-v']

    test_data = request.form.to_dict()

    print(test_data.items())

    for key, value in test_data.items():
        match key:
            case 'test_type':
                test_suite = value
            case 'dev_id':
                dev_id = value
            case 'junitxml':
                if request.form["dut"]:
                    ip = request.form["dut"].split("=")[1]
                    junitxml = f'--junitxml={os.path.join(junit_report_path, f"{ip}{junit_file_template}")}'
                    pytestArgs.append(junitxml)
                else:
                    return 'DUT parameter not provided', 404
            case 'report_html':
                test_type = request.form['test_type']
                value = f'--html={os.path.join(os.sep, report_dir_path, test_type, value)}'
                pytestArgs.append(value)
            case _:
                pytestArgs.append(value)

    logging.info(f'pytestArgs are {pytestArgs}')
    job = q.enqueue(pytest_run, pytestArgs)
    job.meta['dev_id'] = dev_id
    job.meta['test_suite'] = test_suite
    job.save_meta()
    logging.debug(f'job ID is {job.id}')
    logging.debug(f'device id is {dev_id}')

    return render_template("progress_bar.html", dev_id=dev_id, test_suite=test_suite, job_key=job.id, polling=True)


@app.route("/get_jobs_status", methods=["GET"])
def get_jobs_status():
    with Connection(redis):
        # GET INFO ABOUT JOBS, BEING CURRENTLY RUN BY WORKERS
        workers = Worker.all(queue=Queue('default'))
        running_jobs = [worker.get_current_job() for worker in workers if worker.get_current_job()]
        job_info_list = []

        # GET INFO ABOUT JOBS, BEING QUEUED
        queued_jobs = q.jobs

        jobs = queued_jobs + running_jobs

        for job in jobs:
            job_info = {
                'id': job.id,
                'status': job.get_status(),
                'dev_id': job.meta['dev_id'],
                'test_suite': job.meta['test_suite']
            }
            job_info_list.append(job_info)

        return job_info_list


def pytest_run(pytest_args: list[str]) -> None:
    '''
    :pytestArgs: pytest arguments to be passed when initializing a testrun
    :results: connection object, used for updating testrun status. When testrun on the device is completed,
    its status will be set up to "completed".
    '''
    os.chdir(autotest_path)  # change working directory to autotest root
    logging.info(f"Starting python tests with args: {pytest_args}")
    pytest.main(pytest_args, plugins=[Progress()])


def send_report_to_testrail(devname, milestone_id, juitxml):
    ''' send report to TestRail '''
    command = f'trcli -y -h https://testrail.2n.cz --project "{PROJECT_NAME}" --username {TESTRAIL_USERNAME} --password {TESTRAIL_PASSWORD} parse_junit --title "{devname}_TestRun" -f {juitxml} --case-fields custom_minimal_version:7 --case-fields custom_case_type_combo:[5] --case-fields custom_supporteddevice:[0] --case-fields custom_security_test:1 --milestone-id {milestone_id}'

    try:
        subprocess.run(command, shell=True, check=True)
        return 'Report sent successfully to TestRail'
    except subprocess.CalledProcessError as e:
        return f'Error sending report to TestRail: {e}'


@app.route('/send_reports', methods=['POST'])
def send_reports():
    ''' send reports to TestRail'''
    if 'milestoneId' in request.form and 'ip' in request.form:
        juitxml = os.path.join(junit_report_path, f"{request.form['ip']}{junit_file_template}")
        for device in polygon_devices:
            if device['ip'] == request.form['ip']:
                devname = device['model']
        try:
            result_message = send_report_to_testrail(devname, request.form['milestoneId'], juitxml)
            return jsonify({'results': [result_message]})
        except Exception as e:
            return jsonify({'error': str(e)})
    else:
        return 'IP or Milestone ID not provided', 404


if __name__ == '__main__':
    # serve(app, host='0.0.0.0', port=5001, url_prefix='/run_autotest')
    app.run(host='0.0.0.0', port=5002, debug=True)
