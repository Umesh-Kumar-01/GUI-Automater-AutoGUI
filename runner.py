import pyautogui
import pyautogui as pg
import time


TASKS = {
    "write": ["interval","text"],
    "hotkey": ["keys"],
    "press_key": ["key"],
    "click": ["coordinates"],
    "click_on_image": ["wait_seconds","image_path"],
    "sleep":["time"],
}

class Work():
    def __init__(self, worktype, **kwargs) -> None:
        self.type = worktype
        self.details = kwargs
        self.status = False
        self.error = None

    def write(self):
        try:
            intvl = self.details['interval'] if self.details.get('interval') else 0.25
            pg.write(self.details['text'], interval=intvl)
            self.status = True
        except Exception as e:
            self.error = e

    def hotkey(self):
        # self .details['keys] should be a tuple
        try:
            pg.hotkey(*self.details['keys'])
            self.status = True
        except Exception as e:
            self.error = e

    def press_key(self):
        try:
            pg.press(self.details['key'])
            self.status = True
        except Exception as e:
            self.error = e

    def click(self):
        try:
            pg.click(self.details['coordinates'][0], self.details['coordinates'][1])
            self.status = True
        except Exception as e:
            self.error = e

    def click_on_image(self):
        try:
            start_time = time.time()
            while time.time() - start_time < self.details['wait_seconds']:
                if pg.locateOnScreen(self.details['image_path']) is None:
                    time.sleep(1)
                    continue
                else:
                    # image is on screen
                    x, y = pg.center(pg.locateOnScreen(self.details['image_path']))
                    pg.click(x, y)
                    self.status = True
                    break
        except Exception as e:
            self.error = e

    def run(self):
        pyautogui.sleep(self.details["start_time"])
        if self.type == 'write':
            self.write()
        elif self.type == 'hotkey':
            self.hotkey()
        elif self.type == 'click':
            self.click()
        elif self.type == 'press_key':
            self.press_key()
        elif self.type == 'sleep':
            time.sleep(self.details["time"])
        elif self.type == 'click_on_image':
            self.click_on_image()

        if not self.status:
            return self.error

        return None


class WorkFlow():
    def __init__(self, name) -> None:
        self.works = []
        self.name = name

    def add_work(self, worktype, **kwargs):
        self.works.append(Work(worktype, **kwargs))

    def run_work(self, index):
        self.works[index].run()

    def run(self):
        for work in self.works:
            work.run()

    def delete_work(self, index):
        del self.works[index]
        self.works.remove(index)

    def total_works(self):
        return len(self.works)


def load_workflow(json_data, name="untitled"):
    try:
        wf = WorkFlow(name)
        for cell in json_data["cells"]:
            if cell["type"] == "task":
                wf.add_work(worktype=cell["task_type"], **cell["task_data"])

        return wf, "No Error!"

    except Exception as e:
        return None, f"Not able to load workflow file! -- {e}"


def delete_workflow(workflow):
    del workflow
