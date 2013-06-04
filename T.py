""" T is new Python template language inspired by James Casbon's:

    https://gist.github.com/1461441

    Extremely useful in situations requiring generation of HTML within
    python code.

    Nothing new to learn, does not 'invent' a new language or DSL and as
    pythonic as it can be.

"""

from string import Template
import datetime

TAB = "  "



class T(object):

    """ A template object has a name, attributes and content.

        The contents may contain sub template objects.

        Attributes are kept in order.

        The only rules one has to remember:

          * use the '<' operator to add content to a template object.

          * elements can receive attributes in the constructor. The 2
            most common attributes, 'class' and 'id' may be passed as
            the first and second positional arguments
            respectively. Further attributes may be provided as
            key=value arguments to the constructor. Attributes that
            are not valid python identifiers may be set using the
            element method .set() or provided in the constructor as a
            dict using the argument 'attr'.
    """

    def __init__(self, name = None, enable_interpolation = False):

        """ 'name' of element. Root object will usually have an emoty name.

             'enable_interpolation' enables string substitution to the
             final document using the rules of the standard python
             library string.Template. If enabled the ._render(**
             parameters) method applies the '** parameters' received
             to the string.Template object.

        """
        
        self.__name = name
        self.__multi_line = False
        self.__contents = []
        self.__attributes = []
        self.__enable_interpolation = enable_interpolation


    def __open(self, level = -1, **namespace):
        out = ["{0}<{1}".format(TAB * level, self.__name)]
        for (name, value) in self.__attributes:
            out.append(' {0}="{1}"'.format(name, value))
        out.append(">")
        
        if self.__multi_line:
            out.append("\n")

        templ = ''.join(out)

        if self.__enable_interpolation:
            txt = Template(templ).substitute(** namespace)
        else:
            txt = templ
            
        return txt


    def __close(self, level = -1, **namespace):

        if self.__multi_line:
            txt = "\n{0}</{1}>\n".format(TAB * level, self.__name) 
        else:
            txt = "</{0}>\n".format(self.__name)
        return txt


    # public API

    def _render(self, level = -1, **namespace):

        out = []

        out_contents = []

        contents = self.__contents

        for item in contents:
            if item is None:
                continue

            ## do some default type conversions here
            if type(item) is T:
                self.__multi_line = True
                out_contents.append(item._render(level = level + 1, **namespace))

            elif type(item) is datetime.datetime:
                out_contents.append(item.strftime("%Y-%m-%d %H:%M:%S"))

            elif type(item) is float or type(item) is int:
                out_contents.append(str(item))

            ## assume string or string.Template
            else:
                if self.__enable_interpolation:
                    txt = Template(item).substitute(**namespace)
                else:
                    txt = item
                out_contents.append(
                    "{0}{1}".format(
                        TAB * level,
                        txt,
                        )
                    )

        txt_contents = ''.join(out_contents)

        if not self.__multi_line:
            txt_contents = txt_contents.strip()
        else:
            txt_contents = txt_contents.rstrip()

        if self.__name:
            out.append(self.__open(level, **namespace))
            out.append(txt_contents)
            out.append(self.__close(level, **namespace))
        else:
            out.append(txt_contents)

        return ''.join(out)


    def __getattr__(self, name):
        t = self.__class__(
            name,
            enable_interpolation = self.__enable_interpolation,
            )
        self < t
        return t


    def __setattr__(self, name, value):
        if name.startswith('_'):
            self.__dict__[name] = value
        else:
            ## everything else is an element attribute
            ## strip trailing underscores
            self.__attributes.append((name.rstrip('_'), value))


    def _set(self, name, value):

        """ settings of attributes when attribure name is not a valid python
            identifier.

        """

        self.__attributes.append((name.rstrip('_'), value))
        

    def __lt__(self, other):
        self.__contents.append(other)
        return self


    def __call__(self, _class = None, _id = None, attr = None, **kws):

        other = {}    
        if attr:
            other.update(attr)
        if kws:
            other.update(kws)

        # explcitly providing the class and id attributes has priority
        # over dict provided info.
        if _class:
            other.pop('class', None)
            self._set('class', _class)
        if _id:
            other.pop('id', None)
            self._set('id', _id)

        if other:
            keys = other.keys()
            keys.sort()
            for key in keys:
                self._set(key, attr[key])

        return self
    

    ## with interface
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        return False





def example():

    doc = T(enable_interpolation = True)
    doc < """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
\n"""


    ## we can create a second template object and add it to any other template object.
    
    footer = T()
    with footer.div('footer', 'foot1').h3.p.pre as pre:
        pre.style = 'some style'
        pre < 'Copyright T inc'


    with doc.html as html:

        with html.head as head:
            ## element attributes are set the usual way. 
            head.title = 'Good morning ${name}!'
            
        with html.body as body:

            ## there is no need to use the with statement. It is useful for
            ## provide=ing structure and clarity to the code.

            body.h3('main', attr = {'non-valid-python-attribute-name': 'warning'}) < "Header 3"

            ## with statement
            with body.p as p:
                p.class_ ="some class"
                p < "First paragraph"

            ## same as above but without the 'with' statement
            body.p("some class") < "First paragraph"


            with body.ul as ul:
                for i in range(10):
                    ul.li < str(i)

            with body.p as p:
                p < "test inline html"
                p.b("bold")

            ## append a template object
            body < footer
            
    return doc



if __name__ == "__main__":

    doc = example()
    html = doc._render(name = 'Clio')
    print html
    

