import csv
import random
# resources: 
# https://docs.python.org/3/library/random.html?highlight=random#module-random
# https://docs.python.org/3/library/csv.html?highlight=csv#module-csv

file_in = "olist_customers_dataset.csv" # input file name
file_out = "sample_small_olist_customers_dataset.csv" # output file name
k = 10000 # number of rows sampled from population
rows = []

with open(file_in, newline = '') as fl:
    reader = csv.reader(fl)

    for row in reader:
        rows.append(row)

sample = random.sample(rows[1:], k)

with open(file_out, 'w', newline='') as fl:
    writer = csv.writer(fl)
    writer.writerow(rows[0])
    for row in sample:
        writer.writerow(row)

print("Finished writing file")

