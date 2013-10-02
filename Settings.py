""" All settings related to the site.

    Main place for customizations.

"""

class Settings(object):

    """ Site configuations, options, templates go here.

    """




    ## how many articles shall we include in each page?
    ARTICLES_PER_PAGE = 10

    ### add these big html blocks at the end as it confuses editor highlighting support.
    
    HEADER = """\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>$title</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="$author">

    <!-- Le styles -->
    <link href="http://netdna.bootstrapcdn.com/bootswatch/3.0.0/flatly/bootstrap.min.css" rel="stylesheet">

    <style>
    body {
      margin-top: 100px; 
      }
    footer {
      margin: 50px 0;
      }
    .glyphicon {
      font-size: 0.5 em;
      }
    </style>

    <!-- HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->

  </head>

  <body>

    <nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-ex1-collapse">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="./index.html">QuietCasting</a>
        </div>

        <!-- Collect the nav links, forms, and other content for toggling -->
        <div class="collapse navbar-collapse navbar-ex1-collapse">
          <ul class="nav navbar-nav">
            <li><a href="./about.html">About</a></li>
          </ul>
        </div><!-- /.navbar-collapse -->
      </div><!-- /.container -->
    </nav>

  
    <div class="container">

"""


    FOOTER = """\
      <hr>
      <footer>
        <div class="row">
          <div class="col-lg-12">

      <p>Copyright &copy; QuietCasting.com &middot; $author</p>
          </div>
        </div>      
      </footer>
    </div> <!-- /container -->

    <!-- Le javascript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.0/jquery.min.js"></script>
    <script src="http://netdna.bootstrapcdn.com/bootstrap/3.0.0/js/bootstrap.min.js"></script>
  </body>
</html>
"""

