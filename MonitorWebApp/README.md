
# PacwarMonitor
Web application to monitor genetic algorithm

## Installation
1. pip install flask
2. pip install gunicorn

## Usage
1. Each line in log file must have three comma seperated values (max score, avg score, avg hamming distance)
2. Modify `config.txt` to change the password, your own python directory and log directory
3. `export FLASK_APP=monitor.py`
4. `flask run --debugger -h 0.0.0.0` (frontend)
5. `nohup gunicorn -w 4 -b 0.0.0.0:5000 monitor:app &` (backend)

## Demo (Not available: This instance is very expensive so I'll close it soon)
http://35.161.96.186:5000/#


