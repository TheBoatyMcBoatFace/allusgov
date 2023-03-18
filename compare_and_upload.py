import os
import json
import git
from git import Repo
from github import Github

def apply_label(g, repo_name, commit_sha, label_name):
    repo = g.get_repo(repo_name)
    labels = [repo.get_label(label_name)]
    commit = repo.get_commit(sha=commit_sha)
    commit.create_status(
        state="success",
        description=f"Applied label: {label_name}",
        context=f"Label: {label_name}",
        target_url="",
    )
    commit.set_labels(*labels)

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

    # Initialize the Github client
    g = Github(os.environ["GITHUB_TOKEN"])
    repo_name = os.environ["REPO"]
    repo = g.get_repo(repo_name)  # Add this line to get the repo object

    # Apply the appropriate labels based on the changes
    if percentage_changed == 0:
        label_name = "No Changes"
    elif percentage_changed <= 10:
        label_name = "Tiny Changes"
    elif percentage_changed <= 30:
        label_name = "Medium Changes"
    elif percentage_changed <= 50:
        label_name = "Big Changes"
    else:
        label_name = "Major Changes"

    # Apply the label to the current commit
    commit_sha = repo.get_commits()[0].sha
    apply_label(g, repo_name, commit_sha, label_name)


# End Compare Data


if __name__ == "__main__":
    agency_name = os.environ["AGENCY_NAME"]
    agency_data_path = os.environ["AGENCY_DATA_PATH"]
    compare_data(agency_data_path, agency_name)


