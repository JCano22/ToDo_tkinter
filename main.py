import tkinter as tk
from tkinter import ttk
import sqlite3
import os

def main():
    root = tk.Tk()
    root.title("To Do List")
    root.geometry("400x300") #to make the window more "notebook" style

    mainframe = ttk.Frame(root, padding = 10)
    mainframe.grid(column = 0, row = 0, sticky = ("N, S, E, W"))

    tasks_frame = ttk.Frame(mainframe)
    tasks_frame.grid(row = 0, column = 0, columnspan = 3, sticky = ("N, S, E, W"), pady = (0, 10))

    root.columnconfigure(0, weight = 1)
    root.rowconfigure(0, weight = 1)
    mainframe.rowconfigure(0, weight=1)
    mainframe.columnconfigure(0, weight=1)
    tasks_frame.columnconfigure(0, weight = 1)

    # We'll keep references to each task so we can delete them later
    # Each element is: {"var": BooleanVar, "check": Checkbutton}
    tasks = []

    #new entry
    new_task_var = tk.StringVar()
    entry = ttk.Entry(mainframe, textvariable = new_task_var)
    entry.grid(row = 1, column = 0, sticky = "ew", padx = (0, 5))

    def add_task(*args):
        text = new_task_var.get().strip()
        if not text:
            return

        # One BooleanVar + one Checkbutton per task
        var = tk.BooleanVar(value=False)
        check = ttk.Checkbutton(tasks_frame, text=text, variable=var)
        check.grid(row=len(tasks), column=0, sticky="w")

        tasks.append({"var": var, "check": check})
        new_task_var.set("")
    
    def delete_selected():
        # Remove all tasks whose checkbox is checked
        # Go backwards so indices stay valid as we pop
        for i in reversed(range(len(tasks))):
            task = tasks[i]
            if task["var"].get():  # if checked
                task["check"].destroy()  # remove widget from UI
                tasks.pop(i)             # remove from list in memory

        # Re-pack remaining tasks so rows are compact (0,1,2,...)
        for row, task in enumerate(tasks):
            task["check"].grid(row=row, column=0, sticky="w")

    
    # === Buttons =============================================================
    add_button = ttk.Button(mainframe, text="Add", command=add_task)
    add_button.grid(row=1, column=1, sticky="ew")

    delete_button = ttk.Button(mainframe, text="Mark 'Completed'", command=delete_selected)
    delete_button.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 0))

    # === Misc ================================================================
    entry.bind("<Return>", add_task)  # Enter key adds task
    entry.focus()                     # cursor on entry

    root.mainloop()

if __name__ == "__main__":
    main()



        
    