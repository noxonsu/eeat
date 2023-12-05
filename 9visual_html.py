import markdown
import os
import datetime

def generate_html_from_markdown(mark, title, PUBLICATION_TAGS, date_iso, author_name, author_link, about_author, CallToActionTitle, CallToActionButton, CallToActionNo):
    # markdown to html with tables
    html = markdown.markdown(mark, extensions=['markdown.extensions.tables'])
    html = html.replace("- ", "<br>- ")
    jscript = """
    // Initialize tocbot
    tocbot.init({
        tocSelector: '.toc-content',
        contentSelector: '.content',
        headingSelector: 'h1, h2, h3, h4, h5, h6, li',                    
        collapseDepth: 0,
        hasInnerContainers: true
    });
    function closePanel() {              
        var button = event.target;              
        var parent = button.closest('.sticky-panel');
        parent.style.display = 'none';
    }"""

    css = """
    /* Custom styles for layout */
    .layout {
        display: flex;
        justify-content: center;            
    }
    .toc-content {            
        position: relative;
    }
    .sticky{
        position: sticky;
        top: 1rem;
    }
    .toc-list{            
        list-style: none;
        margin: 0;                                                                        
        overflow: hidden;
        position: relative;
    }

    .toc-list .toc-list{
        position: static;
    }

    .toc>.toc-list{                    
        position: static;
    }

    .toc>.toc-list li{
        list-style: none;                    
    }

    .sticky-panel{
        position: sticky;
        bottom: 0;
        background-color: #fff;
        margin-left: -1rem;
        margin-right: -1rem;
    }

    .content {
        max-width: 800px; /* Adjust based on your content's optimal reading width */
        margin-left: 2rem; /* Space between TOC and content */
    }

    @media screen and (max-width: 50em){
        .sticky-panel .layout{
            display: block;
        }
    }

    @media screen and (max-width: 30em) {
        aside{
            display: none;
        }
        .content {                
            width: 100%;
            margin-left: 0;
        }
        .layout{
            padding-left: 0;
            padding-right: 0;
        }
    }
    """
    if (CallToActionTitle != ''):
        cta = """
        display: block;
        """
    else:
        cta = """
        display: none;
        """
    template = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta property="og:type" content="article" />
        <meta name="keywords" content="{PUBLICATION_TAGS}">
        <title>{title}</title>
        <!-- Include Tachyons CSS for styling -->
        <link rel="stylesheet" href="https://unpkg.com/tachyons/css/tachyons.min.css"/>
        <!-- Include tocbot CSS for styling the table of contents -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tocbot/dist/tocbot.css">
        <style>
           {css}
        </style>
    </head>
    <body class="w-100 sans-serif pa3 pb0">
        <header class="tc pv2 pv4-l">
            <h1 class="f2 lh-title mt0">{title}</h1>
            <time class="f6 ttu tracked" datetime="{date_iso}">{date_iso}</time>
            <address class="f6">
                <a href="{author_link}" class="link dim black b">{author_name}</a>
                {about_author}
            </address>
        </header>

        <div class="layout mw7 center pa0">
            <aside class="w-25">
                <div class="sticky">                          
                    <nav class="toc-content mb3">
                        <!-- tocbot will inject TOC here -->                
                    </nav>
                    <!-- <a href="#"><img src="https://placehold.co/200x200" alt=""></a> -->
                </div>      
            </aside>
                                    
            <!-- Main Content -->
            <div class="content w-75">
                <article class="mb4">
                    {html}
                </article>
                <!-- Additional articles or content here -->
            </div>
        
        </div>

        <div style='{cta}' class="sticky-panel shadow-2 pa2">
            <div class="layout mw8 center pa0">
                <div class="w-100 w-100-ns w-100-m flex items-center">
                    <div class="f6 f5-m f4-l lh-copy mb2 mb0-l">{CallToActionTitle}</div>
                </div>
                <div class="w-100 w-100-ns w-100-m w-25-l">
                    <a class="f6 link dim br2 ph3 pv2 dib white bg-dark-blue" href="#0">{CallToActionButton}</a>
                    <a class="f6 link dim br2 ph3 pv2 dib black" onclick="closePanel()" href="#0">{CallToActionNo}</a>
                </div>
            </div>
        </div>

        <!-- Include tocbot script -->
        <script src="https://cdn.jsdelivr.net/npm/tocbot/dist/tocbot.min.js"></script>
        <script>
          {jscript}
        </script>
    </body>
    </html>"""

    return template


def save_html_to_file(html, file_path):
    with open(file_path, "w") as f:
        f.write(html)

def main():
    # Inputs from GitHub Actions
    html_title = os.environ.get('PUBLICATION_TITLE')
    PUBLICATION_TAGS = os.environ.get('PUBLICATION_TAGS')
    markdown_content = os.environ.get('PUBLICATION_TEXT')

    author_link = os.environ.get('AUTHOR_LINK')
    author_name = os.environ.get('AUTHOR_NAME')
    about_author = os.environ.get('ABOUT_AUTHOR')

    INDUSTRY_KEYWORD = os.environ.get('INDUSTRY_KEYWORD')

    CallToActionTitle = os.environ.get('CallToActionTitle')
    CallToActionButton = os.environ.get('CallToActionButton')
    CallToActionNo = os.environ.get('CallToActionButtonNo','No Thanks')

    date_iso = datetime.datetime.now().isoformat()
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    html = generate_html_from_markdown(
        markdown_content,
        html_title,
        PUBLICATION_TAGS,
        date_iso,
        author_name,
        author_link,
        about_author,
        CallToActionTitle,
        CallToActionButton,
        CallToActionNo
    )

    file_path = "data/" + INDUSTRY_KEYWORD + "/article.html"
    save_html_to_file(html, file_path)

if __name__ == "__main__":
    main()
