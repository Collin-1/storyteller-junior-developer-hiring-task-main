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

```bash
python scripts/build_story.py
```

The script will prompt you for the weights file location if not found automatically.

## Running Tests

```bash
pytest
```

## Deactivating the Virtual Environment

When you're done, deactivate the virtual environment:
```bash
deactivate
```
