import json
import os
import re
from collections import defaultdict

import gymnasium as gym

from minari import list_remote_datasets
from minari.dataset.minari_dataset import parse_dataset_id
from minari.storage.hosting import find_highest_remote_version


filtered_datasets = defaultdict(defaultdict)
all_remote_datasets = list_remote_datasets()

for dataset_id in all_remote_datasets.keys():

    env_name, dataset_name, version = parse_dataset_id(dataset_id)

    if dataset_name not in filtered_datasets[env_name]:
        max_version = find_highest_remote_version(env_name, dataset_name)
        max_version_dataset_id = "-".join([env_name, dataset_name, f"v{max_version}"])
        filtered_datasets[env_name][dataset_name] = all_remote_datasets[
            max_version_dataset_id
        ]

for env_name, datasets in filtered_datasets.items():
    for i, (dataset_name, dataset_spec) in enumerate(datasets.items()):
        if i == 0:
            related_pages_meta = "firstpage:\n"
        elif i == len(datasets) - 1:
            related_pages_meta = "lastpage:\n"
        else:
            related_pages_meta = ""

        # Dataset Specs
        dataset_id = dataset_spec["dataset_id"]
        total_timesteps = dataset_spec["total_steps"]
        total_episodes = dataset_spec["total_episodes"]
        flatten_observations = dataset_spec["flatten_observation"]
        flatten_actions = dataset_spec["flatten_action"]
        author = dataset_spec["author"]
        email = dataset_spec["author_email"]
        algo_name = dataset_spec["algorithm_name"]

        # Environment Specs
        env_spec = json.loads(dataset_spec["env_spec"])
        env_id = env_spec["id"]
        env = gym.make(env_id)

        action_space_table = env.action_space.__repr__().replace("\n", "")
        observation_space_table = env.observation_space.__repr__().replace("\n", "")

        env_page = f"""---
autogenerated:
title: {dataset_name.title()}
{related_pages_meta}---
# {dataset_name.title()}

## Dataset Specs

|    |    |
|----|----|
|Total Timesteps| `{total_timesteps}`|
|Total Episodes | `{total_episodes}` |
|Flatten Observations | `{flatten_observations}`|
|Flatten Actions      | `{flatten_actions}`     |
| Algorithm           | `{algo_name}`           |
| Author              | `{author}`              |
| Email               | `{email}`               |
| download            | `minari.download_dataset("{dataset_id}")` |


## Environment Specs

|    |    |
|----|----|
|ID| `{env_id}`|
| Action Space | `{re.sub(' +', ' ', action_space_table)}` |
| Observation Space | `{re.sub(' +', ' ', observation_space_table)}` |

"""

        env_md_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "datasets",
            env_name,
            dataset_name + ".md",
        )
        file = open(env_md_path, "w", encoding="utf-8")
        file.write(env_page)
        file.close()
