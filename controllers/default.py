# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('rotary')
logger.setLevel(logging.INFO)

def index():
    logger.debug("%s",'index()')
    if False:
        redirect(URL('site_closed'))
    pages = db(db.cm_pages.id>0 and db.cm_pages.publish==True).select()
#    pages = []    # test for empty table
    if len(pages) == 0:
        return dict(message=T('Welcome to web2py!'),pages=[])
    else:
        return dict(message=T('Welcome to web2py!'),pages=pages)

@auth.requires_login()
def create_page():
#    create new page content
    logger.debug("%s",'create_page()')
    if len(request.args) == 0:
        form=dict()
    elif '_create' in request.args:
        form=SQLFORM(db.cm_pages).process()
        if form.accepted:
            page_ID = form.vars.id
            session.flash='page accepted'
            redirect(URL(args=["_preview",page_ID]))
        elif form.errors:
            response.flash='page has errors'
        else:
            response.flash='please fill out the form'  
    elif '_preview' in request.args:
        page_ID = request.args[1]
        page_record = db(db.cm_pages.id == page_ID).select().first()
        return dict(title = page_record.title, body = XML(page_record.body))
    return dict(form=form)

@auth.requires_login()
def manage_pages():
    logger.debug("%s",'manage_pages()')
    if len(request.args) != 0 and 'new' in request.args:
        form = SQLFORM(db.cm_pages).process()
        if form.accepted:
            session.flash="success: new page!"
            redirect(URL())
        elif form.errors:
            response.flash='page form has errors'
        else:
            response.flash='please fill out the form'  
        return dict(grid=form,media=False)

    view_button_xml = \
        XML('<span class="icon magnifier icon-zoom-in glyphicon glyphicon-eye-open"></span><span class="buttontext button" title="Preview">''</span>')
    custom_links = [
       dict(header='Preview¹',body=lambda row:A(view_button_xml,_class='button btn btn-default', \
                                        _href=URL('create_page',args=['_preview',row.id,'']))),]
    grid=SQLFORM.grid(db.cm_pages, details=True, csv=False, create=True, links=custom_links)
    return dict(grid=grid,media=True)

@auth.requires_login()
def manage_media():
    logger.debug("%s",'manage_media()')
    if len(request.args) != 0 and 'new' in request.args:
        form = SQLFORM(db.cm_images).process()
        if form.accepted:
            response.flash="success: new media link now on clipboard!"
            to_clipboard(form.vars.file)
            form.add_button("Page manager",URL('manage_pages'))
#            redirect(URL())
        elif form.errors:
            response.flash='image form has errors'
        else:
            response.flash='please fill out the form'  
        return dict(grid=form,pages=False)

    custom_links = [
       dict(header='Link¹',body=lambda row:A('copy',_href=URL('copy_media_link',args=[row.id]))),]
    grid = SQLFORM.grid(db.cm_images,details=True,csv=False,create=True,links=custom_links)
    return dict(grid=grid,pages=True)

def show_media():
#    display individual media
    logger.debug("%s",'show_media()')
    image = db.cm_images(request.args(0,cast=int)) or redirect(URL('index'))
    return locals()

@auth.requires_login()
def copy_media_link():
#    copy the media link to the clipboard
    logger.debug("%s",'copy_media_link()')
    image_ID=request.args(0,cast=int)
    image = db(db.cm_images.id == image_ID).select()[0]
    to_clipboard(image.file)
    redirect(URL('manage_media'))
    return

def site_closed():
    logger.debug("%s",'site_closed()')
    return dict()

def fluid():
    logger.debug("%s",'fluid()')
    response.fluid = "fluid_green"
    return dict()

def user():
    logger.debug("%s",'user()')
    if request.args[0] == "register":
        request.vars._next=URL("new_registration") # next action after registration form
    return dict(form=auth())  # same as: return {'form':auth()}

def new_registration():
    logger.debug("%s",'new_registration()')
    # default id_photo has caption=='def_id_photo' in cm_defaults
    def_id_photo = db(db.cm_defaults.caption=='def_id_photo').select().first().def_id_photo
    auth_record = db.auth_user(auth.user_id)
    # use default id_photo if none given
    if auth_record['identity_photo'] == '':
        auth_record.update_record(identity_photo=def_id_photo)
        db.commit()
    redirect(URL("index"))

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
    
def members():
    logger.debug("%s",'members()')
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
    logger.debug("%s",'register_address()')
    form=SQLFORM(db.address).process()
    if form.accepted:
        response.flash = 'address accepted'
        id = form.vars.id
        db.address[id] = dict(user_id = auth.user_id)  # link address entry with current user
    elif form.errors:
        response.flash = 'address has errors'
    else:
        response.flash = 'please fill out the form'	
    return dict(form=form)
	
def edit_addresses():
    logger.debug("%s",'edit_addresses()')
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




