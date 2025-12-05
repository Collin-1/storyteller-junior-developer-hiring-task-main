# Setup Instructions

## Prerequisites
- Python 3.8 or higher

## Installation

1. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**
   
   On Windows (PowerShell):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   On Windows (Command Prompt):
   ```cmd
   .\venv\Scripts\activate.bat
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Story Builder

To generate a story pack using the default configuration:

```bash
python scripts/build_story.py --weights weights.example.json
```

You can also specify custom input and output paths:

```bash
python scripts/build_story.py --input data/match_events.json --output out/story.json --weights weights.example.json
```

If you don't provide the `--weights` argument, the script will look for `weights.example.json` or prompt you for a path.

## Running Tests

To run all tests to verify the project invariants:

```bash
pytest
```

To run tests with verbose output:

```bash
pytest -v
```

## Deactivating the Virtual Environment

When you're done, deactivate the virtual environment:
```bash
deactivate
```
