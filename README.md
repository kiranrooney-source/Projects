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

---

## 🚀 Usage

- Run the Flask app locally:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  pip install -r web_requirements.txt
  python Hello-master\web_expense_app.py
  ```
  Open the app at: `http://127.0.0.1:5001`

- Restore data from CSV backups (if available):
  ```powershell
  python Hello-master\restore_data.py
  ```

## 🧪 Testing

- There are no formal tests included, but you can run a quick smoke test by:
  1. Visiting `/` and ensuring the dashboard loads.
  2. Hitting endpoints like `/get_category_data`, `/get_expenses_by_date`, `/get_monthly_data` to confirm JSON responses.
  3. Performing an add/delete expense cycle using `/add_expense` and `/delete_expense/<id>`.

## 🛠 Development & Contribution

Contributions are welcome! Please follow these guidelines:

1. Fork the repository and create a feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```
2. Make your changes and add tests where appropriate.
3. Keep code style consistent (use black/flake8 if available) and update docs.
4. Commit your changes with a clear message and push your branch:
   ```bash
   git add <files>
   git commit -m "Describe your change"
   git push origin feature/my-feature
   ```
5. Open a Pull Request describing the change and any testing instructions.

### Development workflow
- Create small, focused PRs and include screenshots or examples for UI changes.
- Tag maintainers for review if needed.

## 🐞 Reporting Issues

Please file issues on GitHub with a clear title, steps to reproduce, expected vs actual behavior, and any relevant logs/screenshots.

## 🧹 Code Formatting & Linting

- Recommended tools:
  - `black` for formatting
  - `flake8` for linting

## 📜 License

This project is licensed under the MIT License — see the `LICENSE` file for details.

Maintainer: KIRAN
