import Tkinter as Tk

"""
Tkinter Listbox with soft-returns prototype module!
Augusta Nicholas Collins
01703131656

If you're going to use this, put in a good word for me, yes?
Yes?
Thank you. <3
"""

class MutliLine_Single(object):
    '''A basic Tkinter Listbox single-selection window that allows the use of carriage returns
in its strings. Some extended functionality that replaces falsey list elements with the
`divider_string` argument text. Falsey elements are not selectable.'''
    
    def __init__(self, items, title='', width=20, divider_string='', return_index=False, abort_value=None):
        '''A Listbox selector that allows the use of string entries spanning multiple lines.
Strings are broken on normal line breaks (`\n`). If the pane window is closed or cancelled,
`abort_value` or `None` is returned. Otherwise, the complete, selected value is returned, if
any is selected, else `None`.
 * Confirming with no item selected returns `None` and is different from aborting selection!

    = arguments
items           tuplist of strings      Items to be included in the Listbox list.
                                         - Falsey elements are interpreted as spacers in the list
                                          and are not selectable.

    = optional arguments
title           string                  Listbox pane title. (def: '')
width           nonzero positive int    Listbox width, in characters (not px!) (def: 20)
divider_string  string                  Falsey values (including `''`) in the items list will be
                                          replaced with this string when displayed in the Listbox.
                                          In no case are they selectable and clear the current
                                          selection when selected by the user.
                                         - Default: ''
return_index    boolean                 If True, when the Listbox pane is closed, the index value
                                          for the selected item in the `items` argument sequence
                                          will be returned instead of the string itself.
                                         - Be aware that spacer (falsey) list items' indices are
                                          enumerated but are not returnable!
                                         - Returns `None` if no item is selected, as normal.
                                         - Default: False
abort_value     <any>                   If the selector window is closed or cancelled, this value
                                          will be returned. (def: None)
'''
        from Tkinter import TOP, RIGHT, LEFT, BOTTOM, Y
        
        self.root = tkroot = Tk.Tk()

        if title:
            tkroot.title(title)

        lb_frame = Tk.Frame(tkroot)
        lb_frame.pack(side=TOP, padx=6, pady=4)

        lb_scrollbar = Tk.Scrollbar(lb_frame)
        lb_scrollbar.pack(side=RIGHT, fill=Y)
        
        self.lb = lb = Tk.Listbox(lb_frame, selectmode=Tk.SINGLE, width=width)
        lb.pack(side=LEFT, fill=Y)
        lb_scrollbar.config(command=lb.yview)
        lb.config(yscrollcommand=lb_scrollbar.set)

        self.return_index = return_index # return the item index, rather than the string proper?
        self.abort_value = abort_value # return this value on WM_DELETE_WINDOW or cancel.

        self.index_sets = []
            # ^ A list of Listbox element items and the other lines they're
            #  linked to. When a specific Listbox element is selected, the
            #  index of that selection is matched to the corresponding element
            #  in this list, which contains the indices of the first and last
            #  elements in the Listbox. This range is then selected.

        self.string_register = {}
            # ^ A dict that keys the first Listbox element's selection index
            #  to the whole string. Used to match an selection to an output
            #  on item selection.

        self.null_indices = []
            # ^ A list of index values for blank lines (`''` strings).
            #  All they do is clear the selection.

        self.NULL_MARKER = divider_string or ''
            # ^ If you include blank strings (`''`), they will be replaced
            #  with these characters in the list. Useful organizationally.
            
        lb_elements = self._parse_strings(items)
            # ^ Get a list of divided strings to put in the Listbox.

        lb.insert(0, *lb_elements)

        self.lastselection = None # the last Listbox item selected.

        tkroot.bind('<Return>', self._transmit)
        tkroot.bind('<Escape>', self._abort)
        tkroot.protocol('WM_DELETE_WINDOW', self._abort)

        lb.bind('<<ListboxSelect>>', self._reselect)

        transmit_btn = Tk.Button(tkroot, text='Confirm', command=self._transmit)
        transmit_btn.pack(side=BOTTOM, pady=4)

        clear_btn = Tk.Button(tkroot, text='Clear', command=self._clear)
        clear_btn.pack(side=BOTTOM)


    def _parse_strings(self, string_list):
        '''Accepts a list of strings and breaks each string into a series of lines,
logs the sets, and stores them in the item_roster and string_register attributes.'''
        index_sets = self.index_sets
        register = self.string_register
        REG_INDEX = self.return_index # register the item's index in the string list if truey.

        all_lines = [] # holds all strings after lines are split. used for Lb elements.
        line_number = 0
        for n, item in enumerate(string_list): # string_register: `n` is saved if REG_INDEX, else `item`
            if not item: # null strings or falsey elemetns add a blank space. useful organizationally.
                self.null_indices.append(line_number) # record the blank position
                all_lines.append(self.NULL_MARKER) # add the divider text (or '')
                index_sets.append(None) # add an index value for the gap

                line_number += 1 # increment the line number.
                continue
            
            lines = item.splitlines()

            all_lines.extend(lines) # add the divided string to the string stack
            register[line_number] = n if REG_INDEX else item
                # ^ Saves this item keyed to the first Listbox element it's associated with.
                #  Register the string_list index if REG_INDEX, otherwise register the unbroken string.
                #  Dividers are not registered.

            qty = len(lines)
            if qty == 1: # single line item..
                index_sets.append((line_number, line_number))
            else: # multiple lines in this item..
                element_range = line_number, line_number + qty - 1 # the range of Listbox indices..
                index_sets.extend([element_range] * qty) # ..one for each line in the Listbox.

            line_number += qty # increment the line number.
            
        return all_lines
    

    def _reselect(self, event=None):
        "Called whenever the Listbox's selection changes."
        selection = self.lb.curselection() # Get the new selection data.
        if not selection: # if there is nothing selected, do nothing.
            self.lastselection = None
            return

        if selection[0] in self.null_indices: # selected a divider..
            self._clear() # ..so clear the current selection.
            return
    
        lines_st, lines_ed = self.index_sets[selection[0]]
            # ^ Get the string block associated with the current selection.
        
        if lines_st == self.lastselection:
            self._clear()
            return # If the new set is the same as the old one, clear it.

        self.lb.selection_set(lines_st, lines_ed) # select all relevant lines
        self.lastselection = lines_st # remember what you selected last.


    def _clear(self, event=None):
        "Clears the current selection."
        selection = self.lb.curselection() # Get the currently selected item(s).
        if not selection: # Nothing to clear!
            return
        self.lb.selection_clear(selection[0], selection[-1]) # deselect..
        self.lastselection = None # ..and remember that you deselected!


    def _transmit(self, event=None):
        "Return whatever you currently have selected."
        if self.lastselection is None: # Nothing selected.
            self.result = None
        else: # Store the result in the `result` attr.
            self.result = self.string_register[self.lastselection]
        self.lb.destroy()


    def _abort(self, event=None):
        "Cancel out and return a preset or default abort value."
        self.result = self.abort_value
        self.lb.destroy()


    def run_selector(self, force_focus=False):
        '''Run the selector and return the selection (or None) once complete.
The `force_focus` argument, if truey, will immediately give the new selector pane focus.'''
        if force_focus:
            self.root.focus_force()
        self.root.wait_window(self.lb)
        self.root.destroy()
        return self.result


def test():
    "Test a MutliLine_Single object."
    
    testitems = 'mama', 'luigi', 'my birds', '', \
                'this is a single element\n spanning two lines!', '',\
                'here is one\n that ought to span\n three whole lines!!'
    testtitle = 'TESTING A MULTILINE LISTBOX'

    SELECTOR = MutliLine_Single(testitems, testtitle, divider_string='~~~', abort_value='<Aborted the selector!>')
    result = SELECTOR.run_selector(True)

    print "result: ", result
    print repr(result)




        
        
