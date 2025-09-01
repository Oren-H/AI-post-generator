import os
import zipfile
import pdfplumber
import gradio as gr
from dotenv import load_dotenv
from .graph import Graph
from .image_generation import generate_image


def run_generation(article_path: str, author: str):
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
        # Immediately inform the user that generation has started
        yield (
            gr.update(value=[], visible=False),
            gr.update(value="", visible=False),
            gr.update(value=[], visible=False),
            gr.update(value="Generating images... this may take a minute.", visible=True),
            [],
            gr.update(visible=False),
        )
        load_dotenv()
        text = ""
        with pdfplumber.open(article_path) as pdf:
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
        for idx, quote in enumerate(quotes, start=1):
            title = f"{article_title}_{idx}"
            generate_image(quote, byline, title)
            image_paths.append(os.path.abspath(f"{title}.png"))

        yield (
            gr.update(value=image_paths, visible=True),
            gr.update(value=caption, visible=True),
            gr.update(value=image_paths, visible=True),
            gr.update(value="Done.", visible=True),
            image_paths,
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
        generate_btn = gr.Button("Generate")
        with gr.Row():
            gallery = gr.Gallery(label="Generated Images", columns=3, height=600, visible=False)
        caption_box = gr.Textbox(label="Instagram Caption", lines=4, visible=False)
        files = gr.Files(label="Download Images", visible=False)
        with gr.Row():
            download_all_btn = gr.DownloadButton("Download All", visible=False)
        status = gr.Textbox(label="Status", interactive=False, visible=False)
        paths_state = gr.State([])

        generate_btn.click(
            fn=run_generation,
            inputs=[article_input, author_input],
            outputs=[gallery, caption_box, files, status, paths_state, download_all_btn],
        )
        download_all_btn.click(fn=create_zip, inputs=paths_state, outputs=download_all_btn)

    demo.queue().launch()


if __name__ == "__main__":
    launch_app()


