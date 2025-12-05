# AI Post Generator

An AI-powered tool that summarizes a PDF article, pulls direct quotes, generates an Instagram caption, and creates shareable quote images.

Here is an example image the tool is capable of producing:
<img width="600" height="600" alt="image" src="https://github.com/user-attachments/assets/da227065-91c6-45c9-b219-e952eb8a69e2" />


## Features
- Summarizes articles (2–3 paragraphs)
- Extracts multiple pull-out quotes (direct quotations)
- Generates an Instagram-ready caption
- Creates 1080x1080 quote images with byline and logo
- CLI and Gradio UI

## Requirements
- Python 3.10+
- OpenAI API key

## Installation
```bash
# Clone and enter the project
git clone https://github.com/<your-username>/AI-post-generator.git
cd AI-post-generator

# (Optional) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration
Set your OpenAI API key in the environment or a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key
```
Models used (via LangChain/ChatOpenAI): `gpt-4o` and `gpt-4o-mini`.

## Usage

### CLI
Runs end-to-end generation and saves images next to your working directory.
```bash
python -m src.main --article "/absolute/or/relative/path/to/article.pdf"
```
- If `--article` is omitted, you’ll be prompted (default: `Conservatives in Academia.pdf`).
- Outputs:
  - Console: summary, quotes, and Instagram caption
  - Files: `"<article_basename>_1.png"`, `"<article_basename>_2.png"`, ...

### Gradio UI
Launch a simple UI to select a PDF and author/byline.
```bash
python -m src.gui
```
- Enter the article PDF path and optional author (e.g., `Oren Hartstein`)
- Click Generate to create images and caption
- Download individual images or a zipped bundle

## Image Generation
- Output size: 1080x1080 PNG
- Font: Attempts `Times New Roman.ttf`, falls back to default if not found
- Logo: Looks for `sundial_logo_white.png` in project root (skips if missing)
- Byline: Taken from UI input; CLI defaults to `-Oren Hartstein`

## Project Structure
- `src/main.py`: CLI entrypoint
- `src/gui.py`: Gradio UI
- `src/graph.py`: Orchestrates summarization, quotes, caption
- `src/nodes.py`: LLM calls and data flow
- `src/prompts.py`: System prompts
- `src/image_generation.py`: Quote image rendering
- `src/schemas.py`: Data models

## Troubleshooting
- "Please provide a PDF path": Specify a valid file path in CLI/UI
- Font file not found: Place `Times New Roman.ttf` in project root or ignore
- Logo not found: Ensure `sundial_logo_white.png` exists or ignore
- OpenAI errors: Confirm `OPENAI_API_KEY` is set and you have model access

## License
MIT (or your preferred license).
