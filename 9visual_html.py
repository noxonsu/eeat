import markdown
import os
from utils import *
def generate_html_from_markdown(mark,title,keys,desc):
    #markdown to html with tables
    #mark = mark.replace("- ","<Br>- ")
    html = markdown.markdown(mark,extensions=['markdown.extensions.tables'])
    html = html.replace("- ","<Br>- ")
    return """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="keywords" content="{meta_keywords}">
        <meta name="description" content="{meta_description}">
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{title}</title>
        <style>
        body {{
            font-family: Arial, Helvetica, sans-serif;
            font-size: 16px;
            line-height: 1.6;
            padding: 0;
            margin: 0;
        }}
        </style>
    </head>
    <body>
        <article>
        {text}
        </article>
        
    </body>
    </html>""".format(text=html,title=title,meta_keywords=keys,meta_description=desc)

def save_html_to_file(html):
        with open("data/"+INDUSTRY_KEYWORD+"/article.html", "w") as f:
            f.write(html)
            
# Environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
INDUSTRY_KEYWORD = os.environ.get('INDUSTRY_KEYWORD')
TITLE_ARTICLE = os.environ.get('TITLE_ARTICLE', INDUSTRY_KEYWORD)

file = "data/"+INDUSTRY_KEYWORD+"/article.md"


mark=read_markdown_file(file)

html=generate_html_from_markdown(mark,TITLE_ARTICLE,INDUSTRY_KEYWORD,INDUSTRY_KEYWORD)

#sae html to file

    

save_html_to_file(html)
