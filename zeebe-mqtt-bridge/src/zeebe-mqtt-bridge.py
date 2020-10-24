import json
import logging
import grpc
from zeebe_grpc import gateway_pb2, gateway_pb2_grpc
import paho.mqtt.client as mqtt
import uuid

TOPIC_PREFIX = "zeebe"
MQTT_HOST = "localhost"
MQTT_PORT = 1883
ZEEBE_HOST = "localhost"
ZEEBE_PORT = 26500
ZEEBE_WORKER_TYPE = "zeebe-mqtt-worker"
ZEEBE_WORKER_NAME = "zeebe-mqtt-bridge"

logging.basicConfig(level=logging.DEBUG)

class Zeebe:
    def __init__(self):
        channel = grpc.insecure_channel("%s:%s" % (ZEEBE_HOST, ZEEBE_PORT))
        self.stub = gateway_pb2_grpc.GatewayStub(channel)            

    def startWorker(self, callback):
        logging.debug("Start worker polling")
        activate_jobs_response = self.stub.ActivateJobs(
            gateway_pb2.ActivateJobsRequest(
                timeout=10000,
                type=ZEEBE_WORKER_TYPE,
                worker=ZEEBE_WORKER_NAME,
                maxJobsToActivate=16
            )
        )

        for response in activate_jobs_response:
            for job in response.jobs:
                try:
                    callback(jobKey=job.key, variables=job.variables)
                    self.stub.CompleteJob(gateway_pb2.CompleteJobRequest(jobKey=job.key, variables=json.dumps({})))
                    logging.info("Job completed")
                except Exception as e:
                    self.stub.FailJob(gateway_pb2.FailJobRequest(jobKey=job.key))
                    logging.info("Job failed {}".format(e))

        self.startWorker(callback)

    def createWorkflowInstance(self, bpmnProcessId, version=-1, variables={}):
        logging.debug("Create workflow instance for %s" % bpmnProcessId)
        variables['processId'] = str(uuid.uuid4())
        
        self.stub.CreateWorkflowInstance(
            gateway_pb2.CreateWorkflowInstanceRequest(
                bpmnProcessId=bpmnProcessId,
                version=version,
                variables=json.dumps(variables)
            )
        )

    def publishMessage(self, name, correlationKey, timeToLive=10000, messageId=None, variables={}):
        logging.debug("Publish message")
        self.stub.PublishMessage(
            gateway_pb2.PublishMessageRequest(        
                name=name,
                correlationKey=correlationKey,
                timeToLive=timeToLive,
                messageId=messageId or str(uuid.uuid4()),
                variables=json.dumps(variables)
            )
        )

def main():
    zeebe = Zeebe()
    client = mqtt.Client()

    def on_message(client, userdata, msg):
        payload = str(msg.payload.decode("utf-8"))

        methods = {
            "%s/grpc/createWorkflowInstance" % TOPIC_PREFIX: zeebe.createWorkflowInstance,
            "%s/grpc/publishMessage" % TOPIC_PREFIX: zeebe.publishMessage
        }

        try:
            method = methods[msg.topic]
            method(**json.loads(payload))
        except KeyError:
            logging.warning("Method %s is unsupported" % msg.topic)

    def on_job(**kwargs):

        client.publish("%s/job" % TOPIC_PREFIX, json.dumps(kwargs))

    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.subscribe("%s/grpc/#" % TOPIC_PREFIX)
    client.loop_start()

    zeebe.startWorker(callback=on_job)

if __name__ == "__main__":
    main()