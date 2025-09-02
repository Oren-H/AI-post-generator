import os
import pdfplumber
import logging
import argparse
from .graph import Graph
from dotenv import load_dotenv
from .image_generation import generate_image

def main(article_path=None, output_dir=None):
    logging.getLogger("pdfminer").setLevel(logging.ERROR)
    load_dotenv()
    default_article_path = "Conservatives in Academia.pdf"
    if not article_path:
        try:
            user_input = input(f"Enter article PDF path [{default_article_path}]: ").strip()
            article_path = user_input or default_article_path
        except EOFError:
            article_path = default_article_path
    text = ""
    with pdfplumber.open(article_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()

    graph = Graph().graph
    config = {"configurable": {"thread_id": "3"}}
    result = graph.invoke({"article": text}, config=config)
    caption = result["insta_caption"]
    
    print("SUMMARY")
    print('='*150)
    print(result["summary"])
    print('='*150)
    print("QUOTES")
    article_title = os.path.splitext(os.path.basename(article_path))[0]
    # Default output directory to the article's directory if not provided
    if not output_dir:
        output_dir = os.path.dirname(os.path.abspath(article_path))
    for idx, quote in enumerate(result["quotes"].quotes, start=1):
        print(quote)    
        print('-'*100)
        generate_image(quote, "-Oren Hartstein", f"{article_title}_{idx}", save_dir=output_dir)

    print('='*150)
    print("INSTA CAPTION")
    print(caption)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Instagram post images from an article PDF.")
    parser.add_argument("--article", "-a", help="Path to the article PDF", default=None)
    parser.add_argument("--output", "-o", help="Directory to save images (defaults to article's folder)", default=None)
    args = parser.parse_args()
    main(article_path=args.article, output_dir=args.output)