import csv

def get_data_from_csv(device):
    path = ".\\data2.csv"
    reader = csv.reader(open(path, newline=''), delimiter=",")
    dataset= []
    i = 0
    for row in reader:
        for i in range(len(row)):
            if row[i] == device:
                keep = i
        dataset.append(row[keep])

    return dataset
