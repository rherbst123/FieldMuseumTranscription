import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import base64
import anthropic
import requests
from PIL import Image, ImageTk
from io import BytesIO
import subprocess
import sys

class FullScreenImage:
    def __init__(self, master, image):
        self.master = master
        self.original_image = image
        self.top = tk.Toplevel(master)
        self.top.title("Image on the Side")
        
        # Get the screen width and height
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        
        # Set initial window size to 80% of the screen size
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # Center the window on the screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.top.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Allow window resizing
        self.top.resizable(True, True)
        
        self.canvas = tk.Canvas(self.top)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind resize event
        self.top.bind('<Configure>', self.resize_image)
        
        # Bind mouse wheel for zooming
        self.top.bind('<MouseWheel>', self.zoom)  # For Windows
        self.top.bind('<Button-4>', self.zoom)    # For Linux (scroll up)
        self.top.bind('<Button-5>', self.zoom)    # For Linux (scroll down)
        
        # Bind right-click for closing
        self.top.bind('<Button-3>', self.close)
        
        self.scale = 1.0
        self.show_image()

    def show_image(self):
        self.update_image()

    def update_image(self):
        width = self.top.winfo_width()
        height = self.top.winfo_height()
        
        if width <= 1 or height <= 1:
            self.top.after(100, self.update_image)
            return
        
        # Calculate new size while maintaining aspect ratio
        img_ratio = self.original_image.width / self.original_image.height
        win_ratio = width / height
        
        if win_ratio > img_ratio:
            new_height = height
            new_width = int(height * img_ratio)
        else:
            new_width = width
            new_height = int(width / img_ratio)
        
        # Apply zoom scale
        new_width = int(new_width * self.scale)
        new_height = int(new_height * self.scale)
        
        resized_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_image)
        
        self.canvas.delete("all")
        self.canvas.create_image(width//2, height//2, image=self.photo, anchor=tk.CENTER)

    def resize_image(self, event):
        self.update_image()

    def zoom(self, event):
        if event.num == 5 or event.delta == -120:  # Scroll down
            self.scale *= 0.9
        if event.num == 4 or event.delta == 120:   # Scroll up
            self.scale *= 1.1
        self.update_image()

    def close(self, event=None):
        self.top.destroy()
class ImageProcessorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Field Museum Herbarium Parser")
        master.geometry("800x800")
        master.configure(bg="green")
        
        self.current_image_index = 0
        self.processed_images = []
        self.processed_outputs = []
        self.output_file = ""

        #BUTTONS
        input_frame = ttk.LabelFrame(master, text="Input Settings")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="URL's of Images").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.url_file_entry = ttk.Entry(input_frame, width=50)
        self.url_file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_url_file).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(input_frame, text="API Key File:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.api_key_entry = ttk.Entry(input_frame, width=50)
        self.api_key_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_api_key_file).grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(input_frame, text="Prompt Folder:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.prompt_folder_entry = ttk.Entry(input_frame, width=50)
        self.prompt_folder_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_prompt_folder).grid(row=2, column=2, padx=5, pady=5)

        ttk.Label(input_frame, text="Prompt:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.prompt_var = tk.StringVar()
        self.prompt_dropdown = ttk.Combobox(input_frame, textvariable=self.prompt_var, width=47)
        self.prompt_dropdown.grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Refresh", command=self.refresh_prompts).grid(row=3, column=2, padx=5, pady=5)

        ttk.Label(input_frame, text="Output File:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.output_file_entry = ttk.Entry(input_frame, width=50)
        self.output_file_entry.grid(row=4, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Save As", command=self.save_as).grid(row=4, column=2, padx=5, pady=5)

        #GO GO GO
        ttk.Button(master, text="Process Images", command=self.process_images).pack(pady=10)

        output_frame = ttk.LabelFrame(master, text="Output")
        output_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Image 
        self.image_label = ttk.Label(output_frame)
        self.image_label.pack(side="left", padx=10, pady=10)

        #save edits after parsing
        text_frame = ttk.Frame(output_frame)
        text_frame.pack(side="right", fill="both", expand=True)

        self.output_text = tk.Text(text_frame, wrap="word", width=40, height=10)
        self.output_text.pack(padx=10, pady=10, fill="both", expand=True)

        self.save_button = ttk.Button(text_frame, text="Save Edits", command=self.save_edits)
        self.save_button.pack(pady=10)

        nav_frame = ttk.Frame(master)
        nav_frame.pack(pady=10)

        self.prev_button = ttk.Button(nav_frame, text="Previous", command=self.show_previous_image, state=tk.DISABLED)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.next_button = ttk.Button(nav_frame, text="Next", command=self.show_next_image, state=tk.DISABLED)
        self.next_button.grid(row=0, column=1, padx=5)

        # Final 
        self.final_output = tk.Text(master, wrap="word", width=80, height=10)
        self.final_output.pack(padx=10, pady=10, fill="both", expand=True)

    def browse_url_file(self):
        file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        self.url_file_entry.delete(0, tk.END)
        self.url_file_entry.insert(0, file)

    def browse_api_key_file(self):
        file = filedialog.askopenfilename()
        self.api_key_entry.delete(0, tk.END)
        self.api_key_entry.insert(0, file)

    def browse_prompt_folder(self):
        folder = filedialog.askdirectory()
        self.prompt_folder_entry.delete(0, tk.END)
        self.prompt_folder_entry.insert(0, folder)
        self.refresh_prompts()

    def refresh_prompts(self):
        prompt_folder = self.prompt_folder_entry.get()
        if not prompt_folder:
            messagebox.showwarning("Warning", "Please select a prompt folder first.")
            return
        prompt_files = [f for f in os.listdir(prompt_folder) if f.endswith('.txt')]
        self.prompt_dropdown['values'] = prompt_files
        if prompt_files:
            self.prompt_dropdown.set(prompt_files[0])

    def save_as(self):
        file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file:
            self.output_file_entry.delete(0, tk.END)
            self.output_file_entry.insert(0, file)
            self.output_file = file

    def process_images(self):
        url_file = self.url_file_entry.get()
        output_file = self.output_file_entry.get()
        api_key_file = self.api_key_entry.get()
        prompt_folder = self.prompt_folder_entry.get()
        selected_prompt = self.prompt_var.get()

        if not all([url_file, output_file, api_key_file, prompt_folder, selected_prompt]):
            messagebox.showerror("Error", "All fields must be filled.")
            return

        self.output_file = output_file  # Save the output file path

        #API key
        try:
            with open(api_key_file, "r", encoding="utf-8") as api_file:
                api_key = api_file.read().strip()
        except UnicodeDecodeError:
            with open(api_key_file, "r") as api_file:
                api_key = api_file.read().strip()

        #prompt
        prompt_path = os.path.join(prompt_folder, selected_prompt)
        try:
            with open(prompt_path, "r", encoding="utf-8") as prompt_file:
                prompt_text = prompt_file.read().strip()
        except UnicodeDecodeError:
            messagebox.showerror("AHHHHH ERROR", f"Unable to read the prompt file: {prompt_path}. Please make sure no special characters are in prompt and keep it NEAT!!")
            return

        client = anthropic.Anthropic(api_key=api_key)

        #URL
        try:
            with open(url_file, "r", encoding="utf-8") as url_file:
                urls = url_file.readlines()
        except UnicodeDecodeError:
            # If UTF-8 fails, try with system default encoding
            with open(url_file, "r") as url_file:
                urls = url_file.readlines()

        # Process each URL
        self.processed_images.clear()
        self.processed_outputs.clear()
        self.current_image_index = 0

        for index, url in enumerate(urls):
            url = url.strip()
            try:
                response = requests.get(url)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
                
                self.processed_images.append(image)

                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

                # Process image
                message = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=2500,
                    temperature=0,
                    system="You are an assistant that has a job to extract text from an image and parse it out.",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_image}}
                            ]
                        }
                    ]
                )

                # Store output
                output = self.format_response(f"Image {index + 1}", message.content, url)
                self.processed_outputs.append(output)

                # Append to final output
                self.final_output.insert(tk.END, output + "\n" + "="*50 + "\n")

            except requests.exceptions.RequestException as e:
                error_message = f"Error processing image {index + 1}: {str(e)}"
                self.processed_outputs.append(error_message)
                self.final_output.insert(tk.END, error_message + "\n" + "="*50 + "\n")

            self.master.update_idletasks()  # Update GUI

        # Enable navigation buttons
        if self.processed_images:
            self.show_image(0)
            self.prev_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.NORMAL)

        # Show completion message with option to open output directory
        self.show_completion_message(output_file)

        #output to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(self.final_output.get("1.0", tk.END))

    def format_response(self, image_name, response_data, url):
        # Extract the text from the response data
        text_block = response_data[0].text

        # Split the text into lines
        lines = text_block.split('\n')

        formatted_result = f"{image_name}\n"
        formatted_result += f"URL: {url}\n\n"
        formatted_result += "\n".join(lines)

        return formatted_result

    def display_image(self, image):
        image.thumbnail((300, 300))  # Resize image to fit in the GUI
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo  # Keep a reference

        # Open the image in full screen when clicked
        self.image_label.bind("<Button-1>", lambda event: self.open_full_screen(image))

    def open_full_screen(self, image):
        FullScreenImage(self.master, image)

    def show_image(self, index):
        self.current_image_index = index
        self.display_image(self.processed_images[index])
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, self.processed_outputs[index])

    def show_previous_image(self):
        if self.current_image_index > 0:
            self.save_current_output()
            self.show_image(self.current_image_index - 1)

    def show_next_image(self):
        if self.current_image_index < len(self.processed_images) - 1:
            self.save_current_output()
            self.show_image(self.current_image_index + 1)

    def save_current_output(self):
        # Save the current text output to the processed_outputs list
        self.processed_outputs[self.current_image_index] = self.output_text.get(1.0, tk.END)

    def show_completion_message(self, output_file):
        msg_box = tk.messagebox.askyesno("Processing Complete",
                                         f"All images processed. Results saved to {output_file}.\n\n"
                                         "Would you like to open the directory containing the output file?")
        if msg_box:
            self.open_output_directory(output_file)

    def open_output_directory(self, output_file):
        output_dir = os.path.dirname(os.path.abspath(output_file))
        if sys.platform == "win32":
            os.startfile(output_dir)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", output_dir])
        else:  # Assume Linux or other Unix
            subprocess.Popen(["xdg-open", output_dir])
            
    def save_edits(self):
        if not self.output_file:
            messagebox.showerror("Error", "No output file specified.")
            return

        self.save_current_output()  # Save the current output before writing to file

        # Save all outputs to the final output text widget
        self.final_output.delete(1.0, tk.END)
        for output in self.processed_outputs:
            self.final_output.insert(tk.END, output + "\n" + "="*50 + "\n")

        # Write the final output to the file
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(self.final_output.get("1.0", tk.END))
            messagebox.showinfo("Success", f"Edits saved to {self.output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save edits: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorGUI(root)
    root.mainloop()