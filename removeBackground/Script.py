from PIL import Image
import os
import numpy as np

def remove_background(input_path, output_path, color_threshold=40):
    """
    Removes white background from an image while preserving content.

    Args:
        input_path (str): The path to the input image file.
        output_path (str): The path where the output image with 
                           transparent background will be saved.
        color_threshold (int): Threshold for white detection (0-255).
    """
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Resolve paths relative to the script directory if they are relative
    if not os.path.isabs(input_path):
        input_path = os.path.join(script_dir, input_path)
    if not os.path.isabs(output_path):
        output_path = os.path.join(script_dir, output_path)

    # Open the input image
    input_image = Image.open(input_path).convert('RGBA')
    
    # Convert to numpy array for processing
    img_array = np.array(input_image)
    
    # Define white color (255, 255, 255)
    white = np.array([255, 255, 255])
    
    # Calculate distance to white for each pixel
    diff = np.sum((img_array[:, :, :3].astype(np.float32) - white) ** 2, axis=2) ** 0.5
    
    # Create mask: pixels close to white become transparent
    mask = (diff < color_threshold).astype(np.uint8) * 255
    
    # Apply mask to alpha channel (inverted: white = transparent, rest = opaque)
    img_array[:, :, 3] = 255 - mask
    
    # Convert back to PIL Image and save
    output_image = Image.fromarray(img_array, 'RGBA')
    output_image.save(output_path)
    print(f"Background removed and saved to {output_path}")

# Example usage:
# Make sure you have an image named 'Logo.png' in the same directory
remove_background('Logo.png', 'output.png')
