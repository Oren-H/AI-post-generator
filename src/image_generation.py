from PIL import Image, ImageDraw, ImageFont

def _wrap_text(draw, text, font, max_width):
    """
    Wraps text to fit within a specified maximum width.
    This version requires the ImageDraw object to be passed as an argument.
    Returns a list of strings, where each string is a line.
    """
    lines = []
    if not text:
        return lines
    words = text.split()
    current_line = []
    for word in words:
        # Check if adding the next word exceeds max_width
        test_line = " ".join(current_line + [word])
        if draw.textbbox((0, 0), test_line, font=font)[2] <= max_width:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def generate_image(quote, byline, title):

    # 1. Define image dimensions and background color
    img_width = 1080  # Standard Instagram post aspect ratio (square)
    img_height = 1080
    bg_color = (30, 30, 30)  # A dark gray color (R, G, B)

    # 2. Create a new image with the specified dimensions and color
    image = Image.new('RGB', (img_width, img_height), color=bg_color)

    # 3. Get a drawing context
    draw = ImageDraw.Draw(image)

    # 4. Define the text to display. This is a long paragraph to match the image.
    long_text = quote
    byline_text = "-Oren Hartstein"
    logo_text = "Columbia Sundial"

    # 5. Load a font (You'll need a font file, e.g., .ttf or .otf)
    try:
        font_main = ImageFont.truetype("Times New Roman.ttf", size=50)
        font_byline = ImageFont.truetype("Times New Roman.ttf", size=30)
    except IOError:
        print("Font file not found. Using default font.")
        font_main = ImageFont.load_default()
        font_byline = ImageFont.load_default()

    # 6. Wrap the main text based on the image width with some padding
    padding = 100
    wrapped_text = _wrap_text(draw, quote, font_main, img_width - padding * 2)

    # 7. Calculate text position to center the entire block
    # Sum the height of each line using textbbox()
    quote_lines_height = sum(draw.textbbox((0, 0), line, font=font_main)[3] for line in wrapped_text)
    total_text_height = quote_lines_height # We'll add the byline and logo separately

    start_y = (img_height - total_text_height) / 2

    # 8. Draw each line of the wrapped text
    text_color = (255, 255, 255)  # A white color for visibility
    current_y = start_y

    for line in wrapped_text:
        # Use textbbox to get the width of each line for centering
        text_width = draw.textbbox((0, 0), line, font=font_main)[2]
        text_height = draw.textbbox((0, 0), line, font=font_main)[3]
        x = (img_width - text_width) / 2
        draw.text((x, current_y), line, fill=text_color, font=font_main)
        current_y += text_height

    # 9. Draw the byline text at the bottom
    byline_x = padding
    byline_y = img_height - padding - draw.textbbox((0, 0), byline, font=font_byline)[3]
    byline_color = (255, 100, 100) # Lighter red for contrast
    draw.text((byline_x, byline_y), byline, fill=byline_color, font=font_byline)

    # 10. Load and place the logo image at the bottom-right
    # The logo file must be in the same directory as this script
    try:
        logo = Image.open("sundial_logo_white.png")
        logo_width = 200 # Set a desired width for the logo
        aspect_ratio = logo.width / logo.height
        logo_height = int(logo_width / aspect_ratio)

        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

        # Position the logo in the bottom right corner with padding
        logo_x = img_width - padding - logo.width + 80
        logo_y = img_height - padding - logo.height + 130

        # Paste the logo onto the main image using its alpha channel for transparency
        image.paste(logo, (logo_x, logo_y), logo)

    except FileNotFoundError:
        print("Logo file 'logo.png' not found. Skipping logo placement.")
    except Exception as e:
        print(f"An error occurred while processing the logo: {e}")

    # 11. Save the image
    image.save(title + ".png")
    print(f"Image {title} generated successfully!")
