# NUSHMods Project

Inspired by NUSMods, NUSHMods displays info about NUS High's modules and teachers. It also helps students keep track of homework across classes. This project makes use of MySQL to store the module, teacher and homework data. The information is presented through a web interface built using Bootstrap and Flask. Future work includes porting over the application to Vue.js for the frontend, and providing more help in choosing majors, via options for viewing majoring options, forecasting their future workload in hours, and visualising prerequisite/corequisite graphs.

## Setup
1. Install NodeJS, npm, and Python 3
2. Run `pip install -r requirements.txt`

## Running
1. Run the Flask backend:
`cd backend`
`python app.py`
2. Open second terminal (use screen or something), then run Vue frontend
`cd frontend/src`
`npm run serve`


