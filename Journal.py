""" Journal generator.

    Takes a Journal text file and generates a Boostrap.js based journal site.

"""


import re
import os
import argparse
import datetime
from collections import defaultdict
from T import T
from Settings import Settings


try:
    from markdown import markdown
except ImportError:
    print 'WARNING: Markdown not available.'
    def markdown(txt):
        out = '<p>%s</p>' % txt
        return out
    

### Globals
_debug = 0


### helpers

def format_date(date):

    return date.strftime("%Y-%m-%d %H:%M:%S")


def parse_date(iso_string):
    """ parse iso formatted date string.

    """
    d = datetime.datetime(* tuple([int(i) for i in iso_string.strip().split('-')]))
    return d


MAKE_REF_RE = re.compile('[^a-z0-9]+', re.IGNORECASE)

def make_ref(txt):
    """ create a file name valid ref from an arbitrary name.

    """

    ref = MAKE_REF_RE.sub('_', txt).lower()
    return ref
    

###



class Journal(object):

    """ object representing a journal.

    """

    def __init__(self,
                 title = None,
                 author = None,
                 date = None,
                 about = None,
                 ):
        self.title = title
        self.author = author
        self.date = date
        self.about = about
        self.about_html = None
        
        self.articles = []

        self.settings = Settings()
        

    def add(self, article):

        if article.author is None:
            article.author = self.author

        self.articles.append(article)
        

    def get_recent_set(self, count = 5):

        """ get 'count' most recent articles.

        """

        
        out = sorted(
            self.articles, 
            cmp = lambda a,b: cmp(a.date, b.date), 
            reverse = True
            )[:count]

        return out

        

    def convert_markdown(self):
        if self.about:
            self.about_html = markdown(self.about)

        for article in self.articles:
            if article.content:
                article.content_html = markdown(article.content)
    

    def get_topics_set(self):

        out = []

        d = defaultdict(list)
        for article in self.articles:
            l = d[article.topic]
            l.append(article)

        for _tuple in sorted(d.items()):
            out.append(_tuple)

        return out


    def create_nav(self):
        """ create chapter and topic links.

        """


        nav = T(enable_interpolation = True)

        # do recent
        with nav.div("well") as well:
            well.h4 < "Recent"
            with well.ul("list-unstyled") as ul:
                for article in self.get_recent_set():
                    with ul.li as li:
                        li.a(href = "./%s.html" % article.ref) < article.title
                        li < "&nbsp;&middot;&nbsp;"
                        li.span(style = "font-size: 0.7em;").a(href = "./%s.html" % article.topic_ref) < article.topic
                        li < "&nbsp;"
                        li.span(style = "font-size: 0.7em;") < article.date.strftime("%b %d, %Y")


        ## do source code references to github
        with nav.div("well") as well:
            well.h4 < "Code"
            well.a(href = "https://github.com/pavlos-christoforou/web") < "Journal.py"
            well < " - A very easy to use, single file static data generator."
            well.br
            well.a(href = "https://github.com/pavlos-christoforou/web") < "T.py"
            well < " - A very easy to use, easy to read single file templating engine."  
            well.br
            well.a(href = "https://github.com/pavlos-christoforou/bitcoin") < "Wallet.py"
            well < " - A single file deterministic bitcoin address generator with no external dependencies."  
                
        
        ## do all articles
        with nav.div("well") as well:
            well.h4 < "Contents"
            with well.ul("list-unstyled") as ul:
                for article in self.articles:
                    with ul.li as li:
                        li.a(href = "./%s.html" % article.ref) < article.title
                        li < "&nbsp;&middot;&nbsp;"
                        li.span(style = "font-size: 0.7em;").a(href = "./%s.html" % article.topic_ref) < article.topic
                        li < "&nbsp;"
                        li.span(style = "font-size: 0.7em;") < article.date.strftime("%b %d, %Y")


            
        
        # do topics
        topics = self.get_topics_set()
        len_topics = len(topics)
        len_left = int(len_topics / 2.0 + 0.6)

        with nav.div("well") as well:
            well.h4 < "Topics"
            with well.div("row") as row:
                with row.div("col-lg-6").ul("list-unstyled") as ul:
                    for (title, articles) in topics[:len_left]:
                        if articles:
                            with ul.li as li:
                                li.a(href = "./%s.html" % articles[0].topic_ref) < title
                                
                with row.div("col-lg-6").ul("list-unstyled") as ul:
                    for (title, articles) in topics[len_left:]:
                        if articles:
                            with ul.li as li:
                                li.a(href = "./%s.html" % articles[0].topic_ref) < title

                    
        return nav



        
    def create_page(self, page_content):

        doc = T(enable_interpolation = True)
        doc < self.settings.HEADER

        with doc.div("row") as main:
            with main.div("col-lg-8") as text:
                text < page_content

            with main.div("col-lg-4") as nav:
                nav < self.create_nav()
                    

        doc < self.settings.FOOTER

        return doc

        

    def get_namespace(self):
        """ create a namespace for the _render method of the final
            document. Any python string.Template substitutions will be
            looked up in this namespace.

        """

        nmsp = self.settings.__dict__.copy()
        nmsp.update(self.__dict__.copy())

        return nmsp

        

    def create_site(self, target_dir):

        self.convert_markdown()
        nmsp = self.get_namespace()

        ## create about page
        about = self.create_page(self.about_html)._render(** nmsp)
        open(os.path.join(target_dir, 'about.html'), 'w').write(about)

        ## index page
        text = T(enable_interpolation = True)
        for article in self.articles:
            text < article.create_content()
            text.hr
            text.br
        index = self.create_page(text)._render(** nmsp)
        open(os.path.join(target_dir, 'index.html'), 'w').write(index)

                
        ## topic pages
        topics = self.get_topics_set()
        for (title, articles) in topics:
            topic = T(enable_interpolation = True)
            for article in articles:
                topic < article.create_content()
                topic.hr
                topic.br
                topic_html = self.create_page(topic)._render(** nmsp)
                open(
                    os.path.join(
                        target_dir, 
                        '%s.html' % articles[0].topic_ref
                        ), 
                    'w'
                    ).write(topic_html)
                

        ## individual articles
        for article in self.articles:
            article_html = self.create_page(article.create_content())._render(** nmsp)
            open(
                os.path.join(
                    target_dir, 
                    '%s.html' % article.ref
                    ), 
                'w'
                ).write(article_html)
                
                


class Article(object):

    """ object representing a journal article.

    """


    def __init__(self,
                 title = None,
                 author = None,
                 date = None,
                 topic = None,
                 ref = None,
                 content = None,
                 ):
        
        self.title = title
        self.author = author
        self.date = date
        self.topic= topic
        self.content = content
        self.content_html = None

        self.topic_ref = make_ref(topic)
        self.ref = make_ref(title)


        
    def create_content(self):

        """ create content for article.

        """

        doc = T(enable_interpolation = True)
        doc.h3.a(href="./%s.html" % self.ref) < self.title
        doc.hr
        doc.a(href="./%s.html" % self.topic_ref) < self.topic
        doc < '&nbsp;&nbsp;&middot;&nbsp;&nbsp;'
        doc < self.date.strftime("%B %d, %Y")
        doc < '&nbsp;&nbsp;&nbsp;&nbsp;'
        doc.a(href="./%s.html" % self.ref) < "Permalink"
        doc.hr
        doc < self.content_html

        return doc

        




def parse_source(txt):

    """ parse Journal contents and return a Journal object.

    """

    ARTICLE_RE = re.compile('\s*article:\s*(.*)\s*', re.IGNORECASE)
    SETTING_RE = re.compile('\s*(journal|date|author|article|topic):\s*(.*)\s*', re.IGNORECASE)


    def process_block(txt):

        """ process block of text, extracting any initial setting
            fields followed by any remaining text block.

        """

        settings = {}
        text = ''
        end_pos = 0
        
        while 1:
            match = SETTING_RE.match(txt, end_pos)
            if match:
                (key, value) = match.groups()
                settings[key.lower()] = value
                end_pos = match.end()
            else:
                text = txt[end_pos:]
                break

        return (settings, text)


    ## split txt into articles
    parts = ARTICLE_RE.split(txt)
    journal_header = parts.pop(0)

    ## process journal header
    (journal_settings, about) = process_block(journal_header)

    journal = Journal(
        title = journal_settings.get('journal'),
        date = parse_date(journal_settings.get('date')),
        author = journal_settings.get('author'),
        about = about.strip()
        )

    print 'Processing Journal: %s' % journal.title
    print

    while parts:
        article_title = parts.pop(0)
        article_block = parts.pop(0)

        print '    Processing Article: %s' % article_title
        print
        
        (article_settings, content) = process_block(article_block)

        article = Article(
            title = article_title,
            author = article_settings.get('author'),
            date = parse_date(article_settings.get('date')),
            topic = article_settings.get('topic'),
            content = content.strip()
            )
        
        
        journal.add(article)


    return journal



def cli():

    """ command line interface.

    """

    parser = argparse.ArgumentParser(
        description = 'Journal CLI',
        )
    
    parser.add_argument('source_file', help = "Journal source file")
    parser.add_argument('target_dir', help = "Target dir for generated html.")
    args = parser.parse_args()

    txt = open(args.source_file, 'r').read()
    journal = parse_source(txt)
    journal.create_site(args.target_dir)







if __name__ == '__main__':
    cli()
