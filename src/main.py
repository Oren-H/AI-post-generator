import pdfplumber
import logging
from graph import Graph
from dotenv import load_dotenv

def main():
    logging.getLogger("pdfminer").setLevel(logging.ERROR)
    load_dotenv()
    text = ""
    with pdfplumber.open("Conservatives in Academia.pdf") as pdf:
        for page in pdf.pages:
            text += page.extract_text()

    graph = Graph().graph
    config = {"configurable": {"thread_id": "3"}}
    result = graph.invoke({"article": text}, config=config)
    
    print("SUMMARY")
    print('='*150)
    print(result["summary"])
    print('='*150)
    print("QUOTES")
    for quote in result["quotes"].quotes:
        print(quote)
        print('-'*100)
    print('='*150)
    print("INSTA CAPTION")
    print(result["insta_caption"])

if __name__ == "__main__":
    main()