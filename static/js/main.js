import { interval } from './constants.js';
document.addEventListener('DOMContentLoaded', function() {
    function throttle(fn, wait) {
        let lastTime = 0;
        return function(...args) {
            const now = new Date().getTime();
            if (now - lastTime >= wait) {
                lastTime = now;
                return fn(...args);
            }
        };
    }

    // Function to check for hidden elements and disable/enable the button accordingly
    function checkPollingElements() {
        const hiddenElements = document.querySelectorAll('[hidden^="hidden_"]');
        const hiddenDevIds = new Set();
        hiddenElements.forEach(el => {
            const hiddenAttr = el.getAttribute('hidden');
            const devId = hiddenAttr.replace('hidden_', '');
            hiddenDevIds.add(devId);
        });

        const buttons = document.querySelectorAll('.start-btn');
        buttons.forEach(button => {
            const buttonDevId = Array.from(button.classList).find(cls => cls.startsWith('dev_id_'));
            if (hiddenDevIds.has(buttonDevId)) {
                button.disabled = true;
            } else {
                button.disabled = false;
            }
        });
    }

    // Throttled version of the check function
    const throttledCheckPollingElements = throttle(checkPollingElements, 1000);

    // MutationObserver to watch for changes in the DOM
    const observer = new MutationObserver((mutationsList, observer) => {
        throttledCheckPollingElements();
    });

    // Start observing the entire document for changes in child nodes and attributes
    observer.observe(document.body, { attributes: true, childList: true, subtree: true });

    // Initial check on page load
    fetch('/get_jobs_status')
        .then(response => response.json())
        .then(data => {
            data.forEach(job => {
                if (job.status === "queued" || job.status === "started") {
                    let pollingDiv = document.createElement('div');
                    pollingDiv.hidden = true;
                    pollingDiv.setAttribute('hx-trigger', 'every 1s');
                    pollingDiv.setAttribute('hx-get', `/progress_report/${job.id}`);
                    pollingDiv.setAttribute('hx-target', `.${job.test_suite}_tests.${job.dev_id}.progress-container`);

                    let container = document.querySelector(`.${job.test_suite}_tests.${job.dev_id}.progress-container`);
                    if (container) {
                        container.appendChild(pollingDiv);
                        htmx.process(pollingDiv);
                    } else {
                        console.warn(`Container not found for job: ${job.id}`);
                    }
                }
            });

            let startButtons = document.querySelectorAll('.start-btn');
            for (let i = 0; i < startButtons.length; i++) {
                startButtons[i].addEventListener('htmx:configRequest', prepareTestRunData);
            }

            let reportLinks = document.querySelectorAll('.result-btn');
            for (let i = 0; i < reportLinks.length; i++) {
                prepareReportLink(reportLinks[i]);
            }

            let startTestsOnAllButton = document.querySelector('.start-btn-all');
            if (startTestsOnAllButton) {
                startTestsOnAllButton.addEventListener('click', startTestOnAllDevices);
            }

            const SharedInputElements = [
                { input: document.querySelector('.password-all:first-child'), targetClass: '.password' },
                { input: document.querySelector('.release_firmware-all:first-child'), targetClass: '.release_firmware' },
                { input: document.querySelector('.upgrade-fw-all:first-child'), targetClass: '.upgrade_fw' },
                { input: document.querySelector('.additional-device-all:first-child'), targetClass: '.add-dev' },
            ];

            let testPathAll = document.querySelector('.test-path-all:first-child');
            if (testPathAll) {
                testPathAll.addEventListener('change', function () {
                    addValueToAllDevices(testPathAll, '.test-path');
                });
            }

            SharedInputElements.forEach(({ input, targetClass }) => {
                if (input) {
                    input.addEventListener('input', function () {
                        addValueToAllDevices(input, targetClass);
                    });
                }
            });
        })
        .catch(error => console.error('Error fetching data:', error));

    function prepareReportLink(reportButtonElement) {
        reportButtonElement.addEventListener('click', (event) => {
            let deviceId = reportButtonElement.parentElement.className.split(' ')[0];
            let element = document.querySelector(`.ip.${deviceId}`);
            let ip = element.tagName.toLowerCase() === 'a' ? element.innerText : element.value;
            let pageType = document.querySelector('input[name="page_type"]').value;
            let reportURL = 'static/' + pageType + '/' + ip + 'report.html' + '?sort=result&visible=failed,error,xfailed,xpassed,rerun';
            reportButtonElement.href = reportURL;
        });
    }

    function addValueToAllDevices(inputElement, targetClass) {
        let inputValue = inputElement.value;
        let inputsCollection = document.querySelectorAll(targetClass);
        inputsCollection.forEach(function (input) {
            input.value = inputValue;
        });
    }

    function startTestOnAllDevices(event) {
        let rowCount = document.querySelectorAll('.table tbody tr').length;
        for (let i = 1; i <= (rowCount - 1); i++) {
            let deviceId = `dev_id_${i}`;
            let button = document.querySelector(`.start-btn.${deviceId}`);
            if (button) {
                button.click();
            }
        }
    }

    function prepareTestRunData(event) {
        let button = event.target;
        let deviceId = button.classList[1];
        let element = document.querySelector(`.ip.${deviceId}`);
        let ip = element.tagName.toLowerCase() === 'a' ? element.innerText : element.value;
        let password = document.querySelector(`.password.${deviceId}`).value;
        let release_firmware = document.querySelector(`.release_firmware.${deviceId}`) ? document.querySelector(`.release_firmware.${deviceId}`).value : null;
        let upgrade = document.querySelector(`.upgrade_fw.${deviceId}`).value;
        let addDevice = document.querySelector(`.add-dev.${deviceId}`).value;
        let testType = document.querySelector('input[name="page_type"]').value;

        let testrun_data = {
            dut: `--dut=${ip}`,
            password: `--password=${password}`,
            add_dev: `--additional-device=${addDevice}`,
            test_type: `${testType}`,
            report_html: `${ip}report.html`,
            html_type: `--self-contained-html`,
            dev_id: `${deviceId}`,
        };

        if (release_firmware) {
            testrun_data.release_firmware = `--release_firmware=${release_firmware}`;
        }

        if (upgrade) {
            testrun_data.upgrade = `--upgrade=${upgrade}`;
        }

        let testPath = document.querySelector(`.test-path.${deviceId}`).value;
        if (testType === 'api') {
            testPath = testPath === 'all' ? `api_tests` : `api_tests/${testPath}`;
        } else if (testType === 'regression') {
            testPath = testPath === 'all' ? `regression_tests` : `regression_tests/${testPath}`;
        } else if (testType === 'smoke') {
            if (testPath === 'all') {
                testPath = `-m smoke`;
                testrun_data.junitxml = true;
            } else {
                testPath = `smoke_test/${testPath}`;
            }
        } else if (testType === 'gandalf') {
            let gandalfUrl = document.querySelector(`a[name="gandalf ${deviceId}"]`).getAttribute('href');
            testrun_data["gandalf-url"] = `--gandalf-url=${gandalfUrl}`;
            testPath = testPath === 'all' ? `gandalf_tests` : `gandalf_tests/${testPath}`;
        } else {
            if (testPath === `smoke_tests/all`) {
                testPath = '-m smoke';
                testrun_data.junitxml = true;
            } else if (testPath === `api_test/all`) {
                testPath = 'api_tests';
            } else if (testPath === `regression_tests/all`) {
                testPath = 'regression_tests';
            }
        }

        testrun_data.test_path = `${testPath}`;

        event.detail.parameters = testrun_data;
    }

    $(document).ready(function () {
        var sendToTestRailButtons = $(".send-to-testrail-btn");
        var sendAllToTestRailButton = $(".send-all-to-testrail-btn");
        var milestoneIdAllInput = $(".milestone-id-all");

        sendToTestRailButtons.on("click", function (event) {
            var row = $(this).closest("tr");
            var deviceId = $(this).attr("class").split(" ")[2];
            var element = $(`.ip.${deviceId}`).eq(0);
            var ip = element.prop("tagName").toLowerCase() === "a" ? element.text() : element.val();
            var milestoneId = row.find(".milestone-id").val();

            event.preventDefault();
            sendToTestRail(ip, milestoneId, $(this));
        });

        sendAllToTestRailButton.on("click", function (event) {
            var milestoneIdAllValue = milestoneIdAllInput.val();
            var milestoneIdInputs = $(".milestone-id");

            milestoneIdInputs.val(milestoneIdAllValue);

            sendToTestRailButtons.click();
        });
    });

    function sendToTestRail(ip, milestoneId, button) {
        button.prop("disabled", true);

        var formData = new FormData();
        formData.append('ip', ip);
        formData.append('milestoneId', milestoneId);

        fetch("/send_reports", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            button.prop("disabled", false);
            alert(data.results[0]);
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Error sending report to TestRail!");
            button.prop("disabled", false);
        });
    }
});
