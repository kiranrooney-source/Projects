# Projects (Hello-master)

Modern Expense Tracker and related utilities.

Features
- Web expense tracker built with Flask (`web_expense_app.py`)
- SQLite database `web_expenses.db` with recovery and restore utilities
- Scripts: `restore_data.py`, `recover_data.py`

Quick start
1. Create and activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r web_requirements.txt
   ```
3. Initialize DB (the app will auto-create tables) and start the app:
   ```powershell
   python Hello-master\web_expense_app.py
   ```
4. Open the app at: http://127.0.0.1:5001

Data recovery
- If you have CSV backups in `recovered_data/`, run:
  ```powershell
  python Hello-master\restore_data.py
  ```

Notes
- Database files and recovered CSVs are ignored by `.gitignore`.
- See `web_requirements.txt` and `requirements.txt` for dependency info.

Maintainer: KIRAN
