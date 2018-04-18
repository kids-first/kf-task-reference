import os
import time
import requests
from flask import Flask, request, jsonify, abort
from flask.ext.rq import RQ, job


app = Flask(__name__)

app.config['RQ_DEFAULT_HOST'] = os.environ.get('REDIS_HOST', 'redis')
app.config['RQ_DEFAULT_PORT'] = os.environ.get('REDIS_PORT', 6379)
app.config['RQ_DEFAULT_DB'] = 1

RQ(app)

tasks = {}
COORDINATOR_API = os.environ.get('COORDINATOR_API', 'http://coordinator')


@app.route("/status")
def status():
    # return jsonify(requests.get(COORDINATOR_API).json())
    return jsonify({'name': 'example task', 'version': '1.0.0'})


@job
def process(task_id, release_id, progress=0):
    """ Do something here to prepare for the release """
    time.sleep(10)
    # Interact with dataservice
    studies = requests.get(COORDINATOR_API+'/releases/'+release_id).json()
    resp = requests.patch(COORDINATOR_API+'/tasks/'+task_id,
                          json={'state': 'staged', 'progress': 100})


@job
def publish(task_id, release_id, progress=0):
    """ Complete the final steps to make the new data public """
    time.sleep(5)
    # Processing here
    # Inform coordinator that the task has been published
    resp = requests.patch(COORDINATOR_API+'/tasks/'+task_id,
                          json={'state': 'published', 'progress': 100})
    

def parse_request(req):
    """ Parse fields from post body """
    # Parsing out the request body
    data = req.get_json()
    if (data is None or
        'action' not in data or
        'task_id' not in data or
        'release_id' not in data):
        abort(400)
    
    action = data['action']
    task = data['task_id']
    release = data['release_id']
    return action, task, release


@app.route("/tasks", methods=['POST'])
def task_endponit():
    """ Handles all actions sent by the coordinator """
    action, task, release = parse_request(request)

    # Determine what action to take
    if action == 'initialize':
        # Assert that the service is ready to start a new task
        tasks[task] = {
            'state': 'pending',
            'release_id': release,
            'task_id': task,
            'progress': 0
        }
    elif action == 'start':
        # Here is where the bulk of the processing will happen
        tasks[task] = {
            'state': 'running',
            'release_id': release,
            'task_id': task,
            'progress': 0
        }
        # Add to the queue
        process.delay(task, release)
    elif action == 'publish':
        # Make the changes live
        tasks[task] = {
            'state': 'publishing',
            'release_id': release,
            'task_id': task,
            'progress': 0
        }
        publish.delay(task, release)
    elif action == 'get_status':
        if task_id not in tasks:
            abort(404)
        return tasks[task]
    elif action == 'cancel':
        tasks[task] = {
            'state': 'canceled',
            'release_id': release,
            'task_id': task,
            'progress': 0
        }
    else:
        # Not a valid action
        abort(400)

    # Return current task state
    return jsonify(tasks[task])
