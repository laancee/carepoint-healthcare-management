# CarePoint — Health Management Web App

A beginner-friendly Flask + MongoDB Atlas clinic record management project. The responsive Bootstrap interface works in modern phone and PC browsers.

## Included features

- Staff registration and login
- Password hashing (passwords are not stored as plain text)
- Dashboard with total patient count and recently updated records
- Create, view, edit, delete, and search patient records
- MongoDB Atlas document database (NoSQL)
- Responsive layout using Bootstrap 5
- Form validation and delete confirmation

> **Important:** This is an educational starter project, not a certified clinical system. Use fictional records for school demonstrations. Do not store real patient/health information until a qualified team has added security, privacy, access control, audit logs, backups, and legal compliance controls. The sample registration page is open to anyone who can reach it; disable or restrict it before real use.

## 1. Requirements

- Python 3.10 or newer
- A MongoDB Atlas account
- Internet connection for Bootstrap CDN and Atlas

## 2. Set up MongoDB Atlas

1. Create a cluster in MongoDB Atlas.
2. Under **Database Access**, create a database user and password.
3. Under **Network Access**, add your current IP for local testing. For deployment, configure the narrowest network access supported by your hosting provider; avoid opening access to everyone unless you understand the risk.
4. Open **Connect → Drivers** and copy the Python connection string.
5. Replace the username and password placeholders in the connection string. URL-encode special characters in the password if needed.
6. The database and collections are created automatically when the app first writes data.

## 3. Install and run locally

Open a terminal in this project folder.

### Windows PowerShell

```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `MONGO_URI`, `MONGO_DB_NAME`, and a strong random `SECRET_KEY`.

If PowerShell blocks activation, you can use Command Prompt instead:

```bat
.venv\\Scripts\\activate.bat
```

Then run:

```powershell
python app.py
```

Open `http://127.0.0.1:5000` in your browser. Create a staff account, sign in, and add fictional patient records.

To test on your phone while it is connected to the same Wi-Fi as your PC, run Flask with `app.run(host="0.0.0.0", debug=True)` temporarily, find your PC's local IPv4 address using `ipconfig`, then visit `http://YOUR-PC-IP:5000` on your phone. Keep this development-only and do not expose the debug server to the public internet.

## 4. Deploy online

One common option is a Python web host that supports Flask and Gunicorn.

1. Upload the project to a private Git repository. **Never commit `.env`**.
2. Create a new web service from the repository on your chosen host.
3. Build/install command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add environment variables in the host dashboard:
   - `MONGO_URI` = your Atlas connection string
   - `MONGO_DB_NAME` = `healthcare_management`
   - `SECRET_KEY` = a long, random secret generated privately
6. Ensure Atlas network access allows the host to connect. Follow your host's current outbound IP guidance.
7. Deploy, open the provided HTTPS URL on your PC and phone, and test login plus patient CRUD.
8. After creating authorized accounts, disable public registration by removing the `/register` route and its link or replace it with an invitation/admin-only workflow.

Hosting dashboards change over time, so follow the current instructions for your selected provider. Do not use Flask's development server or `debug=True` in production.

## 5. MongoDB document example

A patient document in the `patients` collection looks like:

```json
{
  "name": "Sample Patient",
  "age": 28,
  "sex": "Prefer not to say",
  "phone": "000-000-0000",
  "email": "sample@example.com",
  "blood_type": "Unknown",
  "allergies": "Not recorded",
  "medical_notes": "Fictional record for a class demo"
}
```

The `users` collection stores a username and a Werkzeug password hash, not the original password.

## 6. Suggested improvements for a final project

- Add role-based access (admin, doctor, receptionist)
- Add CSRF protection to forms
- Add audit logs for record access and changes
- Add pagination and more robust validation
- Add password reset and login rate limiting
- Add automated backups and a privacy notice
- Add appointment scheduling and consultation history

## Troubleshooting

- **Database connection issue:** Check the URI, Atlas database username/password, IP access list, and internet connection.
- **`ModuleNotFoundError`:** Activate the virtual environment and run `pip install -r requirements.txt`.
- **Login works locally but not after redeploy:** Confirm environment variables are set in the hosting dashboard and redeploy.
- **Bootstrap styles do not load:** Check internet access; this starter uses the Bootstrap CDN.
