# -*- coding: utf-8 -*-
import re
import inspect

# TINYMCE-Editor toggle button
if session.tinymce_enabled is None:
    session.tinymce_enabled = 'off'
tinymce_checkbutton = SPAN('WYSIWYG ',
                         INPUT(_type='checkbox',
                               _class='boolean',
                               _id='WYSIWYG',
                               _value= session.tinymce_enabled,
                               _checked = True if session.tinymce_enabled == 'on' else False,
                               _onclick="toggle_tinymce_checkbutton('WYSIWYG','cm_pages_body');",
                               ))

def lineno():
    """ Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

def _dict_print(what):
    """ Print a dictionary readable for humans """
    for key, value in sorted(what.items()):
        print(key,value)

regex_URL=re.compile(r'@/(?P<a>\w*)/(?P<c>\w*)/(?P<f>\w*(\.\w+)?)(/(?P<args>[\w\.\-/]+))?')
def replace_at_urls(text,url):
    """
    Transform media all links in a string into absolute urls
    ex: text='src="@/a/c/f/15/image.jpg"' ==> r=src="http://localhost:8080/a/c/f/15/image.jpg"
    This is taken from gluon/contrib/markmin/makmin2html.py
    """
    def pattern(match,url=url):
        a,c,f,args = match.group('a','c','f','args')
        r = url(a=a or None,c=c or None,f = f or None,
                   args=(args or '').split('/'), scheme=True, host=True)
        return r
    r = regex_URL.sub(pattern,text)
    return r    # String

def URLx(a,c,f,args,scheme=False,host=False):
    """
    Special dynamic url generation. http://..../[app]/default/download/[filename]
    Called in regex_URL.sub(...) passed to replace_at_urls(text,ur1) as 2nd formal parameter.
    [attention: only possible in functional programming - mind blowing functional hack!]
    """
    id = args[0]
    real_filename = db.cm_images[id].file        
#    print lineno(),id,real_filename
    r = URL(a=a or None,c=c or None,f ='download',
               args=[real_filename], scheme=scheme, host=host)
    return r

#db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
db = DAL("sqlite://storage.sqlite")

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

## (optional) static assets folder versioning
# response.static_version = '0.0.0'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################
# from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
# crud, service, plugins = Crud(db), Service(), PluginManager()
from gluon.tools import Auth

auth = Auth(db)

## configure email
mail = auth.settings.mailer
# mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.sender = 'wdklotz@gmail.com'
mail.settings.login = "wdklotz@gmail.com:Orang!na"
# mail.settings.tls = False
mail.settings.ssl = True

## configure auth policy
# auth.settings.registration_requires_verification = False
# auth.settings.registration_requires_approval = False
# auth.settings.reset_password_requires_verification = True

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################
## create all tables needed by auth if not custom tables

## after auth = Auth(db)
auth.settings.extra_fields['auth_user'] = [
	Field('identity_photo', 'upload'),
	Field('is_member','boolean', default=True, label="Rotarian"),
	Field('short_description', 'text'),
	Field('tel_number'),
	Field('mobile_number'),
	Field('email2',label="E-mail(alt.)")
]
## before auth.define_tables(username=False, signature=False)
auth.define_tables(username=False, signature=False)

db.define_table('address',
	Field('street', requires=IS_NOT_EMPTY(error_message='please enter street!')),
	Field('number', requires=[IS_NOT_EMPTY(error_message='please enter number!'),IS_ALPHANUMERIC(error_message='invalid number!')]),
	Field('zip_code', type='integer', requires=IS_NOT_EMPTY(error_message='please enter zip code!')),
	Field('town', requires=IS_NOT_EMPTY(error_message='please enter town!')),
	Field('country', requires=IS_NOT_EMPTY(error_message='please enter country!')),
	Field('tel_number',label="Tel. (at this location)"),
	Field('user_id', 'reference auth_user'),
	format = '%(number)s, %(street)s, %(zip_code)s, %(town)s')

db.auth_user.identity_photo.requires = IS_EMPTY_OR(IS_IMAGE())
db.auth_user.email.requires = [IS_NOT_EMPTY(error_message='please enter email!'),IS_EMAIL(error_message='invalid email!')]
db.auth_user.is_member.readable=db.auth_user.is_member.writable=False
db.address.user_id.writable=db.address.user_id.readable=False
db.address.id.readable=False

db.define_table('cm_pages',
	Field('slug',type='string',
          requires=[
                     IS_NOT_EMPTY(error_message='please enter a slug!'),
                     IS_SLUG(maxlen=80, check=True, error_message='must be slug (allowing only alphanumeric characters and non-repeated dashes)')]),
	Field('title',type='string',notnull=False),
	Field('body',type='text',length='65536'),  # 65K for text
    Field('publish',type='boolean',default=False),
    singular="Page",plural='Pages',
	format='%(slug)s')

db.cm_pages.slug.requires = IS_NOT_IN_DB(db, db.cm_pages.slug)
#print('db.py %s - table: %s - fields: ' %(lineno(),'cm_pages'),db.cm_pages.fields)

db.define_table('cm_images',
   Field('title',type='string'),
   Field('file', 'upload',autodelete=True,requires = IS_IMAGE(extensions=('jpeg', 'png','jpg'))),
   Field('in_page','reference cm_pages'),
   singular="Image",plural="Images",
   format = '%(title)s')   

db.cm_images.in_page.requires = IS_IN_DB(db,'cm_pages.id','%(slug)s',zero='chose one')
#print('db.py %s - table: %s - fields: ' %(lineno(),'cm_images'),db.cm_images.fields)

db.define_table('cm_defaults',
    Field('caption',default='def_id_photo'),
    Field('def_id_photo','upload'))

## after defining tables, uncomment below to enable auditing
#auth.enable_record_versioning(db)

#--------------------------------old stuff--------------------------------------
#def use_html():
#	return auth.wiki(resolve=False,render='html')
#def use_markdown():
#	def mrkdwn2wrapper(text): #wrapper to get text from Storage (wdk)
#		import gluon.contrib.markdown.markdown2
#		body = text.body
#		return gluon.contrib.markdown.markdown2.Markdown().convert(body)
#	return auth.wiki(resolve=False,render=mrkdwn2wrapper)
##	return auth.wiki(resolve=False,render="markdown")
#def use_markmin():
#	customMarkup = dict(sub=lambda x:'<sub>'+x+'</sub>',sup=lambda x:'<sup>'+x+'</sup>')
#	return auth.wiki(resolve=False,extra=customMarkup)
#
#use_render=dict(html=use_html,markdown=use_markdown,markmin=use_markmin)

#To allow access to the wiki specific db setup within the model of your app you must add the
#    following sentence to your model file (i.e. db.py)
# Make sure this is called after the auth instance is created
#     and before any change to the wiki tables (wdk)
#use_render['markmin']()
#use_render['markdown']()
#use_render['html']()
