import csv
import numpy as np

from chatbot_webservice.models import Service, ServiceData

SCENARIO = 1
SYSTEM = 'accounting-system'

file_path = 'results_per_request_r4.csv'
percentile = 80
counter = 0


######################################## methods #################################################################
def compute_percentile(service, call_id, k):
    values = []

    with open(file_path, newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        next(reader, None)

        for row in reader:
            service_name = row[2]
            service_call_id = row[1]

            if service_name == service and service_call_id == call_id:
                response_time = row[8]
                values.append(float(response_time))

    array = np.array(values)
    return np.percentile(array, k)


def assign_percentile(qos, service, call_id):
    qos[service][call_id] = compute_percentile(service, call_id, percentile)


def create_expected_qos_map():
    qos = {
        'loon-service': {
            '0': -1.0,
            '1': -1.0,
            '2': -1.0,
            '3': -1.0,
            '4': -1.0
        },
        'loon-service2': {
            '5': -1.0
        }
    }

    assign_percentile(qos, 'loon-service', '0')
    assign_percentile(qos, 'loon-service', '1')
    assign_percentile(qos, 'loon-service', '2')
    assign_percentile(qos, 'loon-service', '3')
    assign_percentile(qos, 'loon-service', '4')
    assign_percentile(qos, 'loon-service2', '5')

    return qos
######################################## methods #################################################################


specifiedResponseTimes = create_expected_qos_map()
print(f'Specified response times: {specifiedResponseTimes}')

with open(file_path, newline='') as csv_file:
    data_reader = csv.reader(csv_file, delimiter=',')
    next(data_reader, None) # skip header
    for row in data_reader:
        counter += 1

        service_name = row[2]
        call_id = row[1]
        service = Service.objects.get(name=service_name, system=SYSTEM, scenario=SCENARIO)

        avgResponseTime = row[8]
        expectedResponseTime = specifiedResponseTimes[service_name][call_id]

        if float(avgResponseTime) == 0.0:
            qos = 100
        else:
            qos = round((float(expectedResponseTime) / float(avgResponseTime)) * 100)
            if qos > 100:
                qos = 100

        ServiceData.objects.create(
            service=service,
            time=row[0],
            callId=call_id,
            uri=row[4],
            qos=qos
        )

        if counter % 50 == 0:
            print(counter,  end='\r')

