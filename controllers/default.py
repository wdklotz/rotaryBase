# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('rotary')
logger.setLevel(logging.WARNING)

#print a dictionary readable for humans
def _dict_print(what):
    for key, value in sorted(what.items()):
        print(key,value)

def index():
    logger.info("%s",'index()')
#    response.flash = T("Hello World")
#    _dict_print(request.wsgi.environ)
    if False:
        redirect(URL('site_closed'))
    return dict(message=T('Welcome to web2py!'))

#def content():
#    logger.info("%s",'content()')
##    return auth.wiki(function='content',render='html')
##    return auth.wiki(function='content',extra=dict(sub=lambda x:"<sub>%s</sub>" % (x)))
##    return auth.wiki(extra=dict(sub=lambda x:'<sub>'+x+'</sub>'))
#    return auth.wiki()

def site_closed():
    logger.info("%s",'site_closed()')
    return dict()

def fluid():
    logger.info("%s",'fluid()')
    response.fluid = "fluid_green"
    return dict()

def user():
    logger.info("%s",'user()')
    if request.args[0] == "register":
        request.vars._next=URL("new_registration")
    return dict(form=auth())  # same as: return {'form':auth()}

def new_registration():
    logger.info("%s",'new_registration()')
    request.vars.request_is = request_is
    #	default id_photo
    default_identity_photo = 'auth_user.identity_photo.8b2b9c234feb78ce.66616365312e706e67.png'

    if auth.user_id:
    #	get just registered user record from auth
        auth_record = db.auth_user(auth.user_id)
    # 		use default id_photo if none given
        if auth_record['identity_photo'] == '':
            auth_record.update_record(identity_photo=default_identity_photo)
            db.commit()
        request.vars.auth_record = auth_record
    # 		redirect(URL("index",args=T("in register_and_store_in_db")))	
    # 		return dict( request_is = request_is, auth_record = auth_record)
        return dict()
    else:
    # 		return dict( request_is = request_is)
        return dict()

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
    
def members():
    logger.info("%s",'members()')
    members = []
    rows = db(db.auth_user.is_member == True).select()
    for member in rows:
        user_id = member['id']
        member_addresses=[] #a list of dicts: [{auth_user},{address},{address},...]
        member_addresses.append(member)
        for address in db(db.address.user_id == user_id).select():
            member_addresses.append(address)
        members.append(member_addresses)
    request.members = members #a list of lists: [[{auth_user},{address},{address},...],...]
    return dict()

def register_address():
    logger.info("%s",'register_address()')
    form=SQLFORM(db.address)
    if form.process().accepted:
        response.flash = 'address accepted'
        id = form.vars.id
        db.address[id] = dict(user_id = auth.user_id)  # link address entry with current user
    elif form.errors:
        response.flash = 'address has errors'
    else:
        response.flash = 'please fill out the form'	
    return dict(form=form)
	
def edit_addresses():
    logger.info("%s",'edit_addresses()')
    query = (db.address.user_id == auth.user_id)
    fields = [db.address.number,db.address.street, db.address.zip_code, db.address.town, db.address.country]
    headers={'address.number' : 'Bldg. Number'}
    grid = SQLFORM.grid(query,fields=fields, editable=True, csv=False, create=False, headers=headers, maxtextlength=40, details=True)
    return dict(grid=grid)

#a minimalistic WSGI application and how to call from web2py, i.e. the rocket server
#def app2(environ, start_response):
#    start_response("200 OK", [])
#    s = "<html>MESSAGE FROM APP2: You requested <strong>%s</strong></html>"
#    s %= environ['PATH_INFO']
#    return [s]
#class LowercaseMiddleware:
#    def __init__(self, application):
#        self.application = application   # A WSGI application callable.
#
#    def __call__(self, environ, start_response):
#        pass  # We could set an item in 'environ' or a local variable.
#        for chunk in self.application(environ, start_response):
#            yield chunk.lower()
#def moin():
#    app = LowercaseMiddleware(app2)
#    return app(request.wsgi.environ,request.wsgi.start_response)




