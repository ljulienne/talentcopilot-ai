import subprocess
from pathlib import Path


def main():
    repo = Path(__file__).resolve().parents[1]
    subprocess.run(["python", "-m", "pytest", "tests/stable"], cwd=repo, check=True)


if __name__ == "__main__":
    main()
