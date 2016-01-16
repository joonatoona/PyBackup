eg_version = __doc__.split()[1]

__all__ = [
    'msgbox'
    , 'integerbox'
    , 'enterbox'
    , 'choicebox'
    , 'diropenbox'
    , 'multchoicebox'
]

import os
import sys
import string
import pickle
import traceback

if sys.hexversion >= 0x020600F0:
    runningPython26 = True
else:
    runningPython26 = False

if sys.hexversion >= 0x030000F0:
    runningPython3 = True
else:
    runningPython3 = False

try:
    from PIL import Image as PILImage
    from PIL import ImageTk as PILImageTk
except:
    pass

if runningPython3:
    from tkinter import *
    import tkinter.filedialog as tk_FileDialog
    from io import StringIO
else:
    from Tkinter import *
    import tkFileDialog as tk_FileDialog
    from StringIO import StringIO

# Set up basestring appropriately
if runningPython3:
    basestring = str

def write(*args):
    args = [str(arg) for arg in args]
    args = " ".join(args)
    sys.stdout.write(args)


def writeln(*args):
    write(*args)
    sys.stdout.write("\n")


if TkVersion < 8.0:
    stars = "*" * 75
    writeln("""\n\n\n""" + stars + """
You are running Tk version: """ + str(TkVersion) + """
You must be using Tk version 8.0 or greater to use EasyGui.
Terminating.
""" + stars + """\n\n\n""")
    sys.exit(0)

rootWindowPosition = "+300+200"

PROPORTIONAL_FONT_FAMILY = ("MS", "Sans", "Serif")
MONOSPACE_FONT_FAMILY = ("Courier")

PROPORTIONAL_FONT_SIZE = 10
MONOSPACE_FONT_SIZE = 9  # a little smaller, because it it more legible at a smaller size
TEXT_ENTRY_FONT_SIZE = 12  # a little larger makes it easier to see


STANDARD_SELECTION_EVENTS = ["Return", "Button-1", "space"]

# Initialize some global variables that will be reset later
__choiceboxMultipleSelect = None
__replyButtonText = None
__choiceboxResults = None
__firstWidget = None
__enterboxText = None
__enterboxDefaultText = ""
__multenterboxText = ""
choiceboxChoices = None
choiceboxWidget = None
entryWidget = None
boxRoot = None

def boolbox(msg="Shall I continue?"
            , title=" "
            , choices=("[Y]es", "[N]o")
            , image=None
            , default_choice='Yes'
            , cancel_choice='No'):
    """
    Display a boolean msgbox.

    The returned value is calculated this way::

        if the first choice is chosen, or if the dialog is cancelled:
            returns True
        else:
            returns False

    :param str msg: the msg to be displayed
    :param str title: the window title
    :param list choices: a list or tuple of the choices to be displayed
    :param str image: Filename of image to display
    :param str default_choice: The choice you want highlighted when the gui appears
    :param str cancel_choice: If the user presses the 'X' close, which button should be pressed
    :return: True if first button pressed or dialog is cancelled, False if second button is pressed
    """
    if len(choices) != 2:
        raise AssertionError('boolbox takes exactly 2 choices!  Consider using indexbox instead')

    reply = buttonbox(msg=msg,
                      title=title,
                      choices=choices,
                      image=image,
                      default_choice=default_choice,
                      cancel_choice=cancel_choice)
    if reply == choices[0]:
        return True
    else:
        return False

def msgbox(msg="(Your message goes here)"
           , title=" "
           , ok_button="OK"
           , image=None
           , root=None):
    if not isinstance(ok_button, basestring):
        raise AssertionError("The 'ok_button' argument to msgbox must be a string.")

    return buttonbox(msg=msg,
                     title=title,
                     choices=[ok_button],
                     image=image,
                     root=root,
                     default_choice=ok_button,
                     cancel_choice=ok_button)


#-------------------------------------------------------------------
# buttonbox
#-------------------------------------------------------------------
def buttonbox(msg=""
              , title=" "
              , choices=("Button[1]", "Button[2]", "Button[3]")
              , image=None
              , root=None
              , default_choice=None
              , cancel_choice=None):
    global boxRoot, __replyButtonText, buttonsFrame

    # If default is not specified, select the first button.  This matches old behavior.
    if default_choice is None:
        default_choice = choices[0]

    # Initialize __replyButtonText to the first choice.
    # This is what will be used if the window is closed by the close button.
    __replyButtonText = choices[0]

    if root:
        root.withdraw()
        boxRoot = Toplevel(master=root)
        boxRoot.withdraw()
    else:
        boxRoot = Tk()
        boxRoot.withdraw()


    boxRoot.title(title)
    boxRoot.iconname('Dialog')
    boxRoot.geometry(rootWindowPosition)
    boxRoot.minsize(400, 100)


    # ------------- define the messageFrame ---------------------------------
    messageFrame = Frame(master=boxRoot)
    messageFrame.pack(side=TOP, fill=BOTH)

    # ------------- define the imageFrame ---------------------------------
    if image:
        tk_Image = None
        try:
            tk_Image = __load_tk_image(image)
        except Exception as inst:
            print(inst)
        if tk_Image:
            imageFrame = Frame(master=boxRoot)
            imageFrame.pack(side=TOP, fill=BOTH)
            label = Label(imageFrame, image=tk_Image)
            label.image = tk_Image  # keep a reference!
            label.pack(side=TOP, expand=YES, fill=X, padx='1m', pady='1m')

    # ------------- define the buttonsFrame ---------------------------------
    buttonsFrame = Frame(master=boxRoot)
    buttonsFrame.pack(side=TOP, fill=BOTH)

    # -------------------- place the widgets in the frames -----------------------
    messageWidget = Message(messageFrame, text=msg, width=400)
    messageWidget.configure(font=(PROPORTIONAL_FONT_FAMILY, PROPORTIONAL_FONT_SIZE))
    messageWidget.pack(side=TOP, expand=YES, fill=X, padx='3m', pady='3m')

    __put_buttons_in_buttonframe(choices, default_choice, cancel_choice)

    # -------------- the action begins -----------
    boxRoot.deiconify()
    boxRoot.mainloop()
    boxRoot.destroy()
    if root:
        root.deiconify()
    return __replyButtonText

def integerbox(msg=""
               , title=" "
               , default=""
               , lowerbound=0
               , upperbound=99
               , image=None
               , root=None):

    if not msg:
        msg = "Enter an integer between {0} and {1}".format(lowerbound, upperbound)

    # Validate the arguments for default, lowerbound and upperbound and convert to integers
    exception_string = 'integerbox "{0}" must be an integer.  It is >{1}< of type {2}'
    if default:
        try:
            default=int(default)
        except ValueError:
            raise ValueError(exception_string.format('default', default, type(default)))
    try:
        lowerbound=int(lowerbound)
    except ValueError:
        raise ValueError(exception_string.format('lowerbound', lowerbound, type(lowerbound)))
    try:
        upperbound=int(upperbound)
    except ValueError:
        raise ValueError(exception_string.format('upperbound', upperbound, type(upperbound)))

    while 1:
        reply = enterbox(msg, title, str(default), image=image, root=root)
        if reply is None:
            return None
        try:
            reply = int(reply)
        except:
            msgbox('The value that you entered:\n\t"{}"\nis not an integer.'.format(reply)
                   , "Error")
            continue
        if reply < lowerbound:
            msgbox('The value that you entered is less than the lower bound of {}.'.format(lowerbound)
                   , "Error")
            continue
        if reply > upperbound:
            msgbox('The value that you entered is greater than the upper bound of {}.'.format(upperbound)
                   , "Error")
            continue
        # reply has passed all validation checks.
        # It is an integer between the specified bounds.
        return reply

def bindArrows(widget):

    widget.bind("<Down>", tabRight)
    widget.bind("<Up>", tabLeft)

    widget.bind("<Right>", tabRight)
    widget.bind("<Left>", tabLeft)


def tabRight(event):
    boxRoot.event_generate("<Tab>")


def tabLeft(event):
    boxRoot.event_generate("<Shift-Tab>")

def enterbox(msg="Enter something."
             , title=" "
             , default=""
             , strip=True
             , image=None
             , root=None):

    result = __fillablebox(msg, title, default=default, mask=None, image=image, root=root)
    if result and strip:
        result = result.strip()
    return result


def passwordbox(msg="Enter your password."
                , title=" "
                , default=""
                , image=None
                , root=None):

    return __fillablebox(msg, title, default, mask="*", image=image, root=root)


def __load_tk_image(filename):

    if filename is None:
        return None

    if not os.path.isfile(filename):
        raise ValueError('Image file {} does not exist.'.format(filename))

    tk_image = None

    filename = os.path.normpath(filename)
    _, ext = os.path.splitext(filename)

    try:
        pil_image = PILImage.open(filename)
        tk_image = PILImageTk.PhotoImage(pil_image)
    except:
        try:
            tk_image = PhotoImage(file=filename) #Fallback if PIL isn't available
        except:
            msg = "Cannot load {}.  Check to make sure it is an image file.".format(filename)
            try:
                _ = PILImage
            except:
                msg += "\nPIL library isn't installed.  If it isn't installed, only .gif files can be used."
            raise ValueError(msg)
    return tk_image


def __fillablebox(msg
                  , title=""
                  , default=""
                  , mask=None
                  , image=None
                  , root=None):

    global boxRoot, __enterboxText, __enterboxDefaultText
    global cancelButton, entryWidget, okButton

    if title is None:
        title == ""
    if default is None:
        default = ""
    __enterboxDefaultText = default
    __enterboxText = __enterboxDefaultText

    if root:
        root.withdraw()
        boxRoot = Toplevel(master=root)
        boxRoot.withdraw()
    else:
        boxRoot = Tk()
        boxRoot.withdraw()

    boxRoot.protocol('WM_DELETE_WINDOW', denyWindowManagerClose)
    boxRoot.title(title)
    boxRoot.iconname('Dialog')
    boxRoot.geometry(rootWindowPosition)
    boxRoot.bind("<Escape>", __enterboxCancel)

    # ------------- define the messageFrame ---------------------------------
    messageFrame = Frame(master=boxRoot)
    messageFrame.pack(side=TOP, fill=BOTH)

    # ------------- define the imageFrame ---------------------------------

    try:
        tk_Image = __load_tk_image(image)
    except Exception as inst:
        print(inst)
        tk_Image = None
    if tk_Image:
        imageFrame = Frame(master=boxRoot)
        imageFrame.pack(side=TOP, fill=BOTH)
        label = Label(imageFrame, image=tk_Image)
        label.image = tk_Image  # keep a reference!
        label.pack(side=TOP, expand=YES, fill=X, padx='1m', pady='1m')

    # ------------- define the buttonsFrame ---------------------------------
    buttonsFrame = Frame(master=boxRoot)
    buttonsFrame.pack(side=TOP, fill=BOTH)


    # ------------- define the entryFrame ---------------------------------
    entryFrame = Frame(master=boxRoot)
    entryFrame.pack(side=TOP, fill=BOTH)

    # ------------- define the buttonsFrame ---------------------------------
    buttonsFrame = Frame(master=boxRoot)
    buttonsFrame.pack(side=TOP, fill=BOTH)

    #-------------------- the msg widget ----------------------------
    messageWidget = Message(messageFrame, width="4.5i", text=msg)
    messageWidget.configure(font=(PROPORTIONAL_FONT_FAMILY, PROPORTIONAL_FONT_SIZE))
    messageWidget.pack(side=RIGHT, expand=1, fill=BOTH, padx='3m', pady='3m')

    # --------- entryWidget ----------------------------------------------
    entryWidget = Entry(entryFrame, width=40)
    bindArrows(entryWidget)
    entryWidget.configure(font=(PROPORTIONAL_FONT_FAMILY, TEXT_ENTRY_FONT_SIZE))
    if mask:
        entryWidget.configure(show=mask)
    entryWidget.pack(side=LEFT, padx="3m")
    entryWidget.bind("<Return>", __enterboxGetText)
    entryWidget.bind("<Escape>", __enterboxCancel)
    # put text into the entryWidget
    entryWidget.insert(0, __enterboxDefaultText)

    # ------------------ ok button -------------------------------
    okButton = Button(buttonsFrame, takefocus=1, text="OK")
    bindArrows(okButton)
    okButton.pack(expand=1, side=LEFT, padx='3m', pady='3m', ipadx='2m', ipady='1m')

    # for the commandButton, bind activation events to the activation event handler
    commandButton = okButton
    handler = __enterboxGetText
    for selectionEvent in STANDARD_SELECTION_EVENTS:
        commandButton.bind("<{}>".format(selectionEvent), handler)


    # ------------------ cancel button -------------------------------
    cancelButton = Button(buttonsFrame, takefocus=1, text="Quit")
    bindArrows(cancelButton)
    cancelButton.pack(expand=1, side=RIGHT, padx='3m', pady='3m', ipadx='2m', ipady='1m')

    # for the commandButton, bind activation events to the activation event handler
    commandButton = cancelButton
    handler = __enterboxCancel
    for selectionEvent in STANDARD_SELECTION_EVENTS:
        commandButton.bind("<{}>".format(selectionEvent), handler)

    # ------------------- time for action! -----------------
    entryWidget.focus_force()  # put the focus on the entryWidget
    boxRoot.deiconify()
    boxRoot.mainloop()  # run it!

    # -------- after the run has completed ----------------------------------
    if root:
        root.deiconify()
    boxRoot.destroy()  # button_click didn't destroy boxRoot, so we do it now
    return __enterboxText


def __enterboxGetText(event):
    global __enterboxText

    __enterboxText = entryWidget.get()
    boxRoot.quit()


def __enterboxRestore(event):
    global entryWidget

    entryWidget.delete(0, len(entryWidget.get()))
    entryWidget.insert(0, __enterboxDefaultText)


def __enterboxCancel(event):
    global __enterboxText

    __enterboxText = None
    boxRoot.quit()


def denyWindowManagerClose():
    """ don't allow WindowManager close
    """
    x = Tk()
    x.withdraw()
    x.bell()
    x.destroy()


#-------------------------------------------------------------------
# multchoicebox
#-------------------------------------------------------------------
def multchoicebox(msg="Pick as many items as you like."
                  , title=" "
                  , choices=()
                  , **kwargs):

    if len(choices) == 0:
        choices = ["Program logic error - no choices were specified."]

    global __choiceboxMultipleSelect
    __choiceboxMultipleSelect = 1
    return __choicebox(msg, title, choices)


#-----------------------------------------------------------------------
# choicebox
#-----------------------------------------------------------------------
def choicebox(msg="Pick something."
              , title=" "
              , choices=()):

    if len(choices) == 0:
        choices = ["Program logic error - no choices were specified."]

    global __choiceboxMultipleSelect
    __choiceboxMultipleSelect = 0
    return __choicebox(msg, title, choices)


#-----------------------------------------------------------------------
# __choicebox
#-----------------------------------------------------------------------
def __choicebox(msg
                , title
                , choices):
    """
    internal routine to support choicebox() and multchoicebox()
    """
    global boxRoot, __choiceboxResults, choiceboxWidget, defaultText
    global choiceboxWidget, choiceboxChoices

    choices = list(choices[:])

    if len(choices) == 0:
        choices = ["Program logic error - no choices were specified."]
    defaultButtons = ["OK", "Quit"]

    choices = [str(c) for c in choices]

    #TODO RL: lines_to_show is set to a min and then set to 20 right after that.  Figure out why.
    lines_to_show = min(len(choices), 20)
    lines_to_show = 20

    if title is None:
        title = ""

    # Initialize __choiceboxResults
    # This is the value that will be returned if the user clicks the close icon
    __choiceboxResults = None

    boxRoot = Tk()
    #boxRoot.protocol('WM_DELETE_WINDOW', denyWindowManagerClose ) #RL: Removed so top-level program can be closed with an 'x'
    screen_width = boxRoot.winfo_screenwidth()
    screen_height = boxRoot.winfo_screenheight()
    root_width = int((screen_width * 0.8))
    root_height = int((screen_height * 0.5))
    root_xpos = int((screen_width * 0.1))
    root_ypos = int((screen_height * 0.05))

    boxRoot.title(title)
    boxRoot.iconname('Dialog')
    rootWindowPosition = "+0+0"
    boxRoot.geometry(rootWindowPosition)
    boxRoot.expand = NO
    boxRoot.minsize(root_width, root_height)
    rootWindowPosition = '+{0}+{1}'.format(root_xpos, root_ypos)
    boxRoot.geometry(rootWindowPosition)

    # ---------------- put the frames in the window -----------------------------------------
    message_and_buttonsFrame = Frame(master=boxRoot)
    message_and_buttonsFrame.pack(side=TOP, fill=X, expand=NO)

    messageFrame = Frame(message_and_buttonsFrame)
    messageFrame.pack(side=LEFT, fill=X, expand=YES)

    buttonsFrame = Frame(message_and_buttonsFrame)
    buttonsFrame.pack(side=RIGHT, expand=NO, pady=0)

    choiceboxFrame = Frame(master=boxRoot)
    choiceboxFrame.pack(side=BOTTOM, fill=BOTH, expand=YES)

    # -------------------------- put the widgets in the frames ------------------------------

    # ---------- put a msg widget in the msg frame-------------------
    messageWidget = Message(messageFrame, anchor=NW, text=msg, width=int(root_width * 0.9))
    messageWidget.configure(font=(PROPORTIONAL_FONT_FAMILY, PROPORTIONAL_FONT_SIZE))
    messageWidget.pack(side=LEFT, expand=YES, fill=BOTH, padx='1m', pady='1m')

    # --------  put the choiceboxWidget in the choiceboxFrame ---------------------------
    choiceboxWidget = Listbox(choiceboxFrame
                              , height=lines_to_show
                              , borderwidth="1m"
                              , relief="flat"
                              , bg="white"
    )

    if __choiceboxMultipleSelect:
        choiceboxWidget.configure(selectmode=MULTIPLE)

    choiceboxWidget.configure(font=(PROPORTIONAL_FONT_FAMILY, PROPORTIONAL_FONT_SIZE))

    # add a vertical scrollbar to the frame
    rightScrollbar = Scrollbar(choiceboxFrame, orient=VERTICAL, command=choiceboxWidget.yview)
    choiceboxWidget.configure(yscrollcommand=rightScrollbar.set)

    # add a horizontal scrollbar to the frame
    bottomScrollbar = Scrollbar(choiceboxFrame, orient=HORIZONTAL, command=choiceboxWidget.xview)
    choiceboxWidget.configure(xscrollcommand=bottomScrollbar.set)

    bottomScrollbar.pack(side=BOTTOM, fill=X)
    rightScrollbar.pack(side=RIGHT, fill=Y)

    choiceboxWidget.pack(side=LEFT, padx="1m", pady="1m", expand=YES, fill=BOTH)

    if runningPython3:
        choices.sort(key=str.lower)
    else:
        choices.sort(lambda x, y: cmp(x.lower(), y.lower()))  # case-insensitive sort

    lastInserted = None
    choiceboxChoices = list()
    for choice in choices:
        if choice == lastInserted:
            continue
        else:
            choiceboxWidget.insert(END, choice)
            choiceboxChoices.append(choice)
            lastInserted = choice

    boxRoot.bind('<Any-Key>', KeyboardListener)

    # put the buttons in the buttonsFrame
    if len(choices):
        okButton = Button(buttonsFrame, takefocus=YES, text="OK", height=1, width=6)
        bindArrows(okButton)
        okButton.pack(expand=NO, side=TOP, padx='2m', pady='1m', ipady="1m", ipadx="2m")

        # for the commandButton, bind activation events to the activation event handler
        commandButton = okButton
        handler = __choiceboxGetChoice
        for selectionEvent in STANDARD_SELECTION_EVENTS:
            commandButton.bind("<%s>" % selectionEvent, handler)

        # now bind the keyboard events
        choiceboxWidget.bind("<Return>", __choiceboxGetChoice)
        choiceboxWidget.bind("<Double-Button-1>", __choiceboxGetChoice)
    else:
        # now bind the keyboard events
        choiceboxWidget.bind("<Return>", __choiceboxCancel)
        choiceboxWidget.bind("<Double-Button-1>", __choiceboxCancel)

    cancelButton = Button(buttonsFrame, takefocus=YES, text="Quit", height=1, width=6)
    bindArrows(cancelButton)
    cancelButton.pack(expand=NO, side=BOTTOM, padx='2m', pady='1m', ipady="1m", ipadx="2m")

    # for the commandButton, bind activation events to the activation event handler
    commandButton = cancelButton
    handler = __choiceboxCancel
    for selectionEvent in STANDARD_SELECTION_EVENTS:
        commandButton.bind("<%s>" % selectionEvent, handler)

    # add special buttons for multiple select features
    if len(choices) and __choiceboxMultipleSelect:
        selectionButtonsFrame = Frame(messageFrame)
        selectionButtonsFrame.pack(side=RIGHT, fill=Y, expand=NO)

        selectAllButton = Button(selectionButtonsFrame, text="Select All", height=1, width=6)
        bindArrows(selectAllButton)

        selectAllButton.bind("<Button-1>", __choiceboxSelectAll)
        selectAllButton.pack(expand=NO, side=TOP, padx='2m', pady='1m', ipady="1m", ipadx="2m")

        clearAllButton = Button(selectionButtonsFrame, text="Clear All", height=1, width=6)
        bindArrows(clearAllButton)
        clearAllButton.bind("<Button-1>", __choiceboxClearAll)
        clearAllButton.pack(expand=NO, side=TOP, padx='2m', pady='1m', ipady="1m", ipadx="2m")


    # -------------------- bind some keyboard events ----------------------------
    boxRoot.bind("<Escape>", __choiceboxCancel)

    # --------------------- the action begins -----------------------------------
    # put the focus on the choiceboxWidget, and the select highlight on the first item
    choiceboxWidget.select_set(0)
    choiceboxWidget.focus_force()

    # --- run it! -----
    boxRoot.mainloop()
    try:
        boxRoot.destroy()
    except:
        pass
    return __choiceboxResults


def __choiceboxGetChoice(event):
    global boxRoot, __choiceboxResults, choiceboxWidget

    if __choiceboxMultipleSelect:
        __choiceboxResults = [choiceboxWidget.get(index) for index in choiceboxWidget.curselection()]
    else:
        choice_index = choiceboxWidget.curselection()
        __choiceboxResults = choiceboxWidget.get(choice_index)

    boxRoot.quit()


def __choiceboxSelectAll(event):
    global choiceboxWidget, choiceboxChoices

    choiceboxWidget.selection_set(0, len(choiceboxChoices) - 1)


def __choiceboxClearAll(event):
    global choiceboxWidget, choiceboxChoices

    choiceboxWidget.selection_clear(0, len(choiceboxChoices) - 1)


def __choiceboxCancel(event):
    global boxRoot, __choiceboxResults

    __choiceboxResults = None
    boxRoot.quit()


def KeyboardListener(event):
    global choiceboxChoices, choiceboxWidget
    key = event.keysym
    if len(key) <= 1:
        if key in string.printable:
            # Find the key in the list.
            # before we clear the list, remember the selected member
            try:
                start_n = int(choiceboxWidget.curselection()[0])
            except IndexError:
                start_n = -1

            ## clear the selection.
            choiceboxWidget.selection_clear(0, 'end')

            ## start from previous selection +1
            for n in range(start_n + 1, len(choiceboxChoices)):
                item = choiceboxChoices[n]
                if item[0].lower() == key.lower():
                    choiceboxWidget.selection_set(first=n)
                    choiceboxWidget.see(n)
                    return
            else:
                # has not found it so loop from top
                for n, item in enumerate(choiceboxChoices):
                    if item[0].lower() == key.lower():
                        choiceboxWidget.selection_set(first=n)
                        choiceboxWidget.see(n)
                        return

                # nothing matched -- we'll look for the next logical choice
                for n, item in enumerate(choiceboxChoices):
                    if item[0].lower() > key.lower():
                        if n > 0:
                            choiceboxWidget.selection_set(first=(n - 1))
                        else:
                            choiceboxWidget.selection_set(first=0)
                        choiceboxWidget.see(n)
                        return

                # still no match (nothing was greater than the key)
                # we set the selection to the first item in the list
                lastIndex = len(choiceboxChoices) - 1
                choiceboxWidget.selection_set(first=lastIndex)
                choiceboxWidget.see(lastIndex)
                return

#-------------------------------------------------------------------
# textbox
#-------------------------------------------------------------------
def textbox(msg=""
            , title=" "
            , text=""
            , codebox=0):

    if msg is None:
        msg = ""
    if title is None:
        title = ""

    global boxRoot, __replyButtonText, __widgetTexts, buttonsFrame
    global rootWindowPosition
    choices = ["OK"]
    __replyButtonText = choices[0]

    boxRoot = Tk()

    boxRoot.protocol('WM_DELETE_WINDOW', denyWindowManagerClose)

    screen_width = boxRoot.winfo_screenwidth()
    screen_height = boxRoot.winfo_screenheight()
    root_width = int((screen_width * 0.8))
    root_height = int((screen_height * 0.5))
    root_xpos = int((screen_width * 0.1))
    root_ypos = int((screen_height * 0.05))

    boxRoot.title(title)
    boxRoot.iconname('Dialog')
    rootWindowPosition = "+0+0"
    boxRoot.geometry(rootWindowPosition)
    boxRoot.expand = NO
    boxRoot.minsize(root_width, root_height)
    rootWindowPosition = '+{0}+{1}'.format(root_xpos, root_ypos)
    boxRoot.geometry(rootWindowPosition)

    mainframe = Frame(master=boxRoot)
    mainframe.pack(side=TOP, fill=BOTH, expand=YES)

    # ----  put frames in the window -----------------------------------
    # we pack the textboxFrame first, so it will expand first
    textboxFrame = Frame(mainframe, borderwidth=3)
    textboxFrame.pack(side=BOTTOM, fill=BOTH, expand=YES)

    message_and_buttonsFrame = Frame(mainframe)
    message_and_buttonsFrame.pack(side=TOP, fill=X, expand=NO)

    messageFrame = Frame(message_and_buttonsFrame)
    messageFrame.pack(side=LEFT, fill=X, expand=YES)

    buttonsFrame = Frame(message_and_buttonsFrame)
    buttonsFrame.pack(side=RIGHT, expand=NO)

    # -------------------- put widgets in the frames --------------------

    # put a textArea in the top frame
    if codebox:
        character_width = int((root_width * 0.6) / MONOSPACE_FONT_SIZE)
        textArea = Text(textboxFrame, height=25, width=character_width, padx="2m", pady="1m")
        textArea.configure(wrap=NONE)
        textArea.configure(font=(MONOSPACE_FONT_FAMILY, MONOSPACE_FONT_SIZE))

    else:
        character_width = int((root_width * 0.6) / MONOSPACE_FONT_SIZE)
        textArea = Text(
            textboxFrame
            , height=25
            , width=character_width
            , padx="2m"
            , pady="1m"
        )
        textArea.configure(wrap=WORD)
        textArea.configure(font=(PROPORTIONAL_FONT_FAMILY, PROPORTIONAL_FONT_SIZE))


    # some simple keybindings for scrolling
    mainframe.bind("<Next>", textArea.yview_scroll(1, PAGES))
    mainframe.bind("<Prior>", textArea.yview_scroll(-1, PAGES))

    mainframe.bind("<Right>", textArea.xview_scroll(1, PAGES))
    mainframe.bind("<Left>", textArea.xview_scroll(-1, PAGES))

    mainframe.bind("<Down>", textArea.yview_scroll(1, UNITS))
    mainframe.bind("<Up>", textArea.yview_scroll(-1, UNITS))


    # add a vertical scrollbar to the frame
    rightScrollbar = Scrollbar(textboxFrame, orient=VERTICAL, command=textArea.yview)
    textArea.configure(yscrollcommand=rightScrollbar.set)

    # add a horizontal scrollbar to the frame
    bottomScrollbar = Scrollbar(textboxFrame, orient=HORIZONTAL, command=textArea.xview)
    textArea.configure(xscrollcommand=bottomScrollbar.set)

    if codebox:
        bottomScrollbar.pack(side=BOTTOM, fill=X)
    rightScrollbar.pack(side=RIGHT, fill=Y)

    textArea.pack(side=LEFT, fill=BOTH, expand=YES)


    # ---------- put a msg widget in the msg frame-------------------
    messageWidget = Message(messageFrame, anchor=NW, text=msg, width=int(root_width * 0.9))
    messageWidget.configure(font=(PROPORTIONAL_FONT_FAMILY, PROPORTIONAL_FONT_SIZE))
    messageWidget.pack(side=LEFT, expand=YES, fill=BOTH, padx='1m', pady='1m')

    # put the buttons in the buttonsFrame
    okButton = Button(buttonsFrame, takefocus=YES, text="OK", height=1, width=6)
    okButton.pack(expand=NO, side=TOP, padx='2m', pady='1m', ipady="1m", ipadx="2m")

    # for the commandButton, bind activation events to the activation event handler
    commandButton = okButton
    handler = __textboxOK
    for selectionEvent in ["Return", "Button-1", "Escape"]:
        commandButton.bind("<%s>" % selectionEvent, handler)


    # ----------------- the action begins ----------------------------------------
    try:
        # load the text into the textArea
        if isinstance(text, basestring):
            pass
        else:
            try:
                text = "".join(text)  # convert a list or a tuple to a string
            except:
                msgbox("Exception when trying to convert {} to text in textArea".format(type(text)))
                sys.exit(16)
        textArea.insert('end', text, "normal")

    except:
        msgbox("Exception when trying to load the textArea.")
        sys.exit(16)

    try:
        okButton.focus_force()
    except:
        msgbox("Exception when trying to put focus on okButton.")
        sys.exit(16)

    boxRoot.mainloop()

    # this line MUST go before the line that destroys boxRoot
    areaText = textArea.get(0.0, 'end-1c')
    boxRoot.destroy()
    return areaText  # return __replyButtonText


#-------------------------------------------------------------------
# __textboxOK
#-------------------------------------------------------------------
def __textboxOK(event):
    global boxRoot
    boxRoot.quit()


#-------------------------------------------------------------------
# diropenbox
#-------------------------------------------------------------------
def diropenbox(msg=None
               , title=None
               , default=None):

    title = getFileDialogTitle(msg, title)
    localRoot = Tk()
    localRoot.withdraw()
    if not default:
        default = None
    f = tk_FileDialog.askdirectory(
        parent=localRoot
        , title=title
        , initialdir=default
        , initialfile=None
    )
    localRoot.destroy()
    if not f:
        return None
    return os.path.normpath(f)


#-------------------------------------------------------------------
# getFileDialogTitle
#-------------------------------------------------------------------
def getFileDialogTitle(msg
                       ,title):

    if msg and title:
        return "%s - %s" % (title, msg)
    if msg and not title:
        return str(msg)
    if title and not msg:
        return str(title)
    return None  # no message and no title


#-------------------------------------------------------------------
# class FileTypeObject for use with fileopenbox
#-------------------------------------------------------------------
class FileTypeObject:
    def __init__(self, filemask):
        if len(filemask) == 0:
            raise AssertionError('Filetype argument is empty.')

        self.masks = list()

        if isinstance(filemask, basestring):  # a str or unicode
            self.initializeFromString(filemask)

        elif isinstance(filemask, list):
            if len(filemask) < 2:
                raise AssertionError('Invalid filemask.\n'
                                     + 'List contains less than 2 members: "{}"'.format(filemask))
            else:
                self.name = filemask[-1]
                self.masks = list(filemask[:-1])
        else:
            raise AssertionError('Invalid filemask: "{}"'.format(filemask))

    def __eq__(self, other):
        if self.name == other.name:
            return True
        return False

    def add(self, other):
        for mask in other.masks:
            if mask in self.masks:
                pass
            else:
                self.masks.append(mask)

    def toTuple(self):
        return self.name, tuple(self.masks)

    def isAll(self):
        if self.name == "All files":
            return True
        return False

    def initializeFromString(self, filemask):
        # remove everything except the extension from the filemask
        self.ext = os.path.splitext(filemask)[1]
        if self.ext == "":
            self.ext = ".*"
        if self.ext == ".":
            self.ext = ".*"
        self.name = self.getName()
        self.masks = ["*" + self.ext]

    def getName(self):
        e = self.ext
        file_types = {".*":"All", ".txt":"Text", ".py":"Python", ".pyc":"Python", ".xls":"Excel"}
        if e in file_types:
            return '{} files'.format(file_types[e])
        if e.startswith("."):
            return '{} files'.format(e[1:].upper())
        return '{} files'.format(e.upper())

#-------------------------------------------------------------------
#
# fileboxSetup
#
#-------------------------------------------------------------------
def fileboxSetup(default
                 , filetypes):
    if not default:
        default = os.path.join(".", "*")
    initialdir, initialfile = os.path.split(default)
    if not initialdir:
        initialdir = "."
    if not initialfile:
        initialfile = "*"
    initialbase, initialext = os.path.splitext(initialfile)
    initialFileTypeObject = FileTypeObject(initialfile)

    allFileTypeObject = FileTypeObject("*")
    ALL_filetypes_was_specified = False

    if not filetypes:
        filetypes = list()
    filetypeObjects = list()

    for filemask in filetypes:
        fto = FileTypeObject(filemask)

        if fto.isAll():
            ALL_filetypes_was_specified = True  # remember this

        if fto == initialFileTypeObject:
            initialFileTypeObject.add(fto)  # add fto to initialFileTypeObject
        else:
            filetypeObjects.append(fto)

    #------------------------------------------------------------------
    # make sure that the list of filetypes includes the ALL FILES type.
    #------------------------------------------------------------------
    if ALL_filetypes_was_specified:
        pass
    elif allFileTypeObject == initialFileTypeObject:
        pass
    else:
        filetypeObjects.insert(0, allFileTypeObject)

    if len(filetypeObjects) == 0:
        filetypeObjects.append(initialFileTypeObject)

    if initialFileTypeObject in (filetypeObjects[0], filetypeObjects[-1]):
        pass
    else:
        if runningPython26:
            filetypeObjects.append(initialFileTypeObject)
        else:
            filetypeObjects.insert(0, initialFileTypeObject)

    filetypes = [fto.toTuple() for fto in filetypeObjects]

    return initialbase, initialfile, initialdir, filetypes



#-------------------------------------------------------------------
# utility routines
#-------------------------------------------------------------------
# These routines are used by several other functions in the EasyGui module.

def uniquify_list_of_strings(input_list):

    output_list = list()
    for i, item in enumerate(input_list):
        tempList = input_list[:i] + input_list[i+1:]
        if item not in tempList:
            output_list.append(item)
        else:
            output_list.append('{0}_{1}'.format(item, i))
    return output_list

import re

def parse_hotkey(text):

    ret_val = [text, None, None] #Default return values
    if text is None:
        return ret_val

    # Single character, remain visible
    res = re.search('(?<=\[).(?=\])', text)
    if res:
        start = res.start(0)
        end = res.end(0)
        caption = text[:start-1]+text[start:end]+text[end+1:]
        ret_val = [caption, text[start:end], start-1]

    # Single character, hide it
    res = re.search('(?<=\[\[).(?=\]\])', text)
    if res:
        start = res.start(0)
        end = res.end(0)
        caption = text[:start-2]+text[end+2:]
        ret_val = [caption, text[start:end], None]

    # a Keysym.  Always hide it
    res = re.search('(?<=\[\<).+(?=\>\])', text)
    if res:
        start = res.start(0)
        end = res.end(0)
        caption = text[:start-2]+text[end+2:]
        ret_val = [caption, '<{}>'.format(text[start:end]), None]

    return ret_val



def __buttonEvent(event=None, buttons=None, virtual_event=None):
    # TODO: Replace globals with tkinter variables
    global boxRoot, __replyButtonText, rootWindowPosition

    # Determine window location and save to global
    m = re.match("(\d+)x(\d+)([-+]\d+)([-+]\d+)", boxRoot.geometry())
    if not m:
        raise ValueError("failed to parse geometry string: {}".format(boxRoot.geometry()))
    width, height, xoffset, yoffset = [int(s) for s in m.groups()]
    rootWindowPosition = '{0:+g}{1:+g}'.format(xoffset, yoffset)

    # print('{0}:{1}:{2}'.format(event, buttons, virtual_event))
    if virtual_event == 'cancel':
        for button_name, button in buttons.items():
            if 'cancel_choice' in button:
                __replyButtonText = button['original_text']
        __replyButtonText = None
        boxRoot.quit()
        return

    if virtual_event == 'select':
        text = event.widget.config('text')[-1]
        if not isinstance(text, basestring):
            text = ' '.join(text)
        for button_name, button in buttons.items():
            if button['clean_text'] == text:
                __replyButtonText = button['original_text']
                boxRoot.quit()
                return

    # Hotkeys
    if buttons:
        for button_name, button in buttons.items():
            hotkey_pressed = event.keysym
            if event.keysym != event.char: # A special character
                hotkey_pressed = '<{}>'.format(event.keysym)
            if button['hotkey'] == hotkey_pressed:
                __replyButtonText = button_name
                boxRoot.quit()
                return

    print("Event not understood")


def __put_buttons_in_buttonframe(choices, default_choice, cancel_choice):
    global buttonsFrame, cancel_invoke

    #TODO: I'm using a dict to hold buttons, but this could all be cleaned up if I subclass Button to hold
    #      all the event bindings, etc
    #TODO: Break __buttonEvent out into three: regular keyboard, default select, and cancel select.
    unique_choices = uniquify_list_of_strings(choices)
    # Create buttons dictionary and Tkinter widgets
    buttons = dict()
    for button_text, unique_button_text in zip(choices, unique_choices):
        this_button = dict()
        this_button['original_text'] = button_text
        this_button['clean_text'], this_button['hotkey'], hotkey_position = parse_hotkey(button_text)
        this_button['widget'] = Button(buttonsFrame,
                                       takefocus=1,
                                       text=this_button['clean_text'],
                                       underline=hotkey_position)
        this_button['widget'].pack(expand=YES, side=LEFT, padx='1m', pady='1m', ipadx='2m', ipady='1m')
        buttons[unique_button_text] = this_button
    # Bind arrows, Enter, Escape
    for this_button in buttons.values():
        bindArrows(this_button['widget'])
        for selectionEvent in STANDARD_SELECTION_EVENTS:
            this_button['widget'].bind("<{}>".format(selectionEvent),
                                       lambda e: __buttonEvent(e, buttons, virtual_event='select'),
                                       add=True)

    # Assign default and cancel buttons
    if cancel_choice in buttons:
        buttons[cancel_choice]['cancel_choice'] = True
    boxRoot.bind_all('<Escape>', lambda e: __buttonEvent(e, buttons, virtual_event='cancel'), add=True)
    boxRoot.protocol('WM_DELETE_WINDOW', lambda: __buttonEvent(None, buttons, virtual_event='cancel'))
    if default_choice in buttons:
        buttons[default_choice]['default_choice'] = True
        buttons[default_choice]['widget'].focus_force()
    # Bind hotkeys
    for hk in [button['hotkey'] for button in buttons.values() if button['hotkey']]:
         boxRoot.bind_all(hk, lambda e: __buttonEvent(e, buttons), add=True)

    return

class EgStore:
    def __init__(self, filename):  # obtaining filename is required
        self.filename = None
        raise NotImplementedError()

    def restore(self):
        if not os.path.exists(self.filename): return self
        if not os.path.isfile(self.filename): return self

        try:
            with open(self.filename, "rb") as f:
                unpickledObject = pickle.load(f)

            for key in list(self.__dict__.keys()):
                default = self.__dict__[key]
                self.__dict__[key] = unpickledObject.__dict__.get(key, default)
        except:
            pass

        return self

    def store(self):
        with open(self.filename, "wb") as f:
            pickle.dump(self, f)

    def kill(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)
        return

    def __str__(self):
        # find the length of the longest attribute name
        longest_key_length = 0
        keys = list()
        for key in self.__dict__.keys():
            keys.append(key)
            longest_key_length = max(longest_key_length, len(key))

        keys.sort()  # sort the attribute names
        lines = list()
        for key in keys:
            value = self.__dict__[key]
            key = key.ljust(longest_key_length)
            lines.append("%s : %s\n" % (key, repr(value)))
        return "".join(lines)  # return a string showing the attributes

package_dir = os.path.dirname(os.path.realpath(__file__))
