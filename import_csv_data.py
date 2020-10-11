import csv

from chatbot_webservice.models import Service, Dependency, ServiceData

file_path = 'results_monkey_nopattern.csv'

specifiedResponseTime = 5

counter = 0

with open(file_path, newline='') as csv_file:
    data_reader = csv.reader(csv_file, delimiter=',')
    next(data_reader, None) # skip header
    for row in data_reader:
        counter += 1

        service_name = row[2]
        service = Service.objects.get(name=service_name)

        avgResponseTime = row[8]

        if float(avgResponseTime) == 0.0:
            qos = 100
        else:
            qos = round((float(specifiedResponseTime) / float(avgResponseTime)) * 100)

        ServiceData.objects.create(
            service=service,
            time=row[0],
            callId=row[1],
            uri=row[4],
            successfulTransactions=row[5],
            failedTransactions=row[6],
            droppedTransactions=row[7],
            qos=qos
        )

        print(counter,  end='\r')
