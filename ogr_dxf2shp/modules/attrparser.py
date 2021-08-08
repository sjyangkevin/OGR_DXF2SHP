import csv

def parse_attribute_file(file_path):

    columns = []
    data = []

    with open(file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            columns = [str(c) for c in list(row.keys())]
            data.append(row)
        
    return columns, data