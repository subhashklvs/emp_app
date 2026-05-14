# 👔 Employee Management System
### Built with Flask + SQLite + Bootstrap 5

---

## ⚙️ Setup

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```
> No MySQL/mysqlclient needed — SQLite is built into Python.

### Step 2 — Run
```bash
python app.py
```
`company.db` is auto-created on first run. Open: **http://127.0.0.1:5000**

---

## 🔗 Routes

| Route            | Method   | Description         |
|------------------|----------|---------------------|
| `/`              | GET/POST | Login               |
| `/register`      | GET/POST | Register            |
| `/forgot`        | GET/POST | Forgot password     |
| `/reset/<token>` | GET/POST | Reset password      |
| `/dashboard`     | GET      | Dashboard           |
| `/add`           | GET/POST | Add employee        |
| `/view`          | GET      | View employees      |
| `/edit/<eid>`    | GET      | Edit employee form  |
| `/update`        | POST     | Save employee edit  |
| `/delete/<eid>`  | POST     | Delete employee     |
| `/contact`       | GET/POST | Contact form        |
| `/logout`        | GET      | Logout              |

---

## 🗄️ MySQL → SQLite Changes

| | MySQL | SQLite |
|---|---|---|
| Driver | `mysql.connector` | Built-in `sqlite3` |
| Placeholders | `%s` | `?` |
| Auto increment | `AUTO_INCREMENT` | `AUTOINCREMENT` |
| Config | host/user/password | `.db` file only |
| Setup | MySQL server needed | Zero setup |
