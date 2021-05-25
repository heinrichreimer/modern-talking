[![CI](https://img.shields.io/github/workflow/status/heinrichreimer/modern-talking/CI?style=flat-square)](https://github.com/heinrichreimer/modern-talking/actions?query=workflow%3A"CI")
[![Code coverage](https://img.shields.io/codecov/c/github/heinrichreimer/modern-talking?style=flat-square)](https://codecov.io/github/heinrichreimer/modern-talking/)
[![Issues](https://img.shields.io/github/issues/heinrichreimer/modern-talking?style=flat-square)](https://github.com/heinrichreimer/modern-talking/issues)
[![Commit activity](https://img.shields.io/github/commit-activity/m/heinrichreimer/modern-talking?style=flat-square)](https://github.com/heinrichreimer/modern-talking/commits)
[![License](https://img.shields.io/github/license/heinrichreimer/modern-talking?style=flat-square)](LICENSE)

# 🗣️ modern-talking

Modern Talking: Key-Point Analysis using Modern Natural Language Processing

Participation at the [Quantitative Summarization – Key Point Analysis Shared Task](https://2021.argmining.org/shared_task_ibm.html#ibm) ([data on GitHub](https://github.com/ibm/KPA_2021_shared_task)).

## Usage

### Installation

First, install [Python 3](https://python.org/downloads/), [pipx](https://pipxproject.github.io/pipx/installation/#install-pipx), and [Pipenv](https://pipenv.pypa.io/en/latest/install/#isolated-installation-of-pipenv-with-pipx).
Then install dependencies (may take a while):

```shell script
pipenv install
```

### Run a matcher pipeline

Each matcher and metric has a unique name. (Names can be listed with `pipenv run python main.py matchers` and `pipenv run python main.py metrics`.)
You can then run a pipeline, i.e., train and evaluate a matcher:

```shell script
pipenv run python main.py traineval [MATCHER] [METRIC]
```

This will automatically download all datasets, train the matcher on the train set and evaluate the metric for predicted labels on the dev set.
Predicted labels are also saved to `data/out/predictions-[METRIC]-[MATCHER].json` in JSON format as described in the [shared task documentation](https://github.com/ibm/KPA_2021_shared_task#track-1---key-point-matching).

### Manual evaluation

Evaluate predicted matches in JSON format:

```shell script
pipenv run python modern_talking/evaluation/track_1_kp_matching.py data/ data/out/predictions-[METRIC]-[MATCHER].json
```

Replace `data/out/predictions-[METRIC]-[MATCHER].json` with the path to a file containing predicted matches in JSON format as described in the [shared task documentation](https://github.com/ibm/KPA_2021_shared_task#track-1---key-point-matching).

### Testing

Run all unit tests:

```shell script
pipenv run pytest
```

## License

This repository is licensed under the [MIT License](LICENSE).
It includes [evaluation code](https://github.com/IBM/KPA_2021_shared_task/blob/771caa1519df4e26127ad37cffe8d5940af3b2da/code/track_1_kp_matching.py) from the shared tasks organizers, licensed under the [Apache License 2.0](https://github.com/IBM/KPA_2021_shared_task/blob/771caa1519df4e26127ad37cffe8d5940af3b2da/LICENSE).
