import csv
import json
from pathlib import Path
import re

FILE = Path(__file__).parent

def scale(title):
    results_path = FILE / "results"
    test_dir = results_path / title
    computed_dir = results_path / f"computed_{title}"
    
    files = list(test_dir.iterdir())
    try:
        computed_dir.mkdir(exist_ok=True)
    finally:
        data_dict = {
            "ch1": [],
            "ch2": [],
            "ch3": []
        }
        time_data = []
        regex = re.compile(r"(-?\d+\.\d{2})\d+(e[-|+]\d{2})")

        with (test_dir / files[0].name).open('r') as csv_file:
            csv_reader = csv.reader(csv_file)
            length = sum(1 for _ in csv_reader) / 200

        with (test_dir / files[0].name).open('r') as csv_file:
            csv_reader = csv.reader(csv_file)
            with (computed_dir / "time.json").open('w') as new_file:
                for i, line in enumerate(csv_reader):
                    if i % length == 0:
                        time_data.append(regex.sub(r'\1\2', line[0]))
                json.dump({'time': time_data}, new_file)

        for file_path in files:
            stem = file_path.stem
            with file_path.open('r') as csv_file:
                csv_reader = csv.reader(csv_file)
                with (computed_dir / f"{stem}.json").open('w') as new_file:
                    # csv_writer = csv.writer(new_file)
                    for i, line in enumerate(csv_reader):
                        if i % length == 0:
                            # csv_writer.writerow(line),
                            # data_dict["time"].append(line[0])
                            data_dict["ch1"].append(regex.sub(r'\1\2', line[1]))
                            data_dict["ch2"].append(regex.sub(r'\1\2', line[2]))
                            data_dict["ch3"].append(regex.sub(r'\1\2', line[3]))
                    json.dump(data_dict, new_file)
                    data_dict = {"ch1": [], "ch2": [], "ch3": []}
