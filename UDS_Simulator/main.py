from tkinter import *
import customtkinter as tk
import ECU as sv
import tester as cl
import headerfile as hf
from PIL import Image

# Create a new window
root = tk.CTk()
root.geometry("800x600")
root.resizable(width=False, height=False)
root.iconbitmap("./media/car.ico")
root.title("UDS Simulator")
root.configure(bg='#FFA500')

# ----------------------------------------------------
# TOP FRAME with Images and Progress Bar
top_frame = tk.CTkFrame(root)
top_frame.pack(fill=tk.X, side=tk.TOP, pady=(10, 0))

# Load and display engine image
engine_image = tk.CTkImage(Image.open("./media/ECU.PNG"), size=(150, 150))
engine_label = tk.CTkLabel(top_frame, image=engine_image, text="")
engine_label.pack(side="left", padx=(30, 10))

# Load and display computer image
computer_image = tk.CTkImage(Image.open("./media/client.png"), size=(150, 150))
computer_label = tk.CTkLabel(top_frame, image=computer_image, text="")
computer_label.pack(side="right", padx=(10, 30))

# Create a Canvas for the animation
canvas = Canvas(top_frame, width=800, height=150)
canvas.pack(side="bottom", fill=tk.X, padx=25, pady=(10, 0))

# Envelope variable to hold the ID of the rectangle
envelope = None

# ----------------------------------------------------
# LEFT FRAME
left_frame = tk.CTkFrame(root, fg_color="blue")
left_frame.pack(side="left", fill=tk.Y, padx=(20, 5), pady=10)

# ECU Label
SERVER_label = tk.CTkLabel(left_frame, text="ECU", font=("Helvetica", 16, "bold"))
SERVER_label.pack(side="top", padx=10, pady=10, fill=tk.X)

# RX Message Label
RESPONSE_label = tk.CTkLabel(left_frame, text="RX Message:", font=("Helvetica", 12))
RESPONSE_label.pack(side="top", padx=10, pady=10, fill=tk.X)

# Textbox for response messages (adjusted height)
RESPONSE_textField = tk.CTkTextbox(left_frame, width=300, height=250)  # Adjust height here
RESPONSE_textField.pack(side="top", padx=10, pady=(0, 5))

# Clear Button
CLEAR_button = tk.CTkButton(left_frame, text="CLEAR", command=lambda: clear_response())
CLEAR_button.pack(side="top", padx=10, pady=(5, 10))  # Adjusting the padding for visibility)

# Function to clear response and reset LED button color
def clear_response():
    RESPONSE_textField.delete("1.0", "end")  # Clear the text box
    led_button.configure(fg_color="red")    # Reset LED button color to green
    status_label.configure(text="", text_color="black")  # Reset status label



# ----------------------------------------------------
# RIGHT FRAME
right_frame = tk.CTkFrame(root, fg_color="Yellow")
right_frame.pack(side="right", fill=tk.BOTH, padx=(5, 20), pady=10)

# Client Label
client_label = tk.CTkLabel(right_frame, text="Client", font=("Helvetica", 16, "bold"))
client_label.pack(side="top", pady=(10, 5))

# Manual Frame
manual_frame = tk.CTkFrame(right_frame)
manual_frame.pack(padx=10, pady=10)

# PCI Frame
PCI_frame = tk.CTkFrame(manual_frame)
PCI_frame.pack(side="top", fill=tk.X, padx=10, pady=5)
PCI_label = tk.CTkLabel(PCI_frame, text="PCI", font=("Helvetica", 12))
PCI_label.pack(side="left", padx=10)
PCI_textField = tk.CTkTextbox(PCI_frame, width=100, height=10)
PCI_textField.pack(side="right", padx=10)

# SID Frame
SID_frame = tk.CTkFrame(manual_frame)
SID_frame.pack(side="top", fill=tk.X, padx=10, pady=5)
SID_label = tk.CTkLabel(SID_frame, text="SID", font=("Helvetica", 12))
SID_label.pack(side="left", padx=10)
SID_options = list(hf.SID.keys())
SID_key = tk.StringVar()
SID_dropdown = tk.CTkOptionMenu(SID_frame, variable=SID_key, values=SID_options, width=100)
SID_dropdown.pack(side="right", padx=10)

# DID/SUB Frame
DID_SUB_frame = tk.CTkFrame(manual_frame)
DID_SUB_frame.pack(side="top", fill=tk.X, padx=10, pady=5)
DID_SUB_key = tk.StringVar()
DID_SUB_options = ["DID", "SUB"]
DID_SUB_dropdown = tk.CTkOptionMenu(DID_SUB_frame, variable=DID_SUB_key, values=DID_SUB_options, width=80)
DID_SUB_dropdown.pack(side="left", padx=5)
DID_SUB_textField = tk.CTkTextbox(DID_SUB_frame, width=100, height=10)
DID_SUB_textField.pack(side="right", padx=10)

# DATA Frame
DATA_frame = tk.CTkFrame(manual_frame)
DATA_frame.pack(side="top", fill=tk.X, padx=10, pady=5)
DATA_label = tk.CTkLabel(DATA_frame, text="DATA", font=("Helvetica", 12))
DATA_label.pack(side="left", padx=10)
DATA_textField = tk.CTkTextbox(DATA_frame, width=100, height=10)
DATA_textField.pack(side="right", padx=10)

# Send Button
send_button = tk.CTkButton(right_frame, text="SEND", command=lambda: clientRun())
send_button.pack(side="bottom", padx=10, pady=(10, 20))

# ----------------------------------------------------
# LED BUTTON (between left and right frames)
led_button = tk.CTkButton(root, text="", width=20, height=20, fg_color="red")
led_button.place(relx=0.5, rely=0.5, anchor="center")

# Status Message Label
status_label = tk.CTkLabel(root, text="", font=("Helvetica", 12, "bold"))
status_label.place(relx=0.55, rely=0.55, anchor="center")


# ----------------------------------------------------
# Function Definitions
def update_led(status):
    """Update the LED button color based on communication status and display a message."""
    if status:
        led_button.configure(fg_color="green")
        status_label.configure(text="Communication is done!", text_color="green")
    else:
        led_button.configure(fg_color="red")
        status_label.configure(text="Communication Failed!", text_color="red")


def serverRun():
    sv.readMessage()
    sv.readSession()
    response = ""

    flagS = 0
    for i in range(0, 5):
        if sv.stored_SID[i] == sv.fr[1]:
            flagS = 1
            break

    if flagS:
        if sv.fr[1] == 0x10:
            if sv.fr[2] == 0x02 and sv.currentSession == 0x01:
                response += sv.session_change_fail()
                update_led(False)  # Communication failed
            else:
                response += sv.session_change_pass()
                sv.writeSession()
                update_led(True)  # Communication successful
        elif sv.fr[1] == 0x11:
            response += sv.ecu_reset_sequence()
            update_led(True)  # Communication successful
        elif sv.fr[1] == 0x22:
            response += sv.service_present_RDBI()
            update_led(True)  # Communication successful
        elif sv.fr[1] == 0x2E:
            response += sv.service_present_WDBI()
            update_led(True)  # Communication successful
    else:
        response += sv.service_not_supported()
        update_led(False)  # Communication failed

    response += sv.displayFrame(sv.fr)
    RESPONSE_textField.insert(INSERT, response)


def clientRun():
    PCI = PCI_textField.get(1.0, "end-1c")
    SID = SID_key.get()
    DID_SUB = DID_SUB_key.get()
    DID_SUB_VAL = DID_SUB_textField.get(1.0, "end-1c")
    DATA = DATA_textField.get(1.0, "end-1c")

    if PCI == "" or SID == "" or DID_SUB == "" or DATA == "":
        print("error")
        return

    hf.fr[0] = int(PCI, 16)
    hf.fr[1] = hf.SID[SID]

    if DID_SUB == "DID":
        hf.fr[2] = int(DID_SUB_VAL, 16) >> 8
        hf.fr[3] = int(DID_SUB_VAL, 16) & 0xff
        hf.fr[4] = int(DATA, 16)
        hf.fr[5] = 0x00
        hf.fr[6] = 0x00
        hf.fr[7] = 0x00
    else:
        hf.fr[2] = int(DID_SUB_VAL, 16)
        hf.fr[3] = int(DATA, 16)
        hf.fr[4] = 0x00
        hf.fr[5] = 0x00
        hf.fr[6] = 0x00
        hf.fr[7] = 0x00
    hf.displayFrame(hf.fr)

    cl.fr = hf.fr
    RESPONSE_textField.insert(INSERT, '\n\nFRAME RECEIVED:')
    RESPONSE_textField.insert(INSERT, cl.displayFrame(cl.fr) + '\n')
    cl.writeMessage()

    reset_and_animate_envelope()  # Reset and start the envelope animation
    serverRun()


# Animation function
def reset_and_animate_envelope():
    global envelope
    canvas.delete(envelope)  # Remove the previous envelope (rectangle)

    # Create a new envelope (rectangle) starting near the computer
    envelope = canvas.create_rectangle(720, 70, 770, 120, fill="blue")

    # Move the envelope all the way from the computer to the engine (from right to left)
    for x in range(0, 710, 10):  # Adjust the range to cover more distance
        canvas.move(envelope, -10, 0)  # Move left by 10 pixels
        canvas.update()  # Update the canvas
        root.after(50)  # Pause for 50 milliseconds

    # Check if the envelope is at the engine position
    if canvas.coords(envelope)[0] <= 150:  # Assuming engine is at x=150
        canvas.delete(envelope)  # Remove the envelope once it reaches the engine


# Run the main event loop
root.mainloop()
