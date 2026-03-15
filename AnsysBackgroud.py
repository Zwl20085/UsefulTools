import time
import hashlib
from PIL import Image, ImageGrab
import numpy as np
import os

def remove_ansys_gradient_background(img, tolerance=15):
    """
    Removes a gradient background by sampling the top and bottom corners 
    to establish a color range.
    """
    img = img.convert("RGBA")
    data = np.array(img)

    # 1. Sample the top-left and bottom-left corners to get the gradient extremes
    top_color = data[0, 0, :3].astype(int)
    bottom_color = data[-1, 0, :3].astype(int)

    # 2. Define the minimum and maximum RGB values of the gradient
    # We subtract/add tolerance to catch slight variations or noise
    min_color = np.minimum(top_color, bottom_color) - tolerance
    max_color = np.maximum(top_color, bottom_color) + tolerance

    # 3. Extract just the RGB channels for comparison
    rgb_data = data[:, :, :3].astype(int)

    # 4. Create a mask: Keep pixels where Red, Green, AND Blue all fall 
    # within our gradient range.
    bg_mask = np.all((rgb_data >= min_color) & (rgb_data <= max_color), axis=-1)

    # 5. Make the matched background pixels fully transparent
    data[bg_mask, 3] = 0

    return Image.fromarray(data)

def get_image_hash(img):
    return hashlib.md5(img.tobytes()).hexdigest()

def watch_clipboard_for_screenshots(output_folder="processed_ansys", tolerance=15):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print(f"Monitoring clipboard for GRADIENT backgrounds...")
    print(f"Images will be saved to '{output_folder}'. Press Ctrl+C to stop.")

    last_image_hash = None
    image_counter = 1

    try:
        while True:
            clipboard_content = ImageGrab.grabclipboard()

            if isinstance(clipboard_content, Image.Image):
                current_hash = get_image_hash(clipboard_content)

                if current_hash != last_image_hash:
                    print(f"\nNew screenshot detected! Processing gradient...")
                    
                    try:
                        # Use the new gradient-aware function
                        processed_img = remove_ansys_gradient_background(clipboard_content, tolerance)
                        
                        filename = os.path.join(output_folder, f"ansys_cleared_{image_counter}.png")
                        processed_img.save(filename)
                        print(f"Success! Saved as {filename}")
                        
                        last_image_hash = current_hash
                        image_counter += 1
                    except Exception as e:
                        print(f"Error processing image: {e}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopped monitoring.")

if __name__ == "__main__":
    # If it still leaves a bit of the gradient, try increasing tolerance to 20 or 25
    watch_clipboard_for_screenshots(tolerance=15)