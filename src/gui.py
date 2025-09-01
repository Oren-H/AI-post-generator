import gradio as gr
from .main import main as run_main


def run_generation(article_path: str) -> str:
    article_path = (article_path or "").strip()
    if not article_path:
        return "Please provide a PDF path."
    try:
        run_main(article_path=article_path)
        return "Done. Check console logs and generated images."
    except Exception as exc:  # noqa: BLE001 - surface error to user
        return f"Error: {exc}"


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
        status = gr.Textbox(label="Status", interactive=False)

        generate_btn.click(fn=run_generation, inputs=article_input, outputs=status)

    demo.launch()


if __name__ == "__main__":
    launch_app()


