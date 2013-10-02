""" Journal generator.

    Takes a Journal text file and generates a Boostrap.js based journal site.

"""


from T import T
from Settings import Settings
import re
import argparse
import datetime
import os
from collections import defaultdict


try:
    from markdown import markdown
except ImportError:
    print 'WARNING: Markdown not available.'
    def markdown(txt):
        out = '<p>%s</p>' % txt
        return out
    

### Globals

SUMMARY_LEN = 10000

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
        

    def sort(self):

        """ sort on article date, newer first.

        """

        self.articles.sort(lambda a,b: cmp(a.date, b.date))
        self.articles.reverse()

        

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


    def get_archives_set(self):

        out = []

        d = defaultdict(list)
        for article in self.articles:
            l = d[article.date.strftime("%B %Y")]
            l.append(article)

        for _tuple in sorted(d.items()):
            out.append(_tuple)

        return out


    def get_chapters_set(self):

        out = []

        d = defaultdict(list)
        for article in self.articles:
            l = d[(article.chapter_i, article.chapter)]
            l.append(article)

        for ((chapter_i, chapter), articles) in sorted(d.items()):
            out.append((chapter, articles))

        return out


    def create_nav(self):
        """ create chapter and topic links.

        """


        nav = T(enable_interpolation = True)
        # do chapters
        chapters = self.get_chapters_set()
        with nav.div("well") as well:
            well.h4 < "Chapters"
            with well.ul("list-unstyled") as ul:
                for (title, articles) in chapters:
                    if articles:
                        with ul.li as li:
                            #li.span < "&nbsp;%s.&nbsp;" % articles[0].chapter_i
                            li.a(href = "./%s.html" % articles[0].chapter_ref) < title

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

        # do recent
        with nav.div("well") as well:
            well.h4 < "Recent"
            with well.ul("list-unstyled") as ul:
                for article in self.articles[:20]:
                    with ul.li as li:
                        li.a(href = "./%s.html" % article.ref) < article.title
                        li < "&nbsp;"
                        li.span(style = "font-size: 0.7em;") < article.date.strftime("%b %d, %Y")

                    
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

        self.sort()
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

        ## chapter pages
        chapters = self.get_chapters_set()
        for (title, articles) in chapters:
            chapter = T(enable_interpolation = True)
            chapter.h3 < "Chapter:&nbsp;%s"  % title 
            for article in articles:
                chapter < article.create_content()
                chapter.hr
                chapter.br
                chapter_html = self.create_page(chapter)._render(** nmsp)
                open(
                    os.path.join(
                        target_dir, 
                        '%s.html' % articles[0].chapter_ref
                        ), 
                    'w'
                    ).write(chapter_html)
                
        ## topic pages
        topics = self.get_topics_set()
        for (title, articles) in topics:
            topic = T(enable_interpolation = True)
            topic.h3 < "Topic:&nbsp;%s"  % title 
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
                 chapter = None,
                 chapter_i = None,
                 ref = None,
                 content = None,
                 ):
        
        self.title = title
        self.author = author
        self.date = date
        self.topic= topic
        self.chapter = chapter
        self.chapter_i = chapter_i
        self.content = content
        self.content_html = None
        

        self.chapter_ref = make_ref(chapter)
        self.topic_ref = make_ref(topic)
        self.ref = make_ref(title)



    def cut_summary(self):
        """ cut some initial part of a text block and return it as
            summary.

            XXX a cleverer approach is needed.

        """

        return self.content[:SUMMARY_LEN]

        
    def create_summary(self):

        """ create a summary for article.

        """

        doc = T(enable_interpolation = True)

        doc.h3 < self.title
        doc.strong < self.date.strftime("%B %d, %Y")
        doc < ' / '
        doc.strong < self.chapter

        if self.topic:
            doc < ' / '
            doc.strong < self.topic

        txt = self.content_html
        if len(txt) <= SUMMARY_LEN:
            doc < txt

        else:
            partial_txt = markdown(self.cut_summary() + ' ')
            doc < partial_txt
            with doc.a("btn") as a:
                a.href = "./%s.html#%s" % (self.chapter_ref, self.ref)
                a < "Read more &raquo;"

        ## I like this T template more and more ...!

        return doc



    def create_content(self):

        """ create content for article.

        """

        doc = T(enable_interpolation = True)
        doc.h3.a(href="./%s.html" % self.ref) < self.title
        doc.hr
        doc.a(href="./%s.html" % self.chapter_ref) < self.chapter

        if self.topic:
            doc < '&nbsp;&nbsp;&middot;&nbsp;&nbsp;'
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

    CHAPTER_RE = re.compile('\s*chapter:\s*(.*)\s*', re.IGNORECASE)
    ARTICLE_RE = re.compile('\s*article:\s*(.*)\s*', re.IGNORECASE)
    SETTING_RE = re.compile('\s*(journal|date|author|chapter|article|topic):\s*(.*)\s*', re.IGNORECASE)


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


    ## split txt into chapters
    parts = CHAPTER_RE.split(txt)
    journal_header = parts[0]

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
    chapter_blocks = parts[1:]
    chapter_i = 0
    for (chapter_title, chapter_block) in zip(chapter_blocks[::2], chapter_blocks[1::2]):
        print '  Processing Chapter: %s' % chapter_title
        print 
        ## split chapter blocks into consituent articles
        parts = ARTICLE_RE.split(chapter_block)
        chapter_header = parts[0]
        ## we have no futrther chapter settings or about section so we can stop here.
        article_blocks = parts[1:]
        chapter_i += 1
        for (article_title, article_block) in zip(article_blocks[::2], article_blocks[1::2]):
            print '    Processing Article: %s' % article_title
            print
            (article_settings, content) = process_block(article_block)

            article = Article(
                title = article_title,
                author = article_settings.get('author'),
                date = parse_date(article_settings.get('date')),
                topic = article_settings.get('topic'),
                chapter = chapter_title,
                chapter_i = chapter_i,
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
