from rembg import remove
from PIL import Image
import io


def remove_background(input_path, output_path):
    # Open the input image
    original_image = Image.open(input_path)

    # Remove the background
    # The 'remove()' function handles the processing using an AI model
    no_bg_image = remove(
        original_image,
        alpha_matting=True,
        alpha_matting_foreground_threshold=400,
        alpha_matting_background_threshold=5,
        alpha_matting_erode_size=30
    )

    # Save the result as a PNG file
    # It is crucial to save as PNG to support transparency (alpha channel)
    no_bg_image.save(output_path)

    print(f"Background removed and saved to {output_path}")


if __name__ == "__main__":
    # Define your input and output file paths
    input_file = "logo_ornamental.png"  # Can be .jpg, .png, etc.
    output_file = "logo_ornamental_transparent.png"

    remove_background(input_file, output_file)
