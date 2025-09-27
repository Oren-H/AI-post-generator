import os
import zipfile
import sys
import subprocess
import pdfplumber
import shutil
import tempfile
import gradio as gr
from dotenv import load_dotenv
from .graph import Graph
from .image_generation import generate_image
from .fp_post_generation import generate_image as fp_generate_image


def run_generation(article_path: str, author: str, style: str = "Original"):
    article_path = (article_path or "").strip()
    author = (author or "").strip()
    if not article_path:
        yield (
            gr.update(value=[], visible=False),
            gr.update(value="", visible=False),
            gr.update(value=[], visible=False),
            gr.update(value="Please upload a PDF.", visible=True),
            [],
            gr.update(visible=False),
        )
        return
    try:
        load_dotenv()
        # Make a safe copy of the uploaded file so streaming (yields) doesn't race with temp cleanup
        safe_article_path = None
        try:
            temp_dir = tempfile.mkdtemp(prefix="ai_post_")
            safe_article_path = os.path.join(temp_dir, os.path.basename(article_path))
            shutil.copy2(article_path, safe_article_path)
            # Inform the user immediately that generation has started
            yield (
                gr.update(value=[], visible=False),
                gr.update(value="", visible=False),
                gr.update(value=[], visible=False),
                gr.update(value="Generating images... this may take a minute.", visible=True),
                [],
                gr.update(visible=False),
            )
        except Exception:
            safe_article_path = None

        open_path = safe_article_path or article_path
        text = ""
        with pdfplumber.open(open_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text() or ""
                text += extracted

        graph = Graph().graph
        config = {"configurable": {"thread_id": "gradio"}}
        result = graph.invoke({"article": text}, config=config)

        caption = result.get("insta_caption") or ""

        quotes_obj = result.get("quotes")
        quotes = quotes_obj.quotes if hasattr(quotes_obj, "quotes") else quotes_obj

        image_paths = []
        article_title = os.path.splitext(os.path.basename(article_path))[0]
        byline = f"-{author}" if author and not author.startswith("-") else (author or "-Oren Hartstein")
        save_dir = os.path.dirname(os.path.abspath(open_path))
        for idx, quote in enumerate(quotes, start=1):
            title = f"{article_title}_{idx}"
            # Choose the appropriate generation function based on style
            if style == "The Free Press":
                fp_generate_image(quote, byline, title, save_dir=save_dir)
            else:  # Default to original style
                generate_image(quote, byline, title, save_dir=save_dir)
            image_paths.append(os.path.abspath(os.path.join(save_dir, f"{title}.png")))

        # Save caption to a .txt file and include in downloadable files/state (not gallery)
        caption_path = os.path.abspath(os.path.join(save_dir, f"{article_title}_caption.txt"))
        try:
            with open(caption_path, "w", encoding="utf-8") as f:
                f.write(caption)
        except Exception:
            caption_path = None

        download_paths = image_paths.copy()
        if caption_path and os.path.isfile(caption_path):
            download_paths.append(caption_path)

        yield (
            gr.update(value=image_paths, visible=True),
            gr.update(value=caption, visible=True),
            gr.update(value=download_paths, visible=True),
            gr.update(value="Done.", visible=True),
            download_paths,
            gr.update(visible=True),
        )
    except Exception as exc:  # noqa: BLE001 - surface error to user
        yield (
            gr.update(value=[], visible=False),
            gr.update(value="", visible=False),
            gr.update(value=[], visible=False),
            gr.update(value=f"Error: {exc}", visible=True),
            [],
            gr.update(visible=False),
        )


def create_zip(image_paths: list):
    if not image_paths:
        return None
    safe_paths = [p for p in image_paths if p and os.path.isfile(p)]
    if not safe_paths:
        return None
    # On macOS, prompt for a destination folder using a native chooser
    selected_dir = None
    if sys.platform == "darwin":
        try:
            script = 'POSIX path of (choose folder with prompt "Choose a folder to save images")'
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            path = (result.stdout or "").strip()
            if path and os.path.isdir(path):
                selected_dir = path
        except Exception:
            selected_dir = None

    # If a folder was chosen, copy images directly into it; otherwise, no-op
    if selected_dir:
        for p in safe_paths:
            try:
                shutil.copy2(p, os.path.join(selected_dir, os.path.basename(p)))
            except Exception:
                # Skip files that cannot be copied
                continue
        # No file to download; returning None keeps the button without triggering a download
        return None
    
    # If no folder selected (e.g., non-macOS), fall back to creating a zip in CWD
    zip_name = "images.zip"
    with zipfile.ZipFile(zip_name, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in safe_paths:
            zf.write(p, arcname=os.path.basename(p))
    return os.path.abspath(zip_name)


def launch_app():
    with gr.Blocks(title="AI Post Generator", analytics_enabled=False) as demo:
        gr.Markdown("## AI Post Generator\nUpload a PDF article and click Generate.")
        with gr.Row():
            article_input = gr.File(label="Article PDF", file_types=[".pdf"], file_count="single", type="filepath")
            author_input = gr.Textbox(
                label="Author",
                value="",
                placeholder="e.g., Oren Hartstein",
            )
            style_input = gr.Dropdown(
                label="Post Style",
                choices=["Original", "The Free Press"],
                value="Original",
                info="Choose the visual style for your posts"
            )
        generate_btn = gr.Button("Generate")
        with gr.Row():
            gallery = gr.Gallery(label="Generated Images", columns=3, visible=False)
        caption_box = gr.Textbox(label="Instagram Caption", lines=4, visible=False)
        files = gr.Files(label="Download Images", visible=False)
        with gr.Row():
            download_all_btn = gr.DownloadButton("Download All", visible=False)
        status = gr.Textbox(label="Status", interactive=False, visible=False)
        paths_state = gr.State([])

        generate_btn.click(
            fn=run_generation,
            inputs=[article_input, author_input, style_input],
            outputs=[gallery, caption_box, files, status, paths_state, download_all_btn],
        )
        download_all_btn.click(fn=create_zip, inputs=paths_state, outputs=download_all_btn)

    # Use PORT environment variable for deployment platforms like Fly.io
    port = int(os.getenv("PORT", 7860))
    demo.queue().launch(server_name="0.0.0.0", server_port=port)


if __name__ == "__main__":
    launch_app()


