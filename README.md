# About

This project introduces web interface (based on flask) to run pytest and introduce test configuration and test data in human readable interface.

# Installation

```shell 
git clone --recurse-submodules https://gitlab.2n.cz/hip/autotest-webrunner.git
```

created virtual environment and install all dependencies and activate it 
```shell
python -m venv .venv
pip install -r requirements.txt
.\.venv\Scripts\activate   # activate in shell
source ./.venv/bin/activate   # activate in bash
```
# Starting the webserver
To start the webserver using waitress in root folder of this project. 

```shell
waitress-serve --listen *:5001 --threads 12 app:app
```
- **listen** - configures the ip and port where will the webserver run (* means on all local interfaces)
- **threads** - is how many threads will waitress use for handling requests, normally default is 4. Value 12 was chosen by trial and error. More threads mean more memory requirements on the host machine
- **app:app** - its the name of the module followed by name of variable containing the flask Application

# Helper scripts
## crontask_util.py
This is simple terminal python module that helps retrieving useful information from intercoms. Have venv activated to have all needed dependencies ready
```
usage: crontask_util.py [-h] [--list] [--package addr passw]

Utility functions for bash scripts

options:
  -h, --help            show this help message and exit
  --list                Print device list used in automation polygon
  --package addr passw  Print device firmware package i.e. 'verso'
```

List example. Shows the current list of ip addresses in test polygon. This reads values from constants.py 
```shell
python crontask_util.py --list

```
package command example
```shell
python crontask_util.py --package 10.27.24.27 2n
```
prints the "fw package name" of the device. i.e. "verso"

## cron_command.sh
This script is used by then cron task that usually daily executes tests on test polygon

```shell
./cron_command.sh
```

Retrieves the list of all ip addresses on polygons, tries to reset them to factory settings and executes api, smoke and regressions tests in sequence
For debugging purposes following param can be used

```shell
./cron_command.sh 10.27.24.27
```
This ignores the list of devices on test polygon, and executes the given tests only on the provided ip address