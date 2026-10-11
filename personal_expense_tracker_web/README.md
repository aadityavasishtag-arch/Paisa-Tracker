# PaisaTrack — Personal Expense Tracker

A beginner-friendly, responsive expense tracker web application built with **Python Flask**, **SQLite**, HTML, CSS, and JavaScript.

## Features

- Add expenses with date, category, description, and amount
- Dashboard with total recorded spending, current-month spending, transaction count, and average expense
- Monthly spending breakdown by category
- Search by description/category
- Filter by category and month
- Edit and delete expenses
- Export the current filtered results to CSV for Excel
- SQLite database persists records between runs
- Responsive layout for laptop, tablet, and phone-sized screens

## Requirements

- Python 3.10 or newer recommended
- Internet access only for loading the optional Google Fonts; the app itself runs locally

## Run on Windows

1. Extract the project ZIP.
2. Open the extracted `personal_expense_tracker_web` folder in VS Code.
3. Open the VS Code terminal in that folder.
4. Create a virtual environment (recommended):

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, you can run the app with `py -m pip` and `py app.py` without activating the environment.

5. Install dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

6. Start the app:

   ```powershell
   py app.py
   ```

7. Open the local address printed in the terminal, usually:

   `http://127.0.0.1:5000`

8. Keep the terminal running while using the application. Press `Ctrl+C` in the terminal to stop it.

## Run on macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 app.py
```

Then open `http://127.0.0.1:5000`.

## Where is my data stored?

The application creates `expenses.db` in the project folder on its first run. This file stores your expense records locally. Keep a backup of it if the records matter to you. The CSV export is useful for spreadsheet analysis, but it is not a full database backup.

## Project structure

```text
personal_expense_tracker_web/
├── app.py
├── requirements.txt
├── README.md
├── expenses.db          # created automatically on first run
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js
```

## How it works

- **Flask** serves the webpage and handles form submissions.
- **SQLite** stores expense records in a local database.
- **HTML** defines the page and forms.
- **CSS** styles the dashboard and makes it responsive.
- **JavaScript** handles edit dialogs and delete confirmation.
- **Parameterized SQL queries** are used for database operations.

## Important notes

- This is a local, single-user starter app, not a deployed multi-user financial service.
- Do not expose the Flask development server directly to the public internet.
- Before deploying publicly, add authentication, CSRF protection, production server configuration, secure secret management, backups, and HTTPS.
- The app records expenses entered by the user. It does not connect to banks or automatically import UPI transactions.
- Categories are defined in `CATEGORIES` in `app.py`; update that list and the app will use the new categories in its forms.
