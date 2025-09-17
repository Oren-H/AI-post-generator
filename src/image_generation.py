from PIL import Image, ImageDraw, ImageFont
import os
import re


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

def _normalize_quotes(text: str) -> str:
    """
    Ensure nested quotes inside the pullout use single quotes, not double quotes,
    while preserving apostrophes inside words. Converts paired double quotes
    (straight or curly) used as quoting delimiters into single quotes.
    """
    if not text:
        return text

    normalized = text

    # Boundaries: avoid converting apostrophes inside words
    boundary_before = r'(^|[\s\(\[\{])'
    boundary_after = r'(?=[\s\)\]\}\.,;:!?]|$)'

    # Curly double quotes → single quotes when used as quoting delimiters
    def repl_curly_doubles(m):
        before, inner = m.group(1), m.group(2)
        return f"{before}'{inner}'"

    normalized = re.sub(boundary_before + r'“([^”]+)”' + boundary_after, repl_curly_doubles, normalized)

    # Straight double quotes → single quotes when used as quoting delimiters
    def repl_straight_doubles(m):
        before, inner = m.group(1), m.group(2)
        return f"{before}'{inner}'"

    normalized = re.sub(boundary_before + r'"([^"\n]+)"' + boundary_after, repl_straight_doubles, normalized)

    return normalized

def _ensure_wrapped_in_double(text: str) -> str:
    """Wrap entire text in straight double quotes if not already double-quoted."""
    if not text:
        return text
    stripped = text.strip()
    if (stripped.startswith('"') and stripped.endswith('"')) or (
        stripped.startswith('“') and stripped.endswith('”')
    ):
        # Normalize to straight doubles for rendering consistency
        return '"' + stripped.strip('“”').strip('"') + '"'
    return '"' + stripped + '"'

def generate_image(quote, byline, title, save_dir=None):

    # 1. Define image dimensions and background color
    img_width = 1080  # Standard Instagram post aspect ratio (square)
    img_height = 1080
    bg_color = (30, 30, 30)  # A dark gray color (R, G, B)

    # 2. Create a new image with the specified dimensions and color
    image = Image.new('RGB', (img_width, img_height), color=bg_color)

    # 3. Get a drawing context
    draw = ImageDraw.Draw(image)

    # 4. Define the text to display. This is a long paragraph to match the image.
    long_text = _ensure_wrapped_in_double(_normalize_quotes(quote))
    byline_text = "-Oren Hartstein"
    logo_text = "Columbia Sundial"

    # 5. Load a font (You'll need a font file, e.g., .ttf or .otf)
    try:
        font_path = "DejaVuSerif.ttf"
        font_main = ImageFont.truetype(font_path, size=50)
        font_byline = ImageFont.truetype(font_path, size=45)
        
    except IOError:
        print("Font file not found. Using default font.")
        font_main = ImageFont.load_default()
        font_byline = ImageFont.load_default()

    # 6. Wrap the main text based on the image width with some padding
    padding = 100
    wrapped_text = _wrap_text(draw, long_text, font_main, img_width - padding * 2)

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

    # 9. Draw the byline text at the bottom center
    formatted_byline = byline
    if byline and byline.strip():
        formatted_byline = "—" + byline.lstrip("-–— ").strip()
    byline_width = draw.textbbox((0, 0), formatted_byline, font=font_byline)[2]
    byline_height = draw.textbbox((0, 0), formatted_byline, font=font_byline)[3]
    byline_x = (img_width - byline_width) / 2
    byline_y = img_height - padding - byline_height + 20
    byline_color = (242, 210, 65)  # Warm golden yellow
    draw.text((byline_x, byline_y), formatted_byline, fill=byline_color, font=font_byline)

    # 10. Load and place the logo image at the top center
    # Resolve logo path relative to project root (parent of this file's directory)
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        logo_path = os.path.join(project_root, "sundial_logo_white.png")

        logo = Image.open(logo_path).convert("RGBA")
        logo_width = 200 # Set a desired width for the logo
        aspect_ratio = logo.width / logo.height
        logo_height = int(logo_width / aspect_ratio)

        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

        # Position the logo at the top center with padding
        logo_x = int((img_width - logo.width) / 2)
        logo_y = int(max(0, padding - 60))

        # Recolor the logo to match the byline color while preserving transparency
        alpha = logo.split()[-1]
        colored_logo = Image.new("RGBA", logo.size, byline_color + (255,))
        colored_logo.putalpha(alpha)
        image.paste(colored_logo, (logo_x, logo_y), colored_logo)

    except FileNotFoundError:
        print(f"Logo file not found at: {logo_path}. Skipping logo placement.")
    except Exception as e:
        print(f"An error occurred while processing the logo: {e}")

    # 11. Save the image
    if save_dir:
        try:
            os.makedirs(save_dir, exist_ok=True)
        except Exception:
            # If directory creation fails, fall back to current directory
            save_dir = None
    output_path = os.path.join(save_dir, title + ".png") if save_dir else (title + ".png")
    image.save(output_path)
    print(f"Image {title} generated successfully!")
