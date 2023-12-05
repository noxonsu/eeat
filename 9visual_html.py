import markdown
import os
import datetime

def generate_html_from_markdown(mark, title, MEDIUM_TAGS, date_iso, author_name, author_link, about_author):
    # markdown to html with tables
    html = markdown.markdown(mark, extensions=['markdown.extensions.tables'])
    html = html.replace("- ", "<br>- ")

    template = f"""<!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>{title}</title>
        <meta name="description" content="">
        <meta name="keywords" content="{MEDIUM_TAGS}">
        <!-- Include Tachyons CSS for styling -->
        <link rel="stylesheet" href="https://unpkg.com/tachyons/css/tachyons.min.css"/>
        <!-- Include tocbot CSS for styling the table of contents -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tocbot/dist/tocbot.css">
        <style>
            /* Custom styles for layout */
            .layout {{
                display: flex;
                justify-content: center;
                padding: 1rem;
            }}
            .toc-content {{
                width: 250px; /* Width of the TOC sidebar */
                position: sticky;
                top: 1rem;
                height: 100vh;
                overflow: auto;
            }}
            .content {{
                max-width: 800px; /* Adjust based on your content's optimal reading width */
                margin-left: 2rem; /* Space between TOC and content */
            }}
            @media screen and (max-width: 30em) {{
                .toc-content {{
                    display: none; /* Hide TOC on smaller screens */
                }}
                .content {{
                    margin-left: 1rem;
                    width: calc(100% - 2rem); /* Full width minus padding on small screens */
                }}
            }}
            a, button {{
                /* Minimum recommended size for tap targets is 48x48 pixels */
                min-width: 48px;
                min-height: 48px;
                /* Additional padding can help enlarge smaller text links */
                padding: 8px;
            }}
        </style>
    </head>
    <body class="sans-serif pa3">
        <!-- Rest of your HTML content here -->
    </body>
    </html>"""

    return template.format(
        text=html,
        title=title,
        date_iso=date_iso,
        author_name=author_name,
        author_link=author_link,
        about_author=about_author
    )

def save_html_to_file(html, file_path):
    with open(file_path, "w") as f:
        f.write(html)

# Inputs from GitHub Actions
html_title = os.environ.get('MEDIUM_TITLE')
MEDIUM_TAGS = os.environ.get('MEDIUM_TAGS')
author_link = os.environ.get('AUTHOR_LINK')
author_name = os.environ.get('AUTHOR_NAME')
about_author = os.environ.get('ABOUT_AUTHOR')
markdown_content = os.environ.get('MEDIUM_TEXT')
INDUSTRY_KEYWORD = os.environ.get('INDUSTRY_KEYWORD')



date_iso = datetime.datetime.now().isoformat()
date = datetime.datetime.now().strftime("%Y-%m-%d")

html = generate_html_from_markdown(
    markdown_content,
    html_title,
    MEDIUM_TAGS,
    date_iso,
    author_name,
    author_link,
    about_author
)


save_html_to_file(html, "data/"+INDUSTRY_KEYWORD+"/article.html")

