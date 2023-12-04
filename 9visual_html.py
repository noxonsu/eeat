import markdown
import os
from utils import *
def generate_html_from_markdown(mark,title,keys,desc):
    #markdown to html with tables
    #mark = mark.replace("- ","<Br>- ")
    html = markdown.markdown(mark,extensions=['markdown.extensions.tables'])
    html = html.replace("- ","<Br>- ")
    return """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
   
    <title>{title}</title>
    <!-- Include Tachyons CSS for styling -->
    <link rel="stylesheet" href="https://unpkg.com/tachyons/css/tachyons.min.css"/>
    <!-- Include tocbot CSS for styling the table of contents -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tocbot/dist/tocbot.css">
    <style>
        /* Custom styles for layout */
        .layout { 
            display: flex;
            justify-content: center;
            padding: 1rem;
        }
        .toc-content {
            width: 250px; /* Width of the TOC sidebar */
            position: sticky;
            top: 1rem;
            height: 100vh;
            overflow: auto;
        }
        .content {
            max-width: 800px; /* Adjust based on your content's optimal reading width */
            margin-left: 2rem; /* Space between TOC and content */
        }
        @media screen and (max-width: 30em) {
            .toc-content {
                display: none; /* Hide TOC on smaller screens */
            }
            .content {
                margin-left: 1rem;
                width: calc(100% - 2rem); /* Full width minus padding on small screens */
            }
        }
        a, button {
            /* Minimum recommended size for tap targets is 48x48 pixels */
            min-width: 48px;
            min-height: 48px;
            /* Additional padding can help enlarge smaller text links */
            padding: 8px;
        }
    </style>
</head>
<body class="sans-serif pa3">
    <header class="tc pv4">
        <h1 class="f2 lh-title">{title}</h1>
        <time class="f6 ttu tracked" datetime="{date_iso}">{date}</time>
        <address class="f6">
            От <a href="{author_link}" class="link dim black b">{author_name}</a>,<br>
            {about_author}
        </address>
    </header>

    <div class="layout">
        <!-- Table of Contents -->
        <nav class="toc-content">
            <!-- tocbot will inject TOC here -->
        </nav>

        <!-- Main Content -->
        <div class="content">
            <article class="mb4">
              {text}
            </article>
            <!-- Additional articles or content here -->
        </div>
    </div>

    <!-- Include tocbot script -->
    <script src="https://cdn.jsdelivr.net/npm/tocbot/dist/tocbot.min.js"></script>
    <script>
      // Initialize tocbot
      tocbot.init({
        tocSelector: '.toc-content',
        contentSelector: '.content',
        headingSelector: 'h1, h2, h3, h4, h5, h6',
      });
    </script>
</body>
</html>
""".format(text=html,title=title,meta_keywords=keys,meta_description=desc)

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
