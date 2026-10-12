# CI/CD pipeline

The pipeline is defined in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) and runs on GitHub Actions.

## When it runs

- on every **push** to any branch
- on every **pull request**
- on demand, from the Actions tab (**Run workflow**)

A newer push to the same branch cancels the older run, so the queue stays short.

## What it does

| Job | Step | What it proves |
|---|---|---|
| `test` | Set up Python 3.11 with the pip cache | The project runs on the Python version used in the container |
| `test` | Install `requirements.txt`, `pytest` and the CPU build of PyTorch | A clean machine can install the project |
| `test` | `pytest tests/test_assignment_a2.py -v` | The 14 assignment test cases pass (see [`TEST_CASES.md`](TEST_CASES.md)) |
| `test` | `pytest -v` | The whole test suite passes |
| `docker` | `docker build` | The image builds from a clean checkout, including the React portal |
| `docker` | Import check inside the image | The server and every dependency it loads at start-up are present |
| `docker` | `id -u` check | The container does not run as root |
| `docker` | `--help` | The server starts without crashing |

## Reading the result

- A green tick beside a commit or pull request means every step passed.
- A red cross means a step failed. Open the run, then the failed step, to read the log.
- The badge at the top of the README shows the state of the latest run on `main`.

## Continuous delivery

The `docker` job builds the deployment image on every change. Model checkpoints are mounted at run time and are never
committed or baked into the image ([`DEPLOYMENT.md`](DEPLOYMENT.md)). Publishing the image to a registry is a later step
once a hospital deployment target is agreed.
