"""
Recall Words - Tkinter + SQLite
Converted from a Flask app into an offline desktop app using Tkinter and SQLite.

Usage:
    python3 recall_app.py

This will create (if not exists) a SQLite database file named recall_words.db
in the same directory as this script.
"""

from db import *
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


class RecallApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("tkvocab")
        self.geometry("700x500")
        self.create_widgets()
        self.show_home()

    def create_widgets(self):
        # Menu / Navigation
        menu_frame = ttk.Frame(self)
        menu_frame.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(menu_frame, text="Home", command=self.show_home).pack(
            side=tk.LEFT, padx=4, pady=4
        )
        ttk.Button(menu_frame, text="Add", command=self.show_add).pack(
            side=tk.LEFT, padx=4, pady=4
        )
        ttk.Button(menu_frame, text="Browse", command=self.show_browse).pack(
            side=tk.LEFT, padx=4, pady=4
        )
        ttk.Button(menu_frame, text="Review", command=self.show_review).pack(
            side=tk.LEFT, padx=4, pady=4
        )

        # Main content area
        self.content = ttk.Frame(self)
        self.content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def show_home(self):
        self.clear_content()
        row = get_review_word_row()
        if row is None:
            lbl = ttk.Label(
                self.content,
                text="No words to review. Congrats 🎉",
                font=("TkDefaultFont", 16),
            )
            lbl.pack(pady=20)
            ttk.Label(
                self.content, text="Add new words to start spaced repetition."
            ).pack()
        else:
            ttk.Label(
                self.content, text="Next review word:", font=("TkDefaultFont", 14)
            ).pack(anchor=tk.W)
            ttk.Label(
                self.content, text=row["word"], font=("TkDefaultFont", 20, "bold")
            ).pack(pady=6)
            ttk.Label(self.content, text=row["comment"], wraplength=650).pack(pady=6)
            ttk.Label(self.content, text=f"Interval days: {row['interval_days']}").pack(
                pady=4
            )
            ttk.Label(
                self.content, text=f"Next review date: {row['next_review_date']}"
            ).pack(pady=4)
            ttk.Button(
                self.content, text="Go to Review", command=self.show_review
            ).pack(pady=10)

    def show_add(self):
        self.clear_content()
        ttk.Label(self.content, text="Add a new word", font=("TkDefaultFont", 16)).pack(
            anchor=tk.W
        )

        form = ttk.Frame(self.content)
        form.pack(fill=tk.X, pady=10)

        ttk.Label(form, text="Word:").grid(row=0, column=0, sticky=tk.W, pady=4)
        word_entry = ttk.Entry(form)
        word_entry.grid(row=0, column=1, sticky=tk.EW, pady=4)
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Comment / Definition:").grid(
            row=1, column=0, sticky=tk.NW, pady=4
        )
        comment_txt = scrolledtext.ScrolledText(form, height=6, wrap=tk.WORD)
        comment_txt.grid(row=1, column=1, sticky=tk.EW, pady=4)

        def submit():
            word = word_entry.get().strip()
            comment = comment_txt.get("1.0", tk.END).strip()
            if not word:
                messagebox.showerror("Validation", "Word is required.")
                return
            ok, err = add_word(word, comment)
            if not ok:
                messagebox.showerror("Error", f"Could not add word: {err}")
            else:
                messagebox.showinfo("Added", f"Added '{word}'")
                word_entry.delete(0, tk.END)
                comment_txt.delete("1.0", tk.END)

        ttk.Button(form, text="Add Word", command=submit).grid(
            row=2, column=1, sticky=tk.E, pady=8
        )

    def show_browse(self):
        self.clear_content()
        ttk.Label(self.content, text="All words", font=("TkDefaultFont", 16)).pack(
            anchor=tk.W
        )
        cols = ("word", "comment", "interval_days", "next_review_date", "created_at")
        tree = ttk.Treeview(self.content, columns=cols, show="headings", height=15)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120, anchor=tk.W)
        tree.pack(fill=tk.BOTH, expand=True, pady=8)

        for row in get_all_words():
            tree.insert(
                "",
                tk.END,
                values=(
                    row["word"],
                    row["comment"],
                    row["interval_days"],
                    row["next_review_date"],
                    row["created_at"],
                ),
            )

        def delete_selected():
            sel = tree.selection()
            if not sel:
                return
            item = tree.item(sel[0])
            word = item["values"][0]
            delete_word(word)
            tree.delete(sel[0])

        ttk.Button(self.content, text="Delete Selected", command=delete_selected).pack(
            anchor=tk.E
        )

    def show_review(self):
        self.clear_content()
        row = get_review_word_row()
        if row is None:
            ttk.Label(
                self.content,
                text="No words to review right now. Great job!",
                font=("TkDefaultFont", 16),
            ).pack(pady=20)
            return

        interval = row["interval_days"]
        all_interval_days = (1, interval, interval * 2, interval * 4)

        ttk.Label(self.content, text="Review", font=("TkDefaultFont", 16)).pack(
            anchor=tk.W
        )
        ttk.Label(
            self.content, text=row["word"], font=("TkDefaultFont", 20, "bold")
        ).pack(pady=6)
        ttk.Label(self.content, text=row["comment"], wraplength=650).pack(pady=6)
        btn_frame = ttk.Frame(self.content)
        btn_frame.pack(pady=8)

        def make_update(days):
            def _():
                update_review_date(row["word"], days)
                messagebox.showinfo(
                    "Updated", f"Next review scheduled in {days} day(s)."
                )
                self.show_home()

            return _

        for d in all_interval_days:
            ttk.Button(btn_frame, text=f"{d} day(s)", command=make_update(d)).pack(
                side=tk.LEFT, padx=4
            )


if __name__ == "__main__":
    init_db()
    app = RecallApp()
    app.mainloop()
