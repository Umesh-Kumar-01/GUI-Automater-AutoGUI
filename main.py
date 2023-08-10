import pathlib
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
from workflow_file import *
from datetime import datetime


class Terminal:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.scrollbar = tk.Scrollbar(text_widget.master)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text_widget.yview)
        self.text_widget.pack(fill=tk.BOTH, expand=False)

    def write(self, message, message_type="INFO"):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message_type}: {message}\n")
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.see(tk.END)


class BaseApp:
    def __init__(self, title):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.minsize(400, 300)
        self.currentDir = None
        self.currentFiles = set([])

        # Menu
        self.menuLabels = {}  # {'File':{'label':command_function, ... }, ... }
        self.menuBar = tk.Menu(self.root)
        self.add_menu_labels(master=self.menuBar, label_map={
            'File': {
                'New': self.donothing,
                'Open': self.open_new_file,
                'Save': self.donothing,
                'Save as': self.donothing,
                'Close': self.donothing,
                'separator': None,
                'Exit': self.root.quit,
            },
            'Edit': {
                'Undo': self.donothing,
                'separator': None,
                'Cut': self.donothing,
                'Copy': self.donothing,
                'Paste': self.donothing,
                'Delete': self.donothing,
                'Select All': self.donothing,
            },
            'Help': {
                'Help Index': self.donothing,
                'About...': self.donothing,
            }
        })
        self.create_layout()
        self.tabs = []
        self.add_notebook_tabs(tabs=[])
        self.plus_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.plus_tab, text='+')
        self.notebook.bind("<Button-1>", self.on_tab_button_click)

        ## Add Terminal
        self.terminal = Terminal(tk.Text(self.terminalPanel, wrap=tk.WORD, state=tk.DISABLED))
        self.terminal.write("Welcome To GUI Automation!", "INFO")

        ## Add List of files in folder
        if self.currentDir is None:
            self.open_label = ttk.Button(self.filePanel, text="Open Folder", command=self.open_folder)
            self.open_label.pack(fill=tk.BOTH, expand=True)

    def on_select(self,event):
        print("Event Triggered!")
        w = event.widget
        index = int(w.curselect()[0])
        value = w.get(index)
        print(w,index,value)
        self.open_file(value)

    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.currentDir = folder_path
            self.terminal.write(f"Opened folder {folder_path}", "INFO")
            files = os.listdir(folder_path)
            workflow_files = [file for file in files if file.endswith('.wkfw')]

            self.updateFileList(workflow_files)

    def updateFileList(self, files):
        self.currentFiles.update(files)
        list_items = tk.Variable(value=tuple(self.currentFiles))
        if hasattr(self,'listFileWidget'):
            self.listFileWidget.destroy()
        else:
            self.open_label.pack_forget()
        self.listFileWidget = tk.Listbox(self.filePanel, listvariable=list_items)
        self.listFileWidget.pack(expand=True, fill=tk.BOTH)

        self.listFileWidget.bind('<ButtonRelease-1>', self.select_open_file)


    def select_open_file(self, event):
        selected_index = self.listFileWidget.curselection()
        if selected_index:
            index = selected_index[0]
            file_name = self.listFileWidget.get(index)
            # print(file_name)
            self.open_file(file=file_name)


    def open_new_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".wkfw")
        if file_path.endswith(".wkfw"):
            self.open_file(file_path,False)
        # print(file_path)

    def open_file(self, file, add_currentDir=True):
        if add_currentDir and self.currentDir:
            path = pathlib.Path(self.currentDir).joinpath(file)
            file_name = file
        elif not add_currentDir:
            path = file
            file_name = file.split('/')[-1]
        else:
            self.terminal.write("Give the full path","ERROR")

        if file_name in self.tabs:
            self.notebook.select(self.tabs.index(file_name))

        else:
            try:
                data = import_wkfw_file(path)
                self.add_notebook_tabs(tabs=[file_name])
                process_data(data)
                self.currentFiles.add(file_name)

            except Exception as e:
                self.terminal.write(f"Not Able to open file, getting {e}", "ERROR")

    def create_layout(self):
        # Panned window
        self.pw = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.filePanel = ttk.Frame(self.pw, relief=tk.SOLID, borderwidth=1)
        self.mainPanel = ttk.Frame(self.pw, relief=tk.SOLID, borderwidth=1)
        self.pw.add(self.filePanel, weight=1)
        self.pw.add(self.mainPanel, weight=3)
        self.pw.pack(fill=tk.BOTH, expand=True)

        self.main_pw = ttk.PanedWindow(self.mainPanel, orient=tk.VERTICAL)
        self.terminalPanel = ttk.Frame(self.main_pw, relief=tk.SOLID, borderwidth=1)
        self.openFilePanel = ttk.Frame(self.main_pw, relief=tk.SOLID, borderwidth=1)
        self.main_pw.add(self.openFilePanel, weight=3)
        self.main_pw.add(self.terminalPanel, weight=1)
        self.main_pw.pack(fill=tk.BOTH, expand=True)

        # Add Notebook widget to openFilePanel
        self.notebook = ttk.Notebook(self.openFilePanel)
        self.notebook.pack(fill=tk.BOTH, expand=True)

    def add_notebook_tabs(self, tabs):
        for tab in tabs:
            print(tab)
            tab1 = ttk.Frame(self.notebook)
            # self.notebook.add(tab1, text=tab)
            self.notebook.insert(self.notebook.index("end")-1,tab1,text=tab)
            self.tabs.append(tab)
            self.notebook.select(self.tabs.index(tab))


    def on_tab_button_click(self, event):
        # print(event.x,event.y)
        try:
            tab_id = self.notebook.index("@%d,%d" % (event.x, event.y))
            tab_text = self.notebook.tab(tab_id, "text")
            if tab_text == "+":
                try:
                    if self.currentDir:
                        file_path = filedialog.asksaveasfilename(initialdir=self.currentDir, defaultextension=".wkfw",
                                                                 filetypes=[("Json Files", "*.wkfw")])
                    else:
                        file_path = filedialog.asksaveasfilename(defaultextension=".wkfw",
                                                                 filetypes=[("Workflow Files", "*.wkfw")])
                    # More code
                    if file_path is None or file_path == "":
                        return
                    try:
                        create_wkfw_file(filepath=file_path)
                        if not self.open_label.winfo_ismapped():
                            self.updateFileList([os.path.split(file_path)[1]])

                    except Exception as e:
                        self.terminal.write(f"{e}","ERROR")

                    if os.path.split(file_path)[1] not in self.currentFiles:
                        new_tab = ttk.Frame(self.notebook)
                        self.notebook.insert(tab_id, new_tab, text=os.path.split(file_path)[1])
                        self.tabs.insert(os.path.split(file_path)[1],tab_id)

                except Exception as e:
                    self.terminal.write(f"{e}", "ERROR")

        except Exception as e:
            self.terminal.write(f"{e}", "ERROR")

    def donothing(self):
        filewin = tk.Toplevel(self.root)
        button = tk.Button(filewin, text="Do nothing button")
        button.pack()

    def add_menu_labels(self, label_map, master):
        self.menuLabels.update(label_map)
        for x, y in label_map.items():
            x_menu = tk.Menu(master, tearoff=0)
            for label, command in y.items():
                if label == 'separator':
                    x_menu.add_separator()
                    continue
                x_menu.add_command(label=label, command=command)

            master.add_cascade(label=x, menu=x_menu)
        self.root.config(menu=self.menuBar)

    def run(self):
        self.root.mainloop()


app = BaseApp("GUI Automator")
app.run()
