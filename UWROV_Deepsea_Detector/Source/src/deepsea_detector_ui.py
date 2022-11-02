"""User interface for running video detection and tracking inference."""

# pylint: disable=line-too-long
# pylint: disable=consider-use-f-string
from datetime import datetime
from functools import partial
from queue import Empty, Queue
import subprocess
from threading import Thread
from tkinter import *  # pylint: disable=wildcard-import disable=unused-wildcard-import
from tkinter import ttk
from tkinter import filedialog
import tkinter
from typing import List, Tuple
from PIL import ImageTk, Image, ImageDraw, ImageFont
import torch
import os

from detection import format_seconds

MIN_WIDTH = 600
MIN_HEIGHT = 600

VERSION = "1.0"

DIR_NAME = os.path.dirname(__file__)
MODEL_DEFAULT_PATH =  os.path.join(DIR_NAME,
                                   "../../Models/deepsea-detector.pt")
INFERENCE_SCRIPT_RELATIVE_PATH = "detection.py"
INFERENCE_SCRIPT_PATH = os.path.join(DIR_NAME, INFERENCE_SCRIPT_RELATIVE_PATH)
SPLASH_IMAGE_RELATIVE_PATH = "assets/splash.jpg"
SPLASH_IMAGE_PATH = os.path.join(DIR_NAME, SPLASH_IMAGE_RELATIVE_PATH)
FONTS_PATH = os.path.join(DIR_NAME, "assets/OpenSans-Light.ttf")
FONTS_PATH_ITALICS = os.path.join(DIR_NAME, "assets/OpenSans-MediumItalic.ttf")


# From https://stackoverflow.com/questions/665566/redirect-command-line-results-to-a-tkinter-gui
def iter_except(function, exception):
    """Works like builtin 2-argument `iter()`, but stops on `exception`."""
    try:
        while True:
            yield function()
    except exception:
        return


def cmdlist_to_cmd_string(cmdlist: List) -> str:
    ret = ""
    for term in cmdlist:
        if isinstance(term, str):
            # Wrap with quotations if there are spaces in it
            if term.find(" ") != -1:
                ret += "'{}' ".format(term)
            else:
                ret += term + " "
        else:
            ret += str(term) + " "
    return ret[0:-1]


class InferenceUI:
    """The user interface for running tracking and inference."""
    file_entry_width = 24

    def __init__(self, root):
        self.root = root
        root.title("Deepsea-Detector UI")
        root.minsize(MIN_WIDTH, MIN_HEIGHT)

        self.inference_process = None
        self.start_timestamp = datetime.now()
        label_padding = ("3 3 3 3")

        # Create frame widget
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        mainframe.columnconfigure(1, weight=1)

        # Splash Screen
        splash_image_src = Image.open(SPLASH_IMAGE_PATH)
        # Get image aspect ratio

        image_aspect_ratio_w_h = splash_image_src.width / splash_image_src.height
        splash_height = int(MIN_WIDTH // image_aspect_ratio_w_h)
        splash_frame = ttk.Frame(mainframe, height=splash_height)
        splash_frame.grid(column=1, row=0, sticky=(W, N, E))        

        splash_image_src = splash_image_src.resize((MIN_WIDTH, splash_height), Image.LANCZOS)
        # Add project name label
        draw = ImageDraw.Draw(splash_image_src)
        font = ImageFont.truetype(FONTS_PATH, 40)
        font_italic = ImageFont.truetype(FONTS_PATH_ITALICS, 12)
        draw.text((10,0), "Deepsea-Detector v" + VERSION, (225,225,225), font=font)
        draw.text((12,50), "Image courtesy of NOAA Ocean Exploration", (225, 225, 225), font=font_italic)

        splash_image = ImageTk.PhotoImage(splash_image_src)
        splash_label = tkinter.Label(splash_frame, image=splash_image)
        splash_label.image = splash_image
        splash_label.place(relx=0, rely=0)

        # ===================
        # INPUT
        # ===================
        # Create a labelframe for the input
        input_frame = ttk.Labelframe(
            mainframe, text="Input", padding="3 3 12 12")
        # Defines location on the main UI grid
        input_frame.grid(column=1, row=1, sticky=(N, E, W, S))
        # Makes the entry fill up any available space
        input_frame.columnconfigure(2, weight=1)

        # Video input label, entry, and button
        ttk.Label(input_frame, text="Video Input:", padding=label_padding).grid(
            column=1, row=1, sticky=NW)
        self.video_in = StringVar()  # String variable that can be read/accessed by Tk
        video_in_entry = ttk.Entry(
            input_frame, width=InferenceUI.file_entry_width, textvariable=self.video_in)
        video_in_entry.grid(column=2, row=1, sticky=(W, E))
        # Defines button that opens a file browser when pressed
        video_in_button = ttk.Button(
            input_frame, text="Browse", command=partial(self.browse, self.video_in))
        video_in_button.grid(column=3, row=1, sticky=W)

        # ===================
        # OUTPUT
        # ===================
        out_frame = ttk.LabelFrame(
            mainframe, text="Output", padding="3 3 12 12")
        out_frame.grid(column=1, row=2, sticky=(N, E, W, S))
        out_frame.columnconfigure(2, weight=1)

        # Video output label, entry, and button
        ttk.Label(out_frame, text="Video Output:", padding=label_padding)\
            .grid(column=1, row=1, sticky=NW)
        # String variable that can be read/accessed by Tk
        self.video_out = StringVar(value="out.mp4")
        video_out_entry = ttk.Entry(out_frame,
                                    width=InferenceUI.file_entry_width,
                                    textvariable=self.video_out)
        video_out_entry.grid(column=2, row=1, sticky=(W, E))
        # Button command, when pressed asks for save location of MP4 file
        video_out_button_cmd = partial(
            self.save_as, self.video_out, self.video_out.get(), [("MP4", ".mp4")])
        video_out_button = ttk.Button(
            out_frame, text="Browse", command=video_out_button_cmd)
        video_out_button.grid(column=3, row=1, sticky=W)
        ttk.Label(out_frame, text="Saves a video showing identifications and inferences made.")\
            .grid(column=2, row=2, sticky=W)

        # CSV output label, entry, and button
        ttk.Label(out_frame, text="CSV Output:", padding=label_padding)\
            .grid(column=1, row=3, sticky=NW)
        # String variable that can be read/accessed by Tk
        self.csv_out = StringVar(value="out.csv")
        csv_out_entry = ttk.Entry(out_frame,
                                  width=InferenceUI.file_entry_width,
                                  textvariable=self.csv_out)
        csv_out_entry.grid(column=2, row=3, sticky=(W, E))
        # Gets save location for CSV file
        csv_out_button_cmd = partial(self.save_as, self.csv_out, self.csv_out.get(), [
                                     ("Comma Separated Value File", ".csv")])
        csv_out_button = ttk.Button(
            out_frame, text="Browse", command=csv_out_button_cmd)
        csv_out_button.grid(column=3, row=3, sticky=W)
        ttk.Label(out_frame, text="Comma separated value file of all detected organisms.").grid(
            column=2, row=4, sticky=W)

        # ===================
        # MODEL CONFIGURATION
        # ===================
        ml_frame = ttk.Labelframe(
            mainframe, text="ML Model Configuration", padding="3 3 12 12")
        ml_frame.grid(column=1, row=3, sticky=(N, E, W, S))
        ml_frame.columnconfigure(2, weight=1)

        # Model Weights (.pt)
        ttk.Label(ml_frame, text="YOLO Model:", padding=label_padding)\
            .grid(column=1, row=1, sticky=NW)
        if (os.path.exists(MODEL_DEFAULT_PATH)):
            self.ml_model_weights = StringVar(value=MODEL_DEFAULT_PATH)
        else:
            self.ml_model_weights = StringVar()
        ttk.Entry(ml_frame, width=InferenceUI.file_entry_width, textvariable=self.ml_model_weights)\
            .grid(column=2, row=1, sticky=(W, E))
        ml_browse_command = partial(self.browse,
                                    self.ml_model_weights,
                                    ".pt",
                                    [("PyTorch Model", ".pt")])
        ml_model_button = ttk.Button(
            ml_frame, text="Browse", command=ml_browse_command)
        ml_model_button.grid(column=3, row=1, sticky=W)
        ttk.Label(ml_frame, text="The YOLOv5 detection Models to use.")\
            .grid(column=2, row=2, sticky=W)

        # Period/Stride Entry
        ttk.Label(ml_frame, text="Period:", padding=label_padding).grid(
            column=1, row=3, sticky=NW)
        self.period = IntVar(value=3)
        ttk.Entry(ml_frame, width=3, textvariable=self.period)\
            .grid(column=2, row=3, sticky=(W))
        period_label = ttk.Label(ml_frame, text="How often, in frames, to run the detection algorithm.\nHigher values can speed up processing but may decrease accuracy.\n(default is 3)")
        period_label.grid(column=2, row=4, sticky=W)

        # Use GPU
        ttk.Label(ml_frame, text="Use GPU:", padding=label_padding).grid(
            column=1, row=5, sticky=NW)
        self.use_gpu = BooleanVar(value=torch.cuda.is_available())
        self.gpu_checkbox = ttk.Checkbutton(ml_frame, variable=self.use_gpu)
        self.gpu_checkbox.grid(column=2, row=5, sticky=W)

        # Enable/disable GPU checkbox based on CUDA device availability
        if torch.cuda.is_available():
            self.gpu_checkbox["state"] = "enable"
        else:
            self.gpu_checkbox["state"] = "disabled"
            ttk.Label(ml_frame, text="No GPU detected.", padding=label_padding).grid(
                column=2, row=6, sticky=NW)
        # Show classes
        ttk.Label(ml_frame, text="Show Class Preview:", padding=label_padding).grid(
            column=1, row=7, sticky=NW)
        self.show_class = BooleanVar(value=False)
        self.show_class_checkbox = ttk.Checkbutton(ml_frame, variable=self.show_class)
        self.show_class_checkbox.grid(column=2, row=7, sticky=W)

        # RUN INFERENCE
        cmd_output_buffer = Queue(maxsize=1024)  # Buffer for output from any running commands.
        run_inference_command = partial(self.run_inference, cmd_output_buffer)
        self.run_inference_button = ttk.Button(mainframe,
                                               text="Run Inference",
                                               width=24,
                                               command=run_inference_command)
        self.run_inference_button.grid(column=1, row=4, sticky=(E))

        # Text area for command output
        cmd_frame = ttk.LabelFrame(mainframe, text='Inference Output')
        cmd_frame.grid(column=1, row=5, sticky=(N, E, W, S))
        cmd_frame.columnconfigure(1, weight=1)
        cmd_frame.rowconfigure(1, weight=1)
        mainframe.rowconfigure(5, weight=1)

        self.cmd_output_area = Text(cmd_frame, wrap=NONE, bd=0, height=6)
        self.cmd_output_area.grid(column=1, row=1, sticky=(N, E, W, S))
        # Add scrollbars
        y_scroll = Scrollbar(cmd_frame, orient="vertical", command=self.cmd_output_area.yview)
        y_scroll.grid(column=2, row=1, sticky=(N, S))
        x_scroll = Scrollbar(cmd_frame, orient="horizontal", command=self.cmd_output_area.xview)
        x_scroll.grid(column=1, row=2, sticky=(W, E))
        self.cmd_output_area['yscrollcommand'] = y_scroll.set
        self.cmd_output_area['xscrollcommand'] = x_scroll.set
        # Configure colors for error and info tags
        self.cmd_output_area.tag_config("errorstring", foreground="#CC0000")
        self.cmd_output_area.tag_config("infostring", foreground="#008800")

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        # Sets up a keybind for running the inference automatically.
        root.bind("<Return>", self.run_inference)
        self.update(cmd_output_buffer)

    def browse(self, target: StringVar, default_extension: str = "", filetypes: List[Tuple[str, str]] = list()):
        "Opens a file dialog and sets the given target StringVar to the selected file path."
        file_path = filedialog.askopenfilename(filetypes=filetypes,
                                               defaultextension=default_extension)
        if file_path != "" and file_path is not None:
            target.set(file_path)

    def save_as(self, target: StringVar, default_path: str, extension: List[Tuple[str, str]] = list()):
        "Opens a file save dialog and sets the given StringVar to that file path."
        file_path = filedialog.asksaveasfilename(
            initialfile=default_path, filetypes=extension)
        if file_path != "" and file_path is not None: # Don't change if cancelled
            target.set(file_path)

    def get_default_tags(self, line):
        """return a tuple of tags to be applied to the line of text 'line'
           when being added to the text widet"""
        l = line.lower()
        if "error" in l or "traceback" in l:
            return ("errorstring", )
        return ()

    # Adapted from https://www.executionunit.com/blog/2012/10/26/using-python-and-tkinter-to-capture-script-output/
    def add_cmd_output(self, str, tags=None):
        """Add a line of text to the cmd output. If tags is None then
        self.get_default_tags will be used to assign tags to the line"""
        self.cmd_output_area.insert(INSERT, str, tags or self.get_default_tags(str))
        self.cmd_output_area.yview(END)

    # Adapted from https://stackoverflow.com/questions/665566/redirect-command-line-results-to-a-tkinter-gui
    def cmd_reader_thread(self, cmd_output_buffer: Queue):
        "Reads the command output while the inference subprocess is running."
        try:
            with self.inference_process.stdout as pipe:
                for line in iter(pipe.readline, b''):
                    cmd_output_buffer.put(line)
        finally:
            cmd_output_buffer.put(None)  # signal that the process is completed

    def update(self, cmd_output_buffer: Queue):
        "Update loop for the InferenceUI."

        if self.inference_process is not None:  # We are currently running inference
            # Dump buffer into the cmd output text area
            for line in iter_except(cmd_output_buffer.get_nowait, Empty):
                if line:
                    # Update command output with new line
                    self.add_cmd_output(line)
            
            # Check if process finished, if so
            returncode = self.inference_process.poll()
            if returncode is not None:
                end_timestamp = datetime.now()
                end_timestamp_s = end_timestamp.strftime("%H:%M:%S")
                if returncode == 0:
                    self.add_cmd_output("\nInference job finished successfully at time {} (returncode 0).".format(end_timestamp_s))
                if self.inference_process.poll() > 0:
                    self.add_cmd_output("\nERROR: Inference job encountered an error at time {} (returncode {}).\n".format(end_timestamp_s, returncode))
                time_elapsed = end_timestamp - self.start_timestamp
                
                self.add_cmd_output("Time elapsed: {}\n".format(format_seconds(time_elapsed.total_seconds())))
                self.inference_process = None

        # Disable Run Inference button if there's an existing process running.
        if self.inference_process:
            self.run_inference_button["state"]="disabled"
        else:
            self.run_inference_button["state"]="enabled"

        # Run next update
        self.root.after(40, self.update, cmd_output_buffer)

    # Adapted from https://www.executionunit.com/blog/2012/10/26/using-python-and-tkinter-to-capture-script-output/
    def run_inference(self, cmd_output_buffer: Queue):
        "Starts inference calculations, using the input settings."
        # Set up script variables        
        video_in_path = self.video_in.get()
        video_out_path = self.video_out.get()
        csv_out_path = self.csv_out.get()
        model_path = self.ml_model_weights.get()
        period = self.period.get()
        device = "cuda" if self.use_gpu.get() else "cpu"

        # Check variables and abort if incomplete.
        if video_in_path == "":
            self.add_cmd_output("ERROR: Missing input video.\n")
            return
        if model_path == "":
            self.add_cmd_output("ERROR: Missing YOLO detection Models.\n")
            return

        if period <= 0:
            self.add_cmd_output("ERROR: Period must be a positive integer. Setting to default (1).")
            period = 0

        # Format command
        cmdlist = [
            "python",
            INFERENCE_SCRIPT_PATH,
            video_in_path,
            "--detector_path", model_path,
            "--output_video", video_out_path,
            "--output_csv", csv_out_path,
            "--period", str(period),
            "--device", device,
            "--conf_thres", str(0.05),
            "--show_preview",
            ]
        if self.show_class.get():
            cmdlist.append("--show_classes")

        # Clear text area, move cursor to end
        # self.cmd_output_area.delete("1.0", END)
        self.cmd_output_area.mark_set("insert", END)

        self.start_timestamp = datetime.now()
        self.add_cmd_output("\n------------------------------\n")
        self.add_cmd_output("Starting new inference job at time {}.\n".format(self.start_timestamp.strftime("%H:%M:%S")))
        self.add_cmd_output("Running inference script with the following command:\n")
        self.add_cmd_output(cmdlist_to_cmd_string(cmdlist) + "\n\n")
        self.add_cmd_output("Setting up...\n")

        # Start the inference thread
        self.inference_process = subprocess.Popen(cmdlist,
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.STDOUT,
                                                  universal_newlines=True)
        # Start a thread to receive process output
        reader_thread = Thread(target=self.cmd_reader_thread, args=[cmd_output_buffer])
        reader_thread.daemon = True # Flags as a daemon thread, so it will close at shutdown
        reader_thread.start()

    def quit(self):
        "Closes running processes and the program."
        if self.inference_process is not None:
            self.inference_process.kill()
        self.root.destroy()

root = Tk()
app = InferenceUI(root)
root.protocol("WM_DELETE_WINDOW", app.quit)
root.mainloop()
