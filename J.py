""" JQ is a jquery helper allowing easy AJAX manipulations.

"""

import json

class Selector(object):
    """ Dispatch jquery actions on a selector.

    """

    def __init__(self, selector = None):
        self.__selector = selector
        self.__actions = []
        self.__last_action = None

    def __getattr__(self, action):
        self.__last_action = action
        return self

    def __call__(self, *kws):
        self.__actions.append((self.__last_action, list(kws)))
        return self
    

    def _as_list(self):
        out = []
        for (action, params) in self.__actions:
            out.append(
                {'s': self.__selector,
                 'a': action,
                 'p': params,
                 }
                )
        
        return out


JS = """

var j_dispatch_function = function (selector, jQuery_method, jQuery_args) {
    var selection = jQuery(selector);
    selection[jQuery_method].apply(selection, jQuery_args);
};

jQuery(function($) {
    $('body').on('submit', 'form[form_async]', function(event) {
        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize(),

            success: function(data, status) {
             if (data.redirect) {
                // data.redirect contains the string URL to redirect to
                window.location.replace(data.redirect);
                }
             else {
                $.each(data, function(index, row ) {
                    j_dispatch_function(row.s, row.a, row.p);
                });
                  }  
             }
        });
        
        event.preventDefault();
    });
});



jQuery(function($) {
    $('body').on('click', '[add_data]', function(event) {
        var $button = $(this);
        var $form = $('#'.concat($button.attr('form')));
        $form.remove('[name="__extra_data"]');
        $form.append('<input type="hidden", name="__button_data", value = "'.concat($button.attr('add_data')).concat('"/>'));
    });
});



"""



def example():

    s = Selector('#buttona')
    s.empty().append('<li>one</li>')
    return s


if __name__ == "__main__":

    s = example()
    print s._as_list()
    

