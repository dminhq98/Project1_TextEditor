import tkinter as tk
import tkinter.messagebox as msg
from tkinter import filedialog
import os
import re

class Editor(tk.Tk):
    def __init__(self):
        super().__init__()
        # Constants
        self.FONT_SIZE = 12
        self.PROGRAM_NAME = "Text Editor"

        self.KEYWORDS_1 = ["import", "as", "from", "def", "try", "except", "self"]
        self.KEYWORDS_FLOW = ["if", "else", "elif", "try", "except", "for", "in", "while", "return", "with"]
        self.KEYWORDS_FUNCTIONS = ["print", "list", "dict", "set", "int", "float", "str"]

        self.SPACES_REGEX = re.compile("^\s*")
        self.STRING_REGEX_SINGLE = re.compile("'[^'\r\n]*'")
        self.STRING_REGEX_DOUBLE = re.compile('"[^"\r\n]*"')
        self.NUMBER_REGEX = re.compile(r"\b(?=\(*)\d+\.?\d*(?=\)*\,*)\b")
        self.KEYWORDS_REGEX = re.compile("(?=\(*)(?<![a-z])(None|True|False)(?=\)*\,*)")
        self.SELF_REGEX = re.compile("(?=\(*)(?<![a-z])(self)(?=\)*\,*)")
        self.FUNCTIONS_REGEX = re.compile("(?=\(*)(?<![a-z])(print|list|dict|set|int|str)(?=\()")

        self.REGEX_TO_TAG = {
            self.STRING_REGEX_SINGLE: "string",
            self.STRING_REGEX_DOUBLE: "string",
            self.NUMBER_REGEX: "digit",
            self.KEYWORDS_REGEX: "keywordcaps",
            self.SELF_REGEX: "keyword1",
            self.FUNCTIONS_REGEX: "keywordfunc",
        }
        # Global variable
        self.file_name = None

        self.title(self.PROGRAM_NAME)  # Application Name
        self.geometry("800x600")  # Application Size

        # icon loading
        self.new_file_icon = tk.PhotoImage(file='icons/new_file.gif')
        self.open_file_icon = tk.PhotoImage(file='icons/open_file.gif')
        self.save_file_icon = tk.PhotoImage(file='icons/save.gif')
        self.save_as_file_icon = tk.PhotoImage(file='icons/save_as.gif')
        self.exit_icon = tk.PhotoImage(file='icons/exit.gif')

        self.undo_icon = tk.PhotoImage(file='icons/undo.gif')
        self.redo_icon = tk.PhotoImage(file='icons/redo.gif')
        self.cut_icon = tk.PhotoImage(file='icons/cut.gif')
        self.copy_icon = tk.PhotoImage(file='icons/copy.gif')
        self.paste_icon = tk.PhotoImage(file='icons/paste.gif')
        self.find_icon = tk.PhotoImage(file='icons/find_text.gif')
        # Adding menu in the widget
        self.menu_bar = tk.Menu(self, bg="lightgrey", fg="black")
        # file menu items
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, bg="lightgrey", fg="black")
        self.file_menu.add_command(label='New', accelerator='Ctrl+N', compound='left', image=self.new_file_icon,underline=0, command=self.new_file)
        self.file_menu.add_command(label='Open', accelerator='Ctrl+O', compound='left', image=self.open_file_icon,underline=0, command=self.open_file)
        self.file_menu.add_command(label='Save', accelerator='Ctrl+S', compound='left', image=self.save_file_icon,underline=0, command=self.save)
        self.file_menu.add_command(label='Save as', accelerator='Shift+Ctrl+S', compound='left',image=self.save_as_file_icon, command=self.save_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', accelerator='Alt+F4', compound='left', image=self.exit_icon,command=self.exit_editor)
        self.menu_bar.add_cascade(label='File', menu=self.file_menu)
        # edit menu-items
        self.edit_menu = tk.Menu(self, bg="lightgrey", fg="black")
        self.edit_menu.add_command(label='Undo', accelerator='Ctrl+Z', compound='left', image=self.undo_icon,command=self.undo)
        self.edit_menu.add_command(label='Redo', accelerator='Ctrl+Y', compound='left', image=self.redo_icon,command=self.redo)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Cut', accelerator='Ctrl+X', compound='left', image=self.cut_icon,command=self.cut)
        self.edit_menu.add_command(label='Copy', accelerator='Ctrl+C', compound='left', image=self.copy_icon,command=self.copy)
        self.edit_menu.add_command(label='Paste', accelerator='Ctrl+V', compound='left', image=self.paste_icon,command=self.paste)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Find', accelerator='Ctrl+F', compound='left', underline=0, image=self.find_icon,command=self.find_text)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Select All', underline=7, accelerator='Ctrl+A', compound='left',command=self.select_all)
        self.menu_bar.add_cascade(label='Edit', menu=self.edit_menu)
        # View menu-items
        self.view_menu = tk.Menu(self, bg="lightgrey", fg="black")
        self.show_line_number = tk.IntVar()
        self.show_line_number.set(1)
        self.view_menu.add_checkbutton(label='Show Line Number', variable=self.show_line_number)
        self.show_cursor_info = tk.IntVar()
        self.show_cursor_info.set(1)
        self.view_menu.add_checkbutton(label='Show Cursor Location at Bottom', variable=self.show_cursor_info,command=self.show_cursor_info_bar)

        ##theme menu
        self.themes_menu = tk.Menu(self, bg="lightgrey", fg="black")
        self.view_menu.add_cascade(label='Themes', menu=self.themes_menu)

        #color scheme
        self.color_schemes = {
            'Default': '#000000.#FFFFFF',
            'Greygarious': '#83406A.#D1D4D1',
            'Aquamarine': '#5B8340.#D1E7E0',
            'Bold Beige': '#4B4620.#FFF0E1',
            'Cobalt Blue': '#ffffBB.#3333aa',
            'Olive Green': '#D1E7E0.#5B8340',
            'Night Mode': '#FFFFFF.#000000',
        }

        self.theme_choice = tk.StringVar()
        self.theme_choice.set('Default')
        for k in sorted(self.color_schemes):
            self.themes_menu.add_radiobutton(label=k, variable=self.theme_choice, command=self.change_theme)
        self.menu_bar.add_cascade(label='View', menu=self.view_menu)
        # Help menu-items will be added here
        self.help_menu = tk.Menu(self, bg="lightgrey", fg="black")
        self.help_menu.add_command(label='About', command=self.display_about_messagebox)
        self.help_menu.add_command(label='Help', command=self.display_help_messaggebox)
        self.menu_bar.add_cascade(label='Help', menu=self.help_menu)

        # Shortcut icon bar
        self.shortcut_bar = tk.Frame(self, height=25, background='Light sea green')
        self.shortcut_bar.pack(expand=0, fill=tk.X)

        self.icons = ('new_file', 'open_file', 'save', 'cut', 'copy', 'paste', 'undo', 'redo', 'find_text')
        for i, icon in enumerate(self.icons):
            self.tool_bar_icon = tk.PhotoImage(file='icons/{}.gif'.format(icon))
            self.cmd = eval('self.'+icon)
            self.tool_bar = tk.Button(self.shortcut_bar, image=self.tool_bar_icon, command=self.cmd)
            self.tool_bar.image = self.tool_bar_icon
            self.tool_bar.pack(side=tk.LEFT)
        # line number bars
        self.line_number_bar = tk.Text(self, width=6, padx=3, takefocus=0, bg="lightgrey", fg="black",
                                       state='disabled', wrap='none',font=("Ubuntu Mono", self.FONT_SIZE))

        self.line_number_bar.pack(side=tk.LEFT, fill=tk.Y)

        # Content portion + Scroll bar settings
        self.content_text = tk.Text(self, wrap='word', bg="white", fg="black", undo=1, font=("Ubuntu Mono", self.FONT_SIZE))


        self.scroll_bar = tk.Scrollbar(self, orient="vertical", command=self.scroll_text_and_line_numbers)
        self.content_text.configure(yscrollcommand=self.scroll_bar.set)
        #self.scroll_bar.config(command=self.scroll_text_and_line_numbers)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_text.pack(expand=1, fill=tk.BOTH)

        self.cursor_info_bar = tk.Label(self.content_text, text='Line: 1 | column: 1')
        self.cursor_info_bar.pack(expand=tk.NO, fill=None, side=tk.RIGHT, anchor='se')

        self.content_text.tag_config("keyword1", foreground="orange")
        self.content_text.tag_config("keywordcaps", foreground="navy")
        self.content_text.tag_config("keywordflow", foreground="purple")
        self.content_text.tag_config("keywordfunc", foreground="darkgrey")
        self.content_text.tag_config("decorator", foreground="khaki")
        self.content_text.tag_config("digit", foreground="red")
        self.content_text.tag_config("string", foreground="green")
        self.content_text.tag_config("findmatch", background="yellow")

        # binding shortcut keys to command
        self.content_text.bind('<Control-N>', self.new_file)
        self.content_text.bind('<Control-n>', self.new_file)
        self.content_text.bind('<Control-O>', self.open_file)
        self.content_text.bind('<Control-o>', self.open_file)
        self.content_text.bind('<Control-S>', self.save)
        self.content_text.bind('<Control-s>', self.save)

        self.content_text.bind('<Control-y>', self.redo)  # handling Ctrl + smallcase y
        self.content_text.bind('<Control-Y>', self.redo)  # handling Ctrl + uppercase Y
        self.content_text.bind('<Control-A>', self.select_all)
        self.content_text.bind('<Control-a>', self.select_all)
        self.content_text.bind('<Control-F>', self.find_text)
        self.content_text.bind('<Control-f>', self.find_text)

        self.content_text.bind('<KeyPress-F1>', self.display_help_messaggebox)
        self.content_text.bind('<Button-3>', self.show_popup_menu)
        self.content_text.bind('<Any-KeyPress>', self.on_content_changed)
        self.content_text.bind("<MouseWheel>", self.scroll_text_and_line_numbers)
        self.content_text.bind("<Button-4>", self.scroll_text_and_line_numbers)
        self.content_text.bind("<Button-5>", self.scroll_text_and_line_numbers)
        self.line_number_bar.bind("<MouseWheel>", self.skip_event)

        # pop up menu
        self.popup_menu = tk.Menu(self.content_text)
        for i in ('cut', 'copy', 'paste', 'undo', 'redo'):
            self.cmd = eval('self.'+i)
            self.popup_menu.add_command(label=i.title(), compound='left', command=self.cmd)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label='Select All', underline=7, command=self.select_all)

        self.configure(menu=self.menu_bar)
        self.protocol('WM_DELETE_WINDOW', self.exit_editor)

    # callback functions
    def skip_event(self, event=None):
        return "break"

    def scroll_text_and_line_numbers(self, *args):
        try: # from scrollbar
            self.content_text.yview_moveto(args[1])
            self.line_number_bar.yview_moveto(args[1])
        except IndexError:
            #from mouse MouseWheel
            event = args[0]
            if event.delta:
                move = -1*(event.delta/120)
            else:
                if event.num == 5:
                    move = 1
                else:
                    move = -1

            self.content_text.yview_scroll(int(move), "units")
            self.line_number_bar.yview_scroll(int(move), "units")

        return "break"
    # File menu callbacks
    def new_file(self, event=None):
        self.title("Untitled")
        #global file_name
        self.file_name = None
        self.content_text.delete(1.0, tk.END)
        self.on_content_changed()

    def open_file(self, event=None):
        self.input_file_name = tk.filedialog.askopenfilename(defaultextension='.txt', filetypes=[("All files", "*.*"), (
        "Text Documents", "*.txt")])
        if self.input_file_name:
            #global file_name
            self.file_name = self.input_file_name
            self.title('{} - {}'.format(os.path.basename(self.file_name), self.PROGRAM_NAME))
            self.content_text.delete(1.0, tk.END)
            with open(self.file_name) as _file:
                self.content_text.insert(1.0, _file.read())
            self.tag_all_lines()
            self.on_content_changed()

    def save(self, event=None):
        #global file_name
        if not self.file_name:
            self.save_as()
        else:
            self.write_to_file(self.file_name)
        return "break"

    def save_as(self, event=None):
        self.input_file_name = tk.filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("All Files", "*.*"),
                                                                                                   ("Text Documents",
                                                                                                    "*.txt")])
        if self.input_file_name:
            #global file_name
            self.file_name = self.input_file_name
            self.write_to_file(self.file_name)
            self.title('{} - {}'.format(os.path.basename(self.file_name), self.PROGRAM_NAME))
        return "break"

    def write_to_file(self, file_name):
        try:
            self.content = self.content_text.get(1.0, tk.END)
            with open(self.file_name, 'w') as the_file:
                the_file.write(self.content)
        except IOError:
            pass
            # pass for now but we show some warning - we do this in next iteration

    def exit_editor(self, event=None):
        if tk.messagebox.askokcancel("Quit?", "Really quit?"):
            self.destroy()

    # edit menu callbacks
    def undo(self, event=None):
        self.content_text.event_generate('<<Undo>>')
        self.on_content_changed()
        return "break"

    def redo(self, event=None):
        self.content_text.event_generate('<<Redo>>')
        self.on_content_changed()
        return "break"

    def cut(self):
        self.content_text.event_generate('<<Cut>>')
        self.on_content_changed()
        return "break"

    def copy(self):
        self.content_text.event_generate('<<Copy>>')
        return "break"

    def paste(self):
        self.content_text.event_generate('<<Paste>>')
        self.tag_all_lines()
        self.on_content_changed()
        return "break"

    def select_all(self, event=None):
        self.content_text.tag_add('sel', 1.0, tk.END)
        return "break"

    def find_text(self, event=None):
        self.search_toplevel = tk.Toplevel(self)
        self.search_toplevel.title("Find Text")
        self.search_toplevel.transient(self)
        self.search_toplevel.resizable(False, False)
        tk.Label(self.search_toplevel, text="Find All").grid(row=0, column=0, sticky='e')
        self.search_entry_widget = tk.Entry(self.search_toplevel, width=25)
        self.search_entry_widget.grid(row=0, column=1, padx=2, pady=2, sticky='we')
        self.search_entry_widget.focus_set()
        self.ignore_case_value = tk.IntVar()
        tk.Checkbutton(self.search_toplevel, text="Ignore case", variable=self.ignore_case_value).grid(row=1, column=1, sticky='e',padx=2, pady=2)
        tk.Button(self.search_toplevel, text="Find All", underline=0,command=lambda: search_output(self.search_entry_widget.get(), self.ignore_case_value.get(), self.content_text,self.search_toplevel, self.search_entry_widget)).grid(row=0, column=2,sticky='e' + 'w', padx=2,pady=2)

        def close_search_window(self):
            self.content_text.tag_remove('match', '1.0', tk.END)
            self.search_toplevel.destroy()
            self.search_toplvel.protocol('WM_DELETE_WINDOW', self.close_search_window)
            return 'break'

        def search_output(needle, if_ignore_case, content_text, search_toplevel, search_box):
            content_text.tag_remove('match', '1.0', tk.END)
            matches_found = 0
            if needle:
                start_pos = '1.0'
                while True:
                    start_pos = content_text.search(needle, start_pos, nocase=if_ignore_case, stopindex=tk.END)
                    if not start_pos:
                        break
                    end_pos = '{}+{}c'.format(start_pos, len(needle))
                    content_text.tag_add('match', start_pos, end_pos)
                    matches_found += 1
                    start_pos = end_pos
                content_text.tag_config('match', foreground='red', background='yellow')
            search_box.focus_set()
            search_toplevel.title('{} matches found'.format(matches_found))

    # view menu callbacks
    def on_content_changed(self, event=None):
        self.update_line_number()
        self.update_cursor_info_bar()
        self.tag_all_lines()

    def get_line_numbers(self):
        self.output = ''
        if self.show_line_number.get():
            self.row, self.col = self.content_text.index(tk.END).split('.')
            for i in range(1, int(self.row)):
                self.output += str(i) + '\n'

        return self.output

    def update_line_number(self, event=None):
        self.line_numbers = self.get_line_numbers()
        self.line_number_bar.config(state='normal')
        self.line_number_bar.delete('1.0', tk.END)
        self.line_number_bar.insert('1.0', self.line_numbers)
        self.line_number_bar.config(state='disabled')

    def update_cursor_info_bar(self, event=None):
        self.row, self.col = self.content_text.index(tk.INSERT).split('.')
        self.line_num, self.col_num = str(int(self.row)), str(int(self.col) + 1)  # Col starts at 0
        self.infotext = "Line: {0} | Column: {1}".format(self.line_num, self.col_num)
        self.cursor_info_bar.config(text=self.infotext)

    def show_cursor_info_bar(self):
        self.show_cursor_info_checked = self.show_cursor_info.get()
        if self.show_cursor_info_checked:
            self.cursor_info_bar.pack(expand=0, fill=None, side=tk.RIGHT, anchor='se')
        else:
            self.cursor_info_bar.pack_forget()

    def change_theme(self, event=None):
        self.selected_theme = self.theme_choice.get()
        self.fg_bg_colors = self.color_schemes.get(self.selected_theme)
        self.foreground_color, self.background_color = self.fg_bg_colors.split('.')
        self.content_text.config(background=self.background_color, fg=self.foreground_color)

    # Help menu callbacks
    def display_about_messagebox(self, event=None):
        tk.messagebox.showinfo("About",
                               "{}{}".format(self.PROGRAM_NAME, "\nTkinter GUI Application\n This is my project"))

    def display_help_messaggebox(self, event=None):
        tk.messagebox.showinfo("Help", "Help Book:{} \nTkinter GUI application \nThis is my project".format(self.PROGRAM_NAME),
                               icon='question')

    # popup menu callbacks
    def show_popup_menu(self, event):
        self.popup_menu.tk_popup(event.x_root, event.y_root)


    def number_of_leading_spaces(self, line):
        spaces = re.search(self.SPACES_REGEX, line)
        if spaces.group(0) is not None:
            number_of_spaces = len(spaces.group(0))
        else:
            number_of_spaces = 0

        return number_of_spaces

    def add_regex_tags(self, line_number, line_text):
        for regex, tag in self.REGEX_TO_TAG.items():
            for match in regex.finditer(line_text):
                start, end = match.span()
                start_index = ".".join([line_number, str(start)])
                end_index = ".".join([line_number, str(end)])
                self.content_text.tag_add(tag, start_index, end_index)

    def tag_keywords(self, event=None, current_index=None):
        if not current_index:
            current_index = self.content_text.index(tk.INSERT)
        line_number = current_index.split(".")[0]
        line_beginning = ".".join([line_number, "0"])
        line_text = self.content_text.get(line_beginning, line_beginning + " lineend")
        line_words = line_text.split()
        number_of_spaces = self.number_of_leading_spaces(line_text)
        y_position = number_of_spaces

        for tag in self.content_text.tag_names():
            if tag != "sel":
                self.content_text.tag_remove(tag, line_beginning, line_beginning + " lineend")

        self.add_regex_tags(line_number, line_text)

        for word in line_words:
            stripped_word = word.strip("():,")

            word_start = str(y_position)
            word_end = str(y_position + len(stripped_word))
            start_index = ".".join([line_number, word_start])
            end_index = ".".join([line_number, word_end])

            if stripped_word in self.KEYWORDS_1:
                self.content_text.tag_add("keyword1", start_index, end_index)
            elif stripped_word in self.KEYWORDS_FLOW:
                self.content_text.tag_add("keywordflow", start_index, end_index)
            elif stripped_word.startswith("@"):
                self.content_text.tag_add("decorator", start_index, end_index)

            y_position += len(word) + 1

    def tag_all_lines(self):
        final_index = self.content_text.index(tk.END)
        final_line_number = int(final_index.split(".")[0])

        for line_number in range(final_line_number):
            line_to_tag = ".".join([str(line_number), "0"])
            self.tag_keywords(None, line_to_tag)

if __name__ == "__main__":
    editor = Editor()
    editor.mainloop()
