import tkinter as tk
from tkinter import ttk
import utilities
import pyautogui
import threading
import configparser
import win32api
import time
import gfb
import hk
import queue

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Carnufex@Github")
        self.root.geometry('400x500')
        self.root.resizable(width=False, height=False)

        self.gfb_bool = tk.BooleanVar()
        self.checkButton_hk_bools = {}
        self.checkButton_spell_bools = {}
        self.hotkey_checkButton_dict = {}
        self.spell_checkButton_dict = {}

        self.hotkeys = []
        #loading all hk's into an array
        for item in config.items('HOTKEYS'):
            self.hotkeys.append(item[0])

        names = ['Hotkeys', 'Spell rotation', 'Healing', 'Config', 'Instructions']
        self.nb = self.create_notebook(self.root, names)
        self.menu = self.create_menus(self.root)





        # We can also add items to the Notebook here
        # tab = self.nb.tabs['Instructions']
        # tk.Label(tab, text='You should\nread these\ninstructions').pack()

        # btn = tk.Button(root, text='Click', command=self.button_command)
        # btn.pack()

        #root.mainloop()

    def thread_handler(self, button):

        button_name = button["text"]
        button_status = button.config('relief')[-1]
        if button_name == "Hotkeys":
            hk_thread = None
            if button_status == 'raised':
                #button pressed
                hk_thread = threading.Thread(target=hk_run)
                try:
                    print("Hotkeys enabled")
                    hk_thread.start()
                except:
                    print("Error: unable to start thread")
            else:
                print("Hotkeys disabled")
                #stop thread
                hk.stop()
                if hk_thread is not None:
                    hk_thread.join()
        elif button_name == "spell rotation":
            #print(self.checkButton_bools)
            gfb_hk_thread = None
            if self.checkButton_hk_bools['spell_rotation'].get() is True:
                #button pressed
                # coords is loaded from file as strings, parsing back to tuple type.
                start_coords = utilities.string2tuple(config['RESOLUTION']['game_start_coords'])
                end_coords = utilities.string2tuple(config['RESOLUTION']['game_end_coords'])
                # hotkey = config['SAVED_VARS']['GFB']
                # print(hotkey)

                #gfb_hk_thread = threading.Thread(target=gfb_run, args=(300, 'avalanche', 2, hotkey, start_coords, end_coords, config))
                gfb_hk_thread = threading.Thread(target=gfb_run, args=(start_coords, end_coords, config, gui))
                try:
                    print("starting spell rotation")
                    gfb_hk_thread.start()
                except:
                    print("Error: unable to start thread")
            else:
                #stop thread
                print("Stopping spell rotation")
                if gfb_hk_thread is not None:
                    gfb_hk_thread.join()



    def button_thread(self, button):
        if button.config('relief')[-1] == 'raised':
            self.thread_handler(button)
            if button.winfo_class() == 'Button':
                button["bg"] = "green"
                button.config(relief = 'sunken')
                print('raised')
        else:
            self.thread_handler(button)
            if button.winfo_class() == 'Button':
                print('sunken')
                button["bg"] = "red"
                button.config(relief = 'raised')

    def update_text(self, text_field, new_text):
        text_field.configure(state='normal')
        text_field.delete('1.0', 'end')
        text_field.insert('end', str(new_text))
        text_field.configure(state='disabled')

    '''
    Using Q to return something from a Thread instead of using multithreading; keeping old code

    Input:
    item : tuple containing var and value loaded from .ini
    text_field : tk.Text object

    Action:
    updated .ini file and value in GUI

    '''
    def button_config(self, item, text_field, section):
        print("updating: ", item, text_field)
        que = queue.Queue()
        mouse_thread = threading.Thread(target=lambda q, arg1: q.put(utilities.detect_mouse_click(arg1)), args=(que, 'test'))
        mouse_thread.start()
        result = que.get()
        mouse_thread.join()
        config.set(section, item[0], str(result))
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        self.update_text(text_field, result)

    def update_hotkeys(GUI_obj, category, item, amountObj):
        new_val = amountObj.get()
        #print('gui: {0}  category: {1}   item: {2}  new val: {3}'.format(GUI_obj, category, item, new_val))
        config.set(category, item, new_val)
        with open('config.ini', 'w') as configfile:
            config.write(configfile)




    def create_notebook(self, root, names):
        nb = ttk.Notebook(root, width=390, height=450)
        nb.pack()

        # Create tabs & save them by name in a dictionary
        nb.tabs = {}
        for name in names:
            nb.tabs[name] = tab = ttk.Frame(root)
            nb.add(tab, text=name)

        def add_label(parent, text, row, column, columnspan=1, rowspan=1):
            label = tk.Label(parent, text=text)
            label.grid(row=row, column=column, sticky=tk.N, pady=10, columnspan=columnspan, rowspan=rowspan)
            return label

        def add_button_thread(parent, button_text, command, row, column, columnspan=1):
            button = tk.Button(parent, text=button_text, command=lambda: command(button), bg="red", relief="raised", width=14)
            button.grid(row=row, column=column, sticky=tk.N, pady=10, padx=10, columnspan=columnspan)
            return button

        def add_button_config(parent, button_text, command, item, text_field, section, row, column):
            button = tk.Button(parent, text=button_text, command=lambda: command(item, text_field, section), bg="grey", width=10)
            button.grid(row=row, column=column, sticky=tk.N, pady=10, padx=10)
            return button

        def add_checkButton_hk(parent, text, variable, command, row, column):
            try:
                variable = self.checkButton_hk_bools[text]
            except:
                print("Didn\'t find the bool connected to checkbox")
            check_button = tk.Checkbutton(parent, text=text.replace("_", " "), variable=variable, command=lambda: command(check_button), onvalue=True, offvalue=False)
            check_button.grid(row=row, column=column, sticky=tk.N, pady=10, padx=10)
            self.hotkey_checkButton_dict[text] = check_button
            return check_button

        def add_checkButton_spell(parent, text, variable, command, row, column):
            try:
                variable = self.checkButton_spell_bools[text]
            except:
                print("Didn\'t find the bool connected to checkbox")
            check_button = tk.Checkbutton(parent, text=text.replace("_", " "), variable=variable, command=lambda: command(check_button), onvalue=True, offvalue=False)
            check_button.grid(row=row, column=column, sticky=tk.N, pady=10, padx=10)
            self.spell_checkButton_dict[text] = check_button
            return check_button

        def add_text(parent, text, width, height, row, col, state='normal'):
            text_field = tk.Text(parent, width=width, height=height)
            text_field.insert('end', text)
            text_field.configure(state=state)
            text_field.grid(row=row, column=col, sticky=tk.N, pady=10, padx=10)
            return text_field

        def add_optionMenu(parent, variable, option_list, command, category, item, row, col):
            option = tk.OptionMenu(parent, variable, *option_list, command=lambda var: command(category, item, variable))
            option.grid(row=row, column=col, sticky=tk.N, pady=10, padx=10)



        def cooldown_window():
            window = tk.Toplevel(self.root)
            window.grid()
            window.title("Cooldowns")
            window.geometry('400x500')
            window.resizable(width=False, height=False)
            load_cooldowns(window)



        def load_cooldowns(parent):
            i = 0
            info = 'Press the top left corner of the cooldown.'
            add_label(parent, info, i, 0, 3)
            i += 1
            info = 'Attack CD\'s'
            add_label(parent, info, i, 0, 3)
            for item in config.items('ATTACK_COOLDOWNS'):
                i += 1
                print(item)
                name = item[0].replace("_", " ")
                name = name.lower()
                add_label(parent, name, i, 0)
                text_field = add_text(parent, item[1], 12, 1, i, 1, 'disabled')
                add_button_config(parent, 'update', self.button_config, item, text_field, 'ATTACK_COOLDOWNS', i ,2)
            i += 1
            info = 'Healing CD\'s'
            add_label(parent, info, i, 0, 3)
            i += 1
            for item in config.items('HEALING_COOLDOWNS'):
                print(item)
                name = item[0].replace("_", " ")
                name = name.lower()
                add_label(parent, name, i, 0)
                text_field = add_text(parent, item[1], 12, 1, i, 1, 'disabled')
                add_button_config(parent, 'update', self.button_config, item, text_field, 'HEALING_COOLDOWNS', i ,2)
                i += 1

        def load_config(parent):
            i = 0
            for item in config.items('RESOLUTION'):
                label = item[0].replace("_", " ")
                label = label.lower()
                add_label(parent, label, i, 0)
                text_field = add_text(parent, item[1], 12, 1, i, 1, 'disabled')
                add_button_config(parent, 'update', self.button_config, item, text_field, 'RESOLUTION', i, 2)
                i += 1
            cooldown_button = tk.Button(parent, text="Cooldowns", command=cooldown_window)
            cooldown_button.grid(row=i, column=1, sticky=tk.N, pady=10, padx=10)

        def load_spell_settings(name):
            hotkey = tk.StringVar()
            amount = tk.StringVar()
            priority = tk.StringVar()
            for save in config.items('SAVED_VARS'):
                if name == save[0]:
                    hotkey.set(save[1])
                    break
                else:
                    hotkey.set('None')
            for save in config.items('AMOUNT'):
                if name == save[0]:
                    amount.set(save[1])
                    break
                else:
                    amount.set('None')
            for save in config.items('PRIORITY'):
                if name == save[0]:
                    priority.set(save[1])
                    break
                else:
                    priority.set('None')
            return (hotkey, amount, priority)

        def load_hotkeys(parent):
            add_label(parent, 'Enable all hotkeys: ', 0, 0)
            add_button_thread(parent, "Hotkeys", self.button_thread, 0, 1, columnspan=3)
            hotkey, trash, trash = load_spell_settings('spell_rotation')
            #hotkey = tk.StringVar()
            add_optionMenu(parent, hotkey, self.hotkeys, self.update_hotkeys, 'SAVED_VARS', 'spell_rotation', 1, 0)
            #spell rotation
            bool = tk.BooleanVar()
            self.checkButton_hk_bools['spell_rotation'] = bool
            add_checkButton_hk(parent, 'spell_rotation', self.checkButton_hk_bools['spell_rotation'], self.button_thread, 1, 1)



        def load_spell_rotation(parent):
            i = 1
            add_label(tab, 'Hotkey', i, 0)
            add_label(tab, 'Active', i, 1)
            add_label(tab, 'Min monsters', i, 2)
            add_label(tab, 'Priority', i, 3)

            #iterating through every offensive attack
            for item in config.items('ATTACK_COOLDOWNS'):
                i += 1
                #saving checkBox variables
                bool = tk.BooleanVar()
                self.checkButton_spell_bools[item[0]] = bool
                # mapping saved hotkeys to hotkeys
                tk_hotkey, tk_amount, tk_priority = load_spell_settings(item[0])
                #adding buttons
                add_optionMenu(parent, tk_hotkey, self.hotkeys, self.update_hotkeys, 'SAVED_VARS', item[0], i, 0)
                add_checkButton_spell(parent, item[0], self.checkButton_spell_bools[item[0]], self.button_thread, i, 1)
                add_optionMenu(parent, tk_amount, [str(i) for i in range(10)], self.update_hotkeys, 'AMOUNT', item[0], i, 2)
                add_optionMenu(parent, tk_priority, [str(i) for i in range(10)], self.update_hotkeys, 'PRIORITY', item[0], i, 3)


        # hotkeys tab
        tab = nb.tabs['Hotkeys']
        load_hotkeys(tab)

        #spell rotation tabs
        tab = nb.tabs['Spell rotation']
        load_spell_rotation(tab)



        # healing tab
        tab = nb.tabs['Healing']
        for i in range(3):
            add_label(tab, 'g' + str(i), 0, i)

        # config tab
        tab = nb.tabs['Config']
        load_config(tab)




        # for i in range(3):
        #     add_label(tab, 'm' + str(i), i, i)

        return nb

    def create_menus(self, root):
        menu = tk.Menu(root, tearoff=False)
        root.config(menu=menu)
        subMenu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label="File", menu=subMenu)
        subMenu.add_separator()
        subMenu.add_command(label='Exit', command=root.destroy)
        return menu


def hk_run():
    hk.start(gui, config)

#def gfb_run(radius, rune, min_monsters, hotkey, start_coords, end_coords, config):
def gfb_run(start_coords, end_coords, config, gui):
    pressed = gui.checkButton_hk_bools['spell_rotation'].get()
    while pressed:
        gfb.spellrotation(start_coords, end_coords, config, gui)
        #gfb.run(radius, rune, min_monsters, hotkey, start_coords, end_coords, config)
        pressed = gui.checkButton_hk_bools['spell_rotation'].get()
        #pressed = gui.gfb_bool.get()

config = configparser.ConfigParser()
config.read('config.ini')



gui = GUI()
gui.root.mainloop()
