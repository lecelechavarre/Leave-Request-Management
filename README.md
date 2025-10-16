Leave Request Manager v10
=========================

This release implements:
- SQLAlchemy ORM (models + DB file: data/leave_manager.db)
- Alembic migration stubs (alembic/*) to support future migrations
- QAbstractItemModel-backed table model (scales better than QStandardItemModel)
- QSortFilterProxyModel for searching/filtering/sorting
- CSV import UI with preview + bulk insert
- Audit log table (audits) capturing who/when/what changes (create/update/delete)
- Passlib (bcrypt) for secure password hashing
- PyInstaller spec stub for packaging

How to run
1. Create venv:
   python -m venv .venv
2. Activate venv and install:
   pip install -r requirements.txt
3. Run:
   python main.py

Default users created on first run:
- admin / admin (role=admin)
- employee / employee (role=employee)

Notes:
- Alembic is included as a stub. To use migrations, configure alembic.ini and run alembic commands.
- Packaging: use the provided spec (pyinstaller.spec) to build a single-file executable.

If you encounter errors, paste the full traceback and I'll patch quickly.
