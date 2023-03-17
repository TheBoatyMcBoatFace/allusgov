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

def compare_data(agency_data_path, agency_name):
    # Load the new data
    with open(agency_data_path, "r") as file:
        new_data = json.load(file)

    # Load the last committed data
    repo = git.Repo(search_parent_directories=True)
    last_commit = repo.head.commit
    last_commit_data = last_commit.tree[agency_data_path].data_stream.read().decode("utf-8")
    last_data = json.loads(last_commit_data)

    # Convert the data to sets of tuples
    new_data_set = set(tuple(entry.items()) for entry in new_data)
    last_data_set = set(tuple(entry.items()) for entry in last_data)

    # Calculate the symmetric difference and union
    symmetric_difference = new_data_set.symmetric_difference(last_data_set)
    union = new_data_set.union(last_data_set)

    # Calculate the percentage of changes
    percentage_changed = (len(symmetric_difference) / len(union)) * 100


    # Initialize the Github client
    g = Github(os.environ["GITHUB_TOKEN"])
    repo_name = os.environ["REPO"]

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
    commit_sha = repo.head.commit.hexsha
    apply_label(g, repo_name, commit_sha, label_name)

if __name__ == "__main__":
    agency_name = os.environ["AGENCY_NAME"]
    agency_data_path = os.environ["AGENCY_DATA_PATH"]
    compare_data(agency_data_path, agency_name)
