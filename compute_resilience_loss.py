import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from chatbot_webservice.models import Service, ServiceData, Specification
from chatbot_webservice.math import Math

expected_qos = 100.0
qos_threshold = 90.0
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


def get_specification_end_index(data, idx, specification_endpoint):
    current_idx = idx
    while data[current_idx].time < specification_endpoint:
        current_idx += 1
    return current_idx


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
                    specification_endpoint = data[start_index].time + max_recovery_time

                    if data[end_index].time < specification_endpoint:
                        end_index = get_specification_end_index(data, end_index, specification_endpoint)

                    transient_behavior_indices.append([start_index, end_index])
                    transient_behavior_endpoint = data[end_index].time

    return transient_behavior_indices


def compute_expected_integral(complete_data, start_idx, end_idx):
    # create numpy arrays
    data = complete_data[start_idx:end_idx + 1]
    x_list = list(map(lambda item: float(item.time), data))
    y = np.full((end_idx + 1 - start_idx,), expected_qos)
    x = np.array(x_list)

    cum_int = integrate.cumtrapz(y, x, initial=0)
    return cum_int


def compute_actual_integral(complete_data, start_idx, end_idx):
    # turn qos values into a numpy array
    data = complete_data[start_idx:end_idx + 1]
    y_list = list(map(lambda item: float(item.qos), data))
    x_list = list(map(lambda item: float(item.time), data))
    y = np.array(y_list)
    x = np.array(x_list)

    cum_int = integrate.cumtrapz(y, x, initial=0)
    return cum_int


def compute_my_expected_integral(complete_data, start_idx, end_idx):
    # create numpy arrays
    data = complete_data[start_idx:end_idx + 1]
    x_list = list(map(lambda item: float(item.time), data))
    y_list = [expected_qos] * ((end_idx + 1) - start_idx)

    print(f'x len: {len(x_list)}, y len: {len(y_list)}')

    cum_int = Math.integrate(y_list, x_list)
    return cum_int


def compute_my_actual_integral(complete_data, start_idx, end_idx):
    data = complete_data[start_idx:end_idx + 1]
    y_list = list(map(lambda item: float(item.qos), data))
    x_list = list(map(lambda item: float(item.time), data))

    cum_int = Math.integrate(y_list, x_list)
    return cum_int


services = Service.objects.all()

service = services.get(name='Cart')
endpoint = 0
cause = 'deployment'
try:
    specification = Specification.objects.get(service_id=service.id, cause=cause)
    data = ServiceData.objects.all().filter(service_id=service.id, callId=endpoint).order_by('time')

    tb_occurrences = find_transient_behavior(data, specification)
    print(tb_occurrences)

    for transient_behavior in tb_occurrences:
        expected_integral = compute_my_expected_integral(data, transient_behavior[0], transient_behavior[1])
        actual_integral = compute_my_actual_integral(data, transient_behavior[0], transient_behavior[1])

        resilience_loss = []
        for i in range(len(expected_integral)):
            resilience_loss.append(expected_integral[i] - actual_integral[i])

        print(resilience_loss)

        if endpoint == 0:
            clip = data[transient_behavior[0]:transient_behavior[1] + 1]
            time = list(map(lambda item: float(item.time), clip))

            # print(time)

            x = np.array(time)
            y = np.array(resilience_loss)

            fig, ax = plt.subplots()
            ax.plot(x, y)
            plt.show()

except Specification.DoesNotExist:
    print(f'No specification for {service.name} in case of {cause}')
