import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import pandas as pd
import os
import pyttsx3

# Initialize text-to-speech engine
engine = pyttsx3.init()

class ColorDetectionChatbot:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Detection Chatbot")
        self.create_widgets()
        
        # Load the colors CSV file
        index = ["color", "color_name", "hex", "R", "G", "B"]
        csv_file_path = r'C:\Users\SHAIKH\Desktop\color detection\colors.csv'  # Update with the correct path
        if os.path.isfile(csv_file_path):
            self.csv = pd.read_csv(csv_file_path, names=index, header=None)
        else:
            self.csv = None
            messagebox.showerror("Error", f"CSV file not found: {csv_file_path}")
        
        # Global variables
        self.canvas = None
        self.img = None
        self.photo = None
        self.color_info_label = None
        
        # Display the welcome message
        self.display_welcome_message()

    def create_widgets(self):
        # Create the label at the top
        self.title_label = tk.Label(self.root, text="Color Detection Chatbot", font=("Arial", 44), bg="blue", fg="white", height=2)
        self.title_label.pack(fill=tk.BOTH, pady=10)
        
        # Create a frame for the chat display and scrollbar
        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create the scrollbar
        self.scrollbar = tk.Scrollbar(self.chat_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create the text area for queries and responses
        self.chat_display = tk.Text(self.chat_frame, wrap=tk.WORD, yscrollcommand=self.scrollbar.set)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.scrollbar.config(command=self.chat_display.yview)
        
        # Create the entry widget for user input
        self.user_input = tk.Entry(self.root, font=("Arial", 24))
        self.user_input.pack(fill=tk.X, padx=10, pady=5)
        self.user_input.bind("<Return>", self.handle_query)
        
        # Create a frame for the buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create the "Open Image" button
        self.open_image_button = tk.Button(self.button_frame, text="Open Image", font=("Arial", 18), bg="violet", fg="black", height=2, width=20, command=self.open_image)
        self.open_image_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create the "Camera" button
        self.camera_button = tk.Button(self.button_frame, text="Camera", font=("Arial", 18), bg="yellow", fg="black", height=2, width=20, command=self.open_camera)
        self.camera_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create the "Send" button
        self.send_button = tk.Button(self.button_frame, text="Send", font=("Arial", 18), bg="red", fg="black", height=2, width=20, command=self.handle_query)
        self.send_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def display_welcome_message(self):
        welcome_message = (
            "Hello, I am Color Detection Chatbot. You can ask me questions like:\n"
            "what is the hex code of color_name?\n"
            "what is the name of the color with hex code #ffffff?\n"
        )
        self.insert_chat_message("Bot", welcome_message, "blue", "white")

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", ".jpg;.jpeg;*.png")])
        if not file_path:
            return
        
        self.img = cv2.cvtColor(cv2.imread(file_path), cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(self.img)
        self.photo = ImageTk.PhotoImage(image=img_pil)
        
        # Create a new window for displaying the image
        self.image_window = tk.Toplevel(self.root)
        self.image_window.title("Selected Image")
        
        canvas = tk.Canvas(self.image_window, width=self.img.shape[1], height=self.img.shape[0])
        canvas.pack(padx=10, pady=10)
        
        canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        canvas.bind("<Button-1>", self.on_canvas_click)
    
    def open_camera(self):
        cap = cv2.VideoCapture(0)  # Open the camera
        if not cap.isOpened():
            messagebox.showerror("Error", "Failed to open camera.")
            return
        
        self.camera_window = tk.Toplevel(self.root)
        self.camera_window.title("Camera")
        
        # Create canvas for displaying camera feed
        self.camera_canvas = tk.Canvas(self.camera_window, width=640, height=480)  # Adjust dimensions as needed
        self.camera_canvas.pack(padx=10, pady=10)
        
        # Define frame variable as nonlocal
        self.frame = None
        
        def update_camera_feed():
            nonlocal cap
            ret, frame = cap.read()  # Read current frame from camera
            if ret:
                # Convert frame from BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Resize frame if needed to fit the canvas
                frame_resized = cv2.resize(frame_rgb, (640, 480))  # Adjust dimensions as needed
                
                # Display the frame on canvas
                img_pil = Image.fromarray(frame_resized)
                self.photo = ImageTk.PhotoImage(image=img_pil)
                self.camera_canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                
                # Assign frame to instance variable for access in on_camera_click
                self.frame = frame_resized
            
            self.camera_window.after(10, update_camera_feed)  # Update every 10 milliseconds
        
        update_camera_feed()  # Start the camera feed update
        
        # Close the camera when the camera window is closed
        def close_camera_window():
            cap.release()
            self.camera_window.destroy()
        
        self.camera_window.protocol("WM_DELETE_WINDOW", close_camera_window)
        
        # Function to handle mouse clicks on camera canvas
        def on_camera_click(event):
            x, y = event.x, event.y
            # Convert canvas coordinates to frame coordinates
            if self.frame is not None:
                scale_x = cap.get(cv2.CAP_PROP_FRAME_WIDTH) / self.camera_canvas.winfo_width()
                scale_y = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / self.camera_canvas.winfo_height()
                frame_x = int(x * scale_x)
                frame_y = int(y * scale_y)
                
                # Get color at the clicked position in the frame
                if 0 <= frame_x < self.frame.shape[1] and 0 <= frame_y < self.frame.shape[0]:
                    b, g, r = self.frame[frame_y, frame_x]
                    color_name = self.get_color_name(r, g, b)
                    color_info = f"Color: {color_name}, R={r}, G={g}, B={b}"
                    
                    # Remove any existing label
                    if self.color_info_label is not None:
                        self.color_info_label.destroy()
                    
                    # Create a new label on the canvas
                    self.color_info_label = tk.Label(self.camera_window, text=color_info, font=("Arial", 14), bg="white", fg="black")
                    self.color_info_label.place(x=x, y=y, anchor=tk.CENTER)
                    self.color_info_label.update()  # Force update to reduce delay
                    
                    # Speak the color information
                    engine.say(color_info)
                    engine.runAndWait()
                    
                    # Display color information on console or update GUI as needed
                    print(color_info)
        
        # Bind mouse click event to camera canvas
        self.camera_canvas.bind("<Button-1>", on_camera_click)

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        r, g, b = self.img[y, x]  # img is already in RGB format
        color_name = self.get_color_name(r, g, b)
        color_info = f"Color: {color_name}, R={r}, G={g}, B={b}"
        
        # Remove any existing label
        if self.color_info_label is not None:
            self.color_info_label.destroy()
        
        # Create a new label on the canvas
        self.color_info_label = tk.Label(self.image_window, text=color_info, font=("Arial", 14), bg="white", fg="black")
        self.color_info_label.place(x=x, y=y, anchor=tk.CENTER)
        self.color_info_label.update()  # Force update to reduce delay
        
        # Speak the color information
        engine.say(color_info)
        engine.runAndWait()

    def get_color_name(self, R, G, B):
        if self.csv is None:
            return "Unknown"
        minimum = 10000
        cname = ""
        for i in range(len(self.csv)):
            d = abs(R - int(self.csv.loc[i, "R"])) + abs(G - int(self.csv.loc[i, "G"])) + abs(B - int(self.csv.loc[i, "B"]))
            if d <= minimum:
                minimum = d
                cname = self.csv.loc[i, "color_name"]
        return cname

    def handle_query(self, event=None):
        user_query = self.user_input.get().lower()
        self.user_input.delete(0, tk.END)
        
        # Insert user query into chat display
        self.insert_chat_message("You", user_query, "black", "white")
        
        # Identify the type of query and process it
        if "hex code of" in user_query:
            color_name = user_query.split("hex code of")[1].strip().lower()
            hex_value = self.get_hex_value(color_name)
            if hex_value:
                bot_response = f"The hex code of {color_name} color is {hex_value}."
            else:
                bot_response = f"Sorry, I don't have the hex code for {color_name} color."

        elif "name of the color with hex code" in user_query:
            hex_value = user_query.split("hex code")[1].strip().lower()
            color_name = self.get_color_name_by_hex(hex_value)
            if color_name:
                bot_response = f"The name of the color with hex code {hex_value} is {color_name}."
            else:
                bot_response = f"Sorry, I don't have the name for the color with hex code {hex_value}."
                
        else:
            bot_response = "I can help you open an image, detect colors, or provide information about colors. You can ask for the hex code of a color or the name of a color by specifying the hex code."

        # Insert bot response into chat display
        self.insert_chat_message("Bot", bot_response, "white", "black")
        
        # Speak the bot response
        engine.say(bot_response)
        engine.runAndWait()

    def insert_chat_message(self, sender, message, bg_color, fg_color):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {message}\n", f"{bg_color}.{fg_color}")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def get_hex_value(self, color_name):
        if self.csv is None:
            return None
        row = self.csv[self.csv['color_name'].str.lower() == color_name]
        if not row.empty:
            return row.iloc[0]['hex']
        else:
            return None

    def get_color_name_by_hex(self, hex_value):
        if self.csv is None:
            return None
        row = self.csv[self.csv['hex'].str.lower() == hex_value]
        if not row.empty:
            return row.iloc[0]['color_name']
        else:
            return None

if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.geometry("800x600")
        app = ColorDetectionChatbot(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Startup Error", f"An error occurred during startup:\n{e}")
