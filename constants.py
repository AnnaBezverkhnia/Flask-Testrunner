from pathlib import Path
import os

root_dir = str(Path(__file__).parent)

autotest_path: str = 'autotest'  # Path to folder containing root of pytest test suite

report_dir_path = os.path.join(os.sep, root_dir, 'static')

# Gandalf proxy web https://automation.ui.2n.cz/

junit_report_path = os.path.join(report_dir_path, 'smoke', 'junit')
junit_file_template = '_junit_report.xml'

TESTRAIL_USERNAME = 'testteam2n@gmail.com'
TESTRAIL_PASSWORD = 'eThdQ3gwGORjhVv1HsU6-aeQdaVl1ksK0dU3UobhB'
PROJECT_NAME = "2N OS all"

polygon_devices: list[dict] = [
    {'ip': '10.0.72.126', 'model': 'IPS', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationips.ui.2n.cz'},
    {'ip': '10.0.72.108', 'model': 'Base', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationbase.ui.2n.cz'},
    {'ip': '10.0.72.109', 'model': 'Base', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': ''},
    {'ip': '10.0.72.111', 'model': 'Vario', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationvario.ui.2n.cz'},
    {'ip': '10.0.72.107', 'model': 'Uni', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationuni.ui.2n.cz'},
    {'ip': '10.0.72.115', 'model': 'Solo', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationsolo.ui.2n.cz'},
    {'ip': '10.0.72.102', 'model': 'AU', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationau.ui.2n.cz'},
    {'ip': '10.0.72.116', 'model': 'AU 2.0', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationautwo.ui.2n.cz'},
    {'ip': '10.0.72.114', 'model': 'Safety', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationsafety.ui.2n.cz'},
    {'ip': '10.0.72.104', 'model': 'Video Kit', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationsafety.ui.2n.cz'},
    {'ip': '10.0.72.105', 'model': 'Audio Kit', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationaudiokit.ui.2n.cz'},
    {'ip': '10.0.72.110', 'model': 'Verso', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationverso.ui.2n.cz'},
    {'ip': '10.0.72.101', 'model': 'Verso', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationversosecond.ui.2n.cz'},
    {'ip': '10.0.72.112', 'model': 'SIP Speaker Horn', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationhorn.ui.2n.cz'},
    {'ip': '10.0.72.121', 'model': 'SIP Speaker', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': ''},
    {'ip': '10.0.72.117', 'model': 'Indoor Compact', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationcompact.ui.2n.cz'},
    {'ip': '10.0.72.118', 'model': 'Indoor View', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationview.ui.2n.cz'},
    {'ip': '10.0.72.119', 'model': 'Indoor Talk', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationtalk.ui.2n.cz'},
    {'ip': '10.0.72.125', 'model': 'Clip', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationclip.ui.2n.cz'},
    {'ip': '10.0.72.120', 'model': 'Verso 2.0', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationversotwo.ui.2n.cz'},
    {'ip': '10.0.72.122', 'model': 'AUM', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationaum.ui.2n.cz'},
    {'ip': '10.0.72.123', 'model': 'IP One', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': 'https://automationipone.ui.2n.cz'},
    {'ip': '10.0.72.106', 'model': 'Audio Converter', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': ''}, 
    {'ip': '10.0.72.103', 'model': 'Force', 'password': 'Test1234', 'add_device': '10.0.72.124', 'gandalf_url': ''},
]
