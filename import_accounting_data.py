import csv

from chatbot_webservice.models import Service, ServiceData

# Change these variables to declare the data that you want to import (scenario 0/1/2)
SCENARIO = 0
FILE_PATH = 'data/accounting_0.csv'

counter = 0
SYSTEM = 'accounting-system'

with open(FILE_PATH, newline='') as csv_file:
    data_reader = csv.reader(csv_file, delimiter=',')

    for row in data_reader:
        counter += 1

        time = row[0]
        call_id = row[1]
        service_name = row[2]
        uri = row[3]
        qos = float(row[4])

        service = Service.objects.get(name=service_name, system=SYSTEM, scenario=SCENARIO)

        ServiceData.objects.create(
            service=service,
            time=time,
            callId=call_id,
            uri=uri,
            qos=qos
        )

        if counter % 50 == 0:
            print(counter,  end='\r')
