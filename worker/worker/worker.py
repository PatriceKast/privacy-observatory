import threading
import queue
import time
import multiprocessing
import os
import json

import api

stop_study_heartbeat = True

class Worker:
    def __init__(self, api_host, api_tkn):
        print("Worker instatiated")
        self.api = api.API(api_host, api_tkn)

        print("Retrieving Worker Details:")
        details = self.api.send_ret_json('GET', 'workers/', None)
        print(details)
        self.worker_id = details['id']

        t0 = threading.Thread(target=self.keep_alive, args=( )).start()

        self.run_job()

    def run_job(self):
        while(True):
            print("Query a new job to perform")
            # try to get next job that is in order
            job = self.api.send_ret_json('GET', 'jobs/next', None)

            # in case a new job is for performing, the ID is set
            if 'id' in job.keys():
                print("new job found")
                study_id = str(job['id'])
                study = self.api.send_ret_json('GET', 'studys/' + study_id, None)
                inputStr = self.api.send('GET', 'domainsets/run/' + str(study['domainset_id']), None)

                self.run_dockers(study_id, inputStr, study['composefile'])

            time.sleep(10)

    def run_dockers(self, study_id, inputStr, dockerComposeStr):
        # change working dir
        os.chdir('/opt/')

        print("write to input file")
        with open("/opt/input.txt", "w") as file:
            file.write(inputStr)
        
        print("prepare output file")
        os.system('echo "" > output.txt')

        print("write to docker-compose file")
        with open("/opt/docker-compose.yaml", "w") as file:
            file.write(dockerComposeStr)

        stop_study_heartbeat = False
        t1 = threading.Thread(target=self.log_scanning, args=(study_id, ))
        t1.start()

        print("start docker-compose")
        os.system('docker-compose up --force-recreate --remove-orphans')
        print("docker-compose has finalized")

        print("send logs to api")
        logs = os.popen('docker-compose logs').read()

        print("load output file")
        with open("/opt/output.txt") as file:
            print("send output to api")
            file_content = json.loads(file.read())

            # add additional fields to the output json
            file_content['output'] = logs
            file_content['study_id'] = study_id

            self.api.send('POST', 'runs', file_content)

        stop_study_heartbeat = True
        t1.join()

    def log_scanning(self, study_id):
        old_logs = None
        while True:
            if stop_study_heartbeat:
                print("kill study heartbeat")
                break

            print("read logs")
            os.chdir('/opt/')
            logs = os.popen('docker-compose logs').read()
            if logs != old_logs:
                print("modification detected, sending hearbeat")
                self.send_heartbeat(study_id)

            time.sleep(15)

    def keep_alive(self, study_id = None):
        while True:
            print("Trigger Heartbeat")
            self.send_heartbeat(study_id)
            time.sleep(15)

    def send_heartbeat(self, study_id = None):
        print(study_id)
        if study_id:
            self.api.send('GET', 'jobs/heartbeat/' + str(study_id), None)
        else:
            self.api.send('GET', 'workers/heartbeat/' + str(self.worker_id), None)