import vosk
import pyaudio
import pyautogui
import tkinter as tk
from tkinter import font

def recognize_microphone(model_path):
    model = vosk.Model(model_path)
    recognizer = vosk.KaldiRecognizer(model, 16000)

    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    def on_closing():
        # Function to be called when the Tkinter window is closed
        stream.stop_stream()
        stream.close()
        p.terminate()
        root.destroy()

    root = tk.Tk()
    root.title("Speech Recognition")
    # Calculate the center position of the screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_position = (screen_width - 450) // 2  # Adjust 450 based on your window width
    y_position = (screen_height - 300) // 2  # Adjust 300 based on your window height

    root.geometry(f"450x300+{x_position}+{y_position}")

    custom_font = font.Font(family="Helvetica", size=12, weight="bold")

    text_section = tk.Label(root, text="Command List", font=custom_font)
    text_section.pack()
    text_section = tk.Label(root, text="\nRight: Move right\nLeft: Move left\nUp: Move up\nDown: Move down\nStop: Stop moving\nClick: Left Click\nOptions: Right Click\nDouble: Double click\nAbove: Scroll up\nBelow: Scroll down\n", justify="left")
    text_section.pack()
    root.protocol("WM_DELETE_WINDOW", on_closing)  # Bind the window closing event

    current_command = None

    while True:
        data = stream.read(8000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            print(result)
            current_command = process_command(result, current_command, stream, recognizer)

        root.update()  # Update the Tkinter window

    print("Final Result:")
    print(recognizer.FinalResult())

def process_command(result, current_command, stream, recognizer):
    # Process the recognized speech result and control the cursor
    command = result.lower()

    if "up" in command and current_command != "up":
        current_command = "up"
        move_continuous(0, -20, stream, recognizer)  # Move the cursor up continuously
    elif "down" in command and current_command != "down":
        current_command = "down"
        move_continuous(0, 20, stream, recognizer)   # Move the cursor down continuously
    elif "left" in command and current_command != "left":
        current_command = "left"
        move_continuous(-20, 0, stream, recognizer)  # Move the cursor left continuously
    elif "right" in command and current_command != "right":
        current_command = "right"
        move_continuous(20, 0, stream, recognizer)   # Move the cursor right continuously
    elif "stop" in command:
        current_command = None
        pyautogui.moveTo(pyautogui.position())  # Stop the cursor movement
    elif "click" in command:
        current_command = "click"
        pyautogui.click(button="left")
    elif "options" in command:
        current_command = "options"
        pyautogui.click(button="right")
    elif "double" in command:
        current_command = "double"
        pyautogui.click(button="left")
        pyautogui.click(button="left")
    elif "above" in command:
        current_command = "scroll above"
        pyautogui.scroll(200)
    elif "below" in command:
        current_command = "scroll below"
        pyautogui.scroll(-200)
    return current_command

def move_continuous(x_offset, y_offset, stream, recognizer):
    # Move the cursor continuously for 10 seconds or until a new command is detected
    start_time = pyautogui.time.time()
    end_time = start_time + 10  # Duration in seconds

    while pyautogui.time.time() < end_time:
        if interrupt_movement(stream, recognizer):
            break
        pyautogui.move(x_offset, y_offset, duration=0.4)

def interrupt_movement(stream, recognizer):
    valid_commands = {"right", "left", "up", "down", "stop"}
    # Check if a new command is detected to interrupt the continuous movement
    data = stream.read(8000)
    if recognizer.AcceptWaveform(data):
        result = recognizer.Result()
        print("Interrupting:", result)
        process_command(result, None, stream, recognizer)  # Update current_command immediately
        return True
    return False

if __name__ == "__main__":
    model_path = "./vosk-model-small-en-us-0.15"
    recognize_microphone(model_path)