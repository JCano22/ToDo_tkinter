import tkinter as tk
from tkinter import ttk
import sqlite3
import os


def main():
    # === Figure out where this script lives (for stable DB path) ===========
    # __file__  -> the path of THIS Python file (main.py)
    # abspath   -> make sure it's an absolute path
    # dirname   -> strip off "main.py", leaving just the folder
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Build the full path to the database file "todo.db" in the same folder
    db_path = os.path.join(script_dir, "todo.db")

    # === Connect to the SQLite database ====================================
    # If "todo.db" doesn't exist yet, SQLite will create it.
    conn = sqlite3.connect(db_path)

    # === Create table if it doesn't exist yet ==============================
    def init_db():
        # "with conn" = automatically commit or rollback the transaction
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    init_db()

    # === Tkinter window setup ==============================================
    root = tk.Tk()
    root.title("To Do List")
    root.geometry("400x300")  # make the window more "notebook" style

    # === Main frame (inside root) ==========================================
    mainframe = ttk.Frame(root, padding=10)
    mainframe.grid(column=0, row=0, sticky="nsew")

    # === Frame that will hold all the checkbox tasks =======================
    tasks_frame = ttk.Frame(mainframe)
    tasks_frame.grid(row=0, column=0, columnspan=3, sticky="nsew", pady=(0, 10))

    # === Grid expansion rules ==============================================
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    mainframe.rowconfigure(0, weight=1)
    mainframe.columnconfigure(0, weight=1)

    tasks_frame.columnconfigure(0, weight=1)

    # We'll keep references to each task so we can manage them
    # Each element will be: {"id": int, "var": BooleanVar, "check": Checkbutton}
    tasks = []

    # === Entry for new task ================================================
    new_task_var = tk.StringVar()
    entry = ttk.Entry(mainframe, textvariable=new_task_var)
    entry.grid(row=1, column=0, sticky="ew", padx=(0, 5))

    # === Helper: update 'completed' in DB when checkbox toggles ============
    def update_completed(task_id, is_completed):
        """
        Update the 'completed' column in the database for a given task.
        is_completed is a bool -> we store 1 (True) or 0 (False) in SQLite.
        """
        with conn:
            conn.execute(
                "UPDATE tasks SET completed = ? WHERE id = ?",
                (1 if is_completed else 0, task_id),
            )

    # === Load existing tasks from the database at startup ==================
    def load_tasks():
        # Clear current UI list (in case this is ever called more than once)
        for task in tasks:
            task["check"].destroy()
        tasks.clear()

        # Get all tasks from the DB in order of their id (oldest first)
        cursor = conn.execute(
            "SELECT id, description, completed FROM tasks ORDER BY id"
        )

        # For each row in the DB, create a checkbox in the UI
        for row_index, (task_id, desc, completed) in enumerate(cursor):
            # BooleanVar holds True/False in Tkinter, initialized from DB (0/1)
            var = tk.BooleanVar(value=bool(completed))

            # Create a Checkbutton with that text and state
            check = ttk.Checkbutton(tasks_frame, text=desc, variable=var)
            check.grid(row=row_index, column=0, sticky="w")

            # When the BooleanVar changes, we want to update the DB.
            def on_toggle(*args, task_id=task_id, v=var):
                update_completed(task_id, v.get())

            # trace_add("write", ...) means: call on_toggle whenever var changes.
            var.trace_add("write", on_toggle)

            tasks.append({"id": task_id, "var": var, "check": check})

    load_tasks()

    # === Functions for add / delete ========================================
    def add_task(*args):
        text = new_task_var.get().strip()
        if not text:
            return  # do nothing on empty input

        # 1) Insert into database (completed = 0 for new task)
        with conn:
            cursor = conn.execute(
                "INSERT INTO tasks (description, completed) VALUES (?, 0)",
                (text,),
            )
            task_id = cursor.lastrowid  # the new row's id

        # 2) Create checkbox in UI
        var = tk.BooleanVar(value=False)
        check = ttk.Checkbutton(tasks_frame, text=text, variable=var)
        check.grid(row=len(tasks), column=0, sticky="w")

        # 3) Link checkbox changes back to DB
        def on_toggle(*args, task_id=task_id, v=var):
            update_completed(task_id, v.get())

        var.trace_add("write", on_toggle)

        # 4) Save in our in-memory list
        tasks.append({"id": task_id, "var": var, "check": check})

        # 5) Clear the entry box
        new_task_var.set("")

    def delete_selected():
        """
        Right now: delete all tasks whose checkbox is checked.
        That means:
        - Remove from DB
        - Remove from UI
        - Remove from our 'tasks' list
        """
        # Go backwards so indices stay valid as we pop from the list
        for i in reversed(range(len(tasks))):
            task = tasks[i]
            if task["var"].get():  # if checkbox is checked
                # 1) Remove from DB
                with conn:
                    conn.execute("DELETE FROM tasks WHERE id = ?", (task["id"],))

                # 2) Remove from UI
                task["check"].destroy()

                # 3) Remove from our in-memory list
                tasks.pop(i)

        # Re-pack remaining tasks so their rows are compact (0, 1, 2, ...)
        for row, task in enumerate(tasks):
            task["check"].grid(row=row, column=0, sticky="w")

    # === Buttons ============================================================
    add_button = ttk.Button(mainframe, text="Add", command=add_task)
    add_button.grid(row=1, column=1, sticky="ew")

    # Note: this currently DELETES checked tasks, despite the label
    delete_button = ttk.Button(mainframe, text="Delete Checked", command=delete_selected)
    delete_button.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 0))

    # === Misc ===============================================================
    entry.bind("<Return>", add_task)  # Enter key adds task
    entry.focus()                     # cursor on entry

    # When the window is closed, close the DB connection cleanly
    def on_close():
        conn.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()


if __name__ == "__main__":
    main()
