import csv
import json
import os
import re


def scale(title):
    files = os.listdir(f"../results/{title}")
    try:
        os.mkdir(f"../results/computed_{title}")
    finally:
        dic = {
            "ch1": [],
            "ch2": [],
            "ch3": []
        }
        time = []
        regex = re.compile(r"(-?\d+\.\d{2})\d+(e[-|+]\d{2})")

        with open(f"../results/{title}/{files[0]}", 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            length = sum(1 for _ in csv_reader) / 200

        with open(f"../results/{title}/{files[0]}", 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            with open(f"../results/computed_{title}/time.json", 'w') as new_file:
                for i, line in enumerate(csv_reader):
                    if i % length == 0:
                        time.append(regex.sub(r'\1\2', line[0]))
                json.dump({'time': time}, new_file)

        for file in files:
            f, _ = os.path.splitext(file)
            with open(f"../results/{title}/{file}", 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                with open(f"../results/computed_{title}/{f}.json", 'w') as new_file:
                    # csv_writer = csv.writer(new_file)
                    for i, line in enumerate(csv_reader):
                        if i % length == 0:
                            # csv_writer.writerow(line),
                            # dic["time"].append(line[0])
                            dic["ch1"].append(regex.sub(r'\1\2', line[1]))
                            dic["ch2"].append(regex.sub(r'\1\2', line[2]))
                            dic["ch3"].append(regex.sub(r'\1\2', line[3]))
                    json.dump(dic, new_file)
                    dic = {"ch1": [], "ch2": [], "ch3": []}
