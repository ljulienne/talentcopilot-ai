# Integration Guide — Release 7.1.6

## Required base

The installer accepts only this official base commit:

`850dcb3d7284f46007affeb921b753c77020ed2c`

## Installation

Run `install_release_7_1_6.py` from the extracted package. The installer:

1. verifies the repository and exact Git HEAD;
2. refuses a dirty working tree except for known runtime artifacts;
3. copies the release payload;
4. compiles the modified Python module;
5. runs the targeted narrative regression suite.

After installation, run the complete test suite before committing:

```bash
python -m pytest -q
```

Expected commit message:

`Release 7.1.6 - Narrative Compression and Semantic Variation`
