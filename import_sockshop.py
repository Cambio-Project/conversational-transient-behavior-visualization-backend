import csv
import numpy as np

from chatbot_webservice.models import Service, ServiceData

SCENARIO = 0
SYSTEM = 'SockShop'

file_path = 'sockshop.csv'
percentile = 90
counter = 0

services = {
    'home': 'Frontend',
    'catalogue': 'Frontend',
    'showDetails': 'Frontend',
    'basket': 'Frontend',
    'viewOrdersPage': 'Frontend',
    'login': 'User',
    'getCustomer': 'User',
    'getCard': 'User',
    'getAddress': 'User',
    'getCatalogue': 'Catalogue',
    'catalogueSize': 'Catalogue',
    'cataloguePage': 'Catalogue',
    'getItem': 'Catalogue',
    'getRelated': 'Catalogue',
    'tags': 'Catalogue',
    'getCart': 'Cart',
    'addToCart': 'Cart',
    'createOrder': 'Order',
    'getOrders': 'Order'
}

callIds = {
    'home': 0,
    'catalogue': 1,
    'showDetails': 2,
    'basket': 3,
    'viewOrdersPage': 4,
    'login': 0,
    'getCustomer': 1,
    'getCard': 2,
    'getAddress': 3,
    'getCatalogue': 0,
    'catalogueSize': 1,
    'cataloguePage': 2,
    'getItem': 3,
    'getRelated': 4,
    'tags': 5,
    'getCart': 0,
    'addToCart': 1,
    'createOrder': 0,
    'getOrders': 1
}


def compute_expected_qos(k):
    values = [
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        []
    ]
    result = []

    with open(file_path, newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        next(reader, None)

        for i, row in enumerate(reader):
            for col in range(1, 20):
                values[col - 1].append(float(row[col]))

    for value in values:
        array = np.array(value)
        result.append(np.percentile(array, k))

    return result


specifiedResponseTimes = compute_expected_qos(percentile)

with open(file_path, newline='') as csv_file:
    data_reader = csv.reader(csv_file, delimiter=',')
    headers = next(data_reader)
    endpoints = headers[1:]

    for row in data_reader:
        counter += 1
        time = float(row.pop(0))

        for i, col in enumerate(row):
            uri = endpoints[i]
            service_name = services[uri]
            call_id = callIds[uri]
            service = Service.objects.get(name=service_name)

            response_time = float(col)
            exp_response_time = specifiedResponseTimes[i]

            if response_time == 0.0:
                qos = 100
            else:
                qos = round((exp_response_time / response_time) * 100)
                if qos > 100:
                    qos = 100

            ServiceData.objects.create(
                system=SYSTEM,
                scenario=SCENARIO,
                service=service,
                time=time,
                callId=call_id,
                uri=uri,
                qos=qos
            )

        if counter % 10 == 0:
            print(counter, end='\r')
