import ast
import pathlib
import tkinter as tk
from pprint import pprint
from tkinter import ttk
from tkinter import filedialog
import os
from workflow_file import *
from datetime import datetime
from runner import *


class TaskCell:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, borderwidth=1)
        self.frame.grid(row=0, column=0)

        self.start_after_label = ttk.Label(self.frame, text="Start Task After (in seconds)", justify="left")
        self.start_after_label.grid(row=0, column=0)
        self.start_after_input = ttk.Entry(self.frame)
        self.start_after_input.insert(0, "0")
        self.start_after_input.grid(row=0, column=1)

        self.task_types = list(TASKS.keys())

        self.label = ttk.Label(self.frame, text="Select Task Type", justify="left")
        self.label.grid(row=1, column=0)
        self.task_type_var = tk.StringVar()
        self.task_type_combobox = ttk.Combobox(self.frame, textvariable=self.task_type_var, values=self.task_types)
        self.task_type_combobox.grid(row=1, column=1)
        self.select_button = ttk.Button(self.frame, text="Select Task Type", command=self.show_selected_task)
        self.select_button.grid(row=2, column=0)
        self.addButton = ttk.Button(self.frame, text="Add New Arguments", command=self.add_new_arg)
        self.addButton.grid(row=2, column=1)

        self.labels = []

    def add_new_arg(self):
        self.create_key_value_label("arg", "", len(self.labels) + 3, False)

    def show_selected_task(self):
        selected_task_type = self.task_type_var.get()
        if selected_task_type:
            if len(self.labels) > 0:
                for label in self.labels:
                    label.destroy()
                self.labels.clear()

            for args in TASKS[selected_task_type]:
                self.create_key_value_label(args, "", len(self.labels) + 3)
        else:
            print("No Task Type Selected!")

    def create_key_value_label(self, key, value, row, key_read_only=True):
        self.labels.append(ttk.Entry(self.frame))
        self.labels[-1].insert(0, key)
        if key_read_only:
            self.labels[-1].config(state="readonly")
        self.labels[-1].grid(row=row, column=0)
        self.labels.append(ttk.Entry(self.frame))
        self.labels[-1].insert(0, value)
        self.labels[-1].grid(row=row, column=1)


class CustomTextCell:
    def __init__(self, parent_frame, text, index):
        self._index = index
        self.frame = ttk.Frame(parent_frame, borderwidth=1)
        self.frame.grid(row=index, column=0)

        self.index_label = ttk.Label(self.frame, text=str(self._index), width=4)
        self.index_label.grid(row=0, column=0)

        self.text = tk.StringVar(value=text)
        self.textWidget = ttk.Frame(self.frame)
        self.textWidget.grid(row=0, column=1, columnspan=10, sticky="ew")
        self.task = TaskCell(self.textWidget)

        self.move_up_button = ttk.Button(self.frame, text="Move Up", command=self.move_up)
        self.move_up_button.grid(row=1, column=5)

        self.move_down_button = ttk.Button(self.frame, text="Move Down", command=self.move_down)
        self.move_down_button.grid(row=1, column=6)

        # self.run_button = ttk.Button(self.frame, text="Compile", command=self.compile)
        # self.run_button.grid(row=1, column=7)

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, new_index):
        self._index = new_index
        self.index_label.config(text=str(self._index))

    def move_up(self):
        if self._index > 0:
            w1 = FileFrame.cells[self._index - 1]
            w2 = FileFrame.cells[self._index]
            FileFrame.swap_widgets(w1, w2)

    def move_down(self):
        if self._index < len(FileFrame.cells) - 1:
            w1 = FileFrame.cells[self._index]
            w2 = FileFrame.cells[self._index + 1]
            FileFrame.swap_widgets(w1, w2)

    def compile(self):
        ans = {}
        # print(self.task.labels)
        i = 0
        while i < len(self.task.labels):
            key = str(self.task.labels[i].get())
            value = str(self.task.labels[i + 1].get())
            try:
                ev = ast.literal_eval(value)
            except:
                ev = value
            if isinstance(ev, str) and ev.isnumeric():
                ev = int(ev)
            ans[key] = ev
            i += 2

        ans["start_time"] = int(self.task.start_after_input.get())
        cell_data = {
            "type": "task",
            "task_type": self.task.task_type_var.get(),
            "task_data": ans
        }
        return cell_data


class FileFrame:
    cells = []

    def __init__(self, parent, file_path, file_name):
        self.file_path = file_path
        self.file_name = file_name
        try:
            self.data = import_wkfw_file(file_path=file_path)
        except Exception as e:
            print("File is not able to Load!")

        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.add_cell_button = ttk.Button(parent, text="Add Cell", command=self.add_cell)
        self.add_cell_button.pack()

        self.runButton = ttk.Button(parent, text="Run All", command=self.run)
        self.runButton.pack()

        self.saveButton = ttk.Button(parent, text="Save", command=self.save_file)
        self.saveButton.pack()

        self.load_data()

    def add_cell(self):
        index = len(FileFrame.cells)
        cell = CustomTextCell(self.frame, text=f"Cell {index}", index=index)
        FileFrame.cells.append(cell)

    def swap_widgets(w1, w2):
        row1, col1 = w1.frame.grid_info()["row"], w1.frame.grid_info()["column"]
        row2, col2 = w2.frame.grid_info()["row"], w2.frame.grid_info()["column"]

        w1.frame.grid(row=row2, column=col2)
        w1.index = row2

        w2.frame.grid(row=row1, column=col1)
        w2.index = row1

    def save_file(self):
        self.compile_all()
        save_wkfw_file(filepath=self.file_path, data=self.data)

    def load_data(self):
        for cell in self.data["cells"]:
            self.add_cell()
            FileFrame.cells[-1].task.start_after_input.delete(0, tk.END)
            FileFrame.cells[-1].task.start_after_input.insert(0, cell["task_data"]["start_time"])

            FileFrame.cells[-1].task.task_type_var.set(cell["task_type"])
            for key, value in cell["task_data"].items():
                if key == "start_time":
                    continue
                if key in TASKS[cell["task_type"]]:
                    FileFrame.cells[-1].task.create_key_value_label(key, str(value),
                                                                    len(FileFrame.cells[-1].task.labels) + 3)
                else:
                    FileFrame.cells[-1].task.create_key_value_label(key, str(value),
                                                                    len(FileFrame.cells[-1].task.labels) + 3, False)

    def compile_all(self):
        for cell in FileFrame.cells:
            m1 = cell.compile()
            if cell.index < len(self.data["cells"]):
                self.data["cells"][cell.index] = m1
            else:
                self.data["cells"].append(m1)

        pprint(self.data)

    def run(self):
        self.compile_all()
        wf = load_workflow(self.data, self.file_name)
        if wf[0] is None:
            return wf[1]
        else:
            wf[0].run()
            return None


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
        self.new_frame = {}
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

    def on_select(self, event):
        print("Event Triggered!")
        w = event.widget
        index = int(w.curselect()[0])
        value = w.get(index)
        print(w, index, value)
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
        if hasattr(self, 'listFileWidget'):
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
            self.open_file(file_path, False)
        # print(file_path)

    def open_file(self, file, add_currentDir=True):
        if add_currentDir and self.currentDir:
            path = pathlib.Path(self.currentDir).joinpath(file)
            file_name = file
        elif not add_currentDir:
            path = file
            file_name = file.split('/')[-1]
        else:
            self.terminal.write("Give the full path", "ERROR")

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
            self.notebook.insert(self.notebook.index("end") - 1, tab1, text=tab)
            self.new_frame[tab] = FileFrame(tab1, file_name=tab, file_path=pathlib.Path(self.currentDir).joinpath(tab))
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
                        self.terminal.write(f"{e}", "ERROR")

                    if os.path.split(file_path)[1] not in self.currentFiles:
                        new_tab = ttk.Frame(self.notebook)
                        self.notebook.insert(tab_id, new_tab, text=os.path.split(file_path)[1])
                        self.tabs.insert(os.path.split(file_path)[1], tab_id)

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
