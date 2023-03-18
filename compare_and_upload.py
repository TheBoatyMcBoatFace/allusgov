import os
import json
from github import Github

# Compare Data
def compare_data(data_path, agency_name):
    def make_hashable(obj):
        if isinstance(obj, (tuple, list)):
            return tuple(make_hashable(e) for e in obj)
        if isinstance(obj, dict):
            return frozenset((k, make_hashable(v)) for k, v in obj.items())
        return obj

    with open(data_path, 'r') as f:
        new_data = json.load(f)

    previous_data_path = f"prev_data/{agency_name.lower()}.json"
    if os.path.exists(previous_data_path):
        with open(previous_data_path, 'r') as f:
            previous_data = json.load(f)
    else:
        previous_data = []

    # Convert the inner dictionaries to frozensets
    new_data_set = set(make_hashable(entry) for entry in new_data)
    previous_data_set = set(make_hashable(entry) for entry in previous_data)

    added_entries = new_data_set - previous_data_set
    removed_entries = previous_data_set - new_data_set

    # Calculate the symmetric difference and union
    symmetric_difference = new_data_set.symmetric_difference(previous_data_set)
    union = new_data_set.union(previous_data_set)

    # Calculate the percentage of changes
    percentage_changed = (len(symmetric_difference) / len(union)) * 100

    print(f"Percentage of changes: {percentage_changed}%")
    print(f"Added entries: {len(added_entries)}")
    print(f"Removed entries: {len(removed_entries)}")

    # Update the previous data file
    with open(previous_data_path, 'w') as f:
        json.dump(new_data, f, indent=4)


# End Compare Data

if __name__ == "__main__":
    agency_name = os.environ["AGENCY_NAME"]
    agency_data_path = os.environ["AGENCY_DATA_PATH"]
    compare_data(agency_data_path, agency_name)

