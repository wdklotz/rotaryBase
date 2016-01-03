# -*- coding: utf-8 -*-

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
mail.settings.login = "wdklotz@gmail.com:SV@lbard2598"
# mail.settings.tls = False
# mail.settings.ssl = True

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

## after defining tables, uncomment below to enable auditing
auth.enable_record_versioning(db)

#To allow access to the wiki specific db setup within the model of your app you must add the
#    following sentence to your model file (i.e. db.py)
# Make sure this is called after the auth instance is created
#     and before any change to the wiki tables
customMarkup = dict(sub=lambda x:'<sub>'+x+'</sub>',sup=lambda x:'<sup>'+x+'</sup>')
auth.wiki(resolve=False,extra=customMarkup)
