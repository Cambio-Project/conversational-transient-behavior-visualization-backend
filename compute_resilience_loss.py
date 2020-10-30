import numpy as np

from chatbot_webservice.models import Service, ServiceData, Specification

expected_qos = 100
qos_threshold = 90
median_range = 5
call_ids = {
    'loon-service': [0, 1, 2, 3, 4],
    'loon-service2': [5]
}
tb_causes = ['failure', 'deployment', 'load-balancing']


def get_next_items(data, idx):
    last_index = idx + median_range if idx + median_range < len(data) else len(data) - 1
    return data[idx:last_index]


def median_of_items(data, idx):
    next_items = get_next_items(data, idx)
    next_qos = list(map(lambda item: item.qos, next_items))
    return np.median(next_qos)


def is_initial_loss(data, idx):
    median = median_of_items(data, idx)
    if median < qos_threshold:
        return True
    return False


def get_start_index(data, idx):
    next_items = get_next_items(data, idx)
    minimum = data[idx]
    min_idx = idx

    for j, item in enumerate(next_items):
        if item.qos < minimum.qos:
            minimum = item
            min_idx = idx + j

    return min_idx


def get_end_index(data, idx):
    remaining_data = data[idx + 1:len(data)]

    for j, item in enumerate(remaining_data):
        if item.qos >= expected_qos:
            median = median_of_items(remaining_data, j)
            if median >= qos_threshold:
                return idx + 1 + j
    return len(data) - 1


def find_transient_behavior(data: ServiceData, specification: Specification):
    max_recovery_time = specification.max_recovery_time
    specification_endpoint = -1.0
    transient_behavior_endpoint = -1.0

    transient_behavior_indices = []

    for i, item in enumerate(data):
        if item.time > specification_endpoint and item.time > transient_behavior_endpoint:
            if item.qos < expected_qos:
                if is_initial_loss(data, i):
                    start_index = get_start_index(data, i)
                    end_index = get_end_index(data, start_index)
                    transient_behavior_indices.append([start_index, end_index])
                    transient_behavior_endpoint = data[end_index].time
                    specification_endpoint = data[start_index].time + max_recovery_time

    return transient_behavior_indices


services = Service.objects.all()

for service in services:
    endpoints = call_ids[service.name]

    for endpoint in endpoints:
        for cause in tb_causes:
            try:
                specification = Specification.objects.get(service_id=service.id, cause=cause)
                data = ServiceData.objects.all().filter(service_id=service.id, callId=endpoint)

                tb_occurrences = find_transient_behavior(data, specification)
                print(f'{service.name}, {endpoint}, {cause}: {tb_occurrences}')

            except Specification.DoesNotExist:
                print(f'No specification for {service.name} in case of {cause}')
