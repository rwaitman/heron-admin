'''genshi_render.py -- Use genshi to render Pyramid views
---------------------------------------------------------

'''

import logging
import os

# from PyPI - the Python Package Index http://pypi.python.org/pypi
from genshi.template import TemplateLoader

log = logging.getLogger(__name__)


class Factory(object):
    docroot = os.path.join(os.path.dirname(__file__), 'templates/')

    def __init__(self, info):
        #docroot = info.settings['templates']
        self._loader = TemplateLoader([self.docroot], auto_reload=True)

    def __call__(self, value, system):
        log.debug('genshi template: %s', system['renderer_name'])
        tmpl = self._loader.load(system['renderer_name'])
        return tmpl.generate(**value).render('xhtml')
