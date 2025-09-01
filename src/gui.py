import os
import uuid
import zipfile
import pdfplumber
import gradio as gr
from dotenv import load_dotenv
from .graph import Graph
from .image_generation import generate_image


def run_generation(article_path: str):
    article_path = (article_path or "").strip()
    if not article_path:
        return [], [], "Please provide a PDF path."
    try:
        load_dotenv()
        text = ""
        with pdfplumber.open(article_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text() or ""
                text += extracted

        graph = Graph().graph
        config = {"configurable": {"thread_id": "gradio"}}
        result = graph.invoke({"article": text}, config=config)

        quotes_obj = result.get("quotes")
        quotes = quotes_obj.quotes if hasattr(quotes_obj, "quotes") else quotes_obj

        image_paths = []
        for idx, quote in enumerate(quotes):
            title = f"gradio_{uuid.uuid4().hex[:8]}_{idx}"
            generate_image(quote, "-Oren Hartstein", title)
            image_paths.append(os.path.abspath(f"{title}.png"))

        return image_paths, image_paths, "Done.", image_paths
    except Exception as exc:  # noqa: BLE001 - surface error to user
        return [], [], f"Error: {exc}", []


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
    with gr.Blocks(title="AI Post Generator") as demo:
        gr.Markdown("## AI Post Generator\nEnter the path to a PDF article and click Generate.")
        with gr.Row():
            article_input = gr.Textbox(
                label="Article PDF Path",
                value="Conservatives in Academia.pdf",
                placeholder="/absolute/or/relative/path/to/article.pdf",
            )
        generate_btn = gr.Button("Generate")
        with gr.Row():
            gallery = gr.Gallery(label="Generated Images", columns=3, height=600)
        files = gr.Files(label="Download Images")
        with gr.Row():
            download_all_btn = gr.DownloadButton("Download All")
        status = gr.Textbox(label="Status", interactive=False)
        paths_state = gr.State([])

        generate_btn.click(fn=run_generation, inputs=article_input, outputs=[gallery, files, status, paths_state])
        download_all_btn.click(fn=create_zip, inputs=paths_state, outputs=download_all_btn)

    demo.launch()


if __name__ == "__main__":
    launch_app()


