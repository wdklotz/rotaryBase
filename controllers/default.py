# -*- coding: utf-8 -*-
from string import  rsplit
import logging

logger = logging.getLogger('rotary')
logger.setLevel(logging.INFO)

def index():
    logger.debug("%s",'index()')
    if False:   # site closed !
        url  = URL('static','images/construction.png')
        body = XML("<img src='"+url+"'/><p>Sorry site closed for maintenance!</p>")
        return HTML(BODY(H1(body,_style="color: red;")))

    pages = db(db.cm_pages.id>0 and db.cm_pages.publish==True).select()
#    pages = []    # test for empty table
    if len(pages) == 0:
        return dict(message=T('Welcome to Rotary!'),pages=[])
    for page in pages:   # all published wiki pages
        page.body = replace_at_urls(page.body,URLx)# here comes the hack! Function object URLx passed not URL!
    return dict(message=T('Welcome to Rotary!'),pages=pages)

@auth.requires_login()
def create_page():
    logger.debug("%s",'create_page()')
#    print lineno(),request.function,request.args,request.vars

    if request.ajax and '_toggle' in request.args:       # $.post('_toggle',...) lands here
        session.tinymce_enabled = request.vars.state
        return

    if len(request.args) == 0:
        form=dict()
    elif '_create' in request.args:
        form=SQLFORM(db.cm_pages).process()
        form[0].insert(2,tinymce_checkbutton)   # position the tinymce checkbutton
        if form.accepted:
            page_ID = form.vars.id
            session.flash='page accepted'
            redirect(URL(args=["_preview",page_ID]))
        elif form.errors:
            response.flash='form has errors'
        else:
            response.flash='please fill out the form'  
    elif '_preview' in request.args:
        page_ID = request.args[1]
        page = db(db.cm_pages.id == page_ID).select().first()
        page.body = replace_at_urls(page.body,URLx)# here comes the hack! Function object URLx passed not URL!
        return dict(title = page.title, body = XML(page.body))
    return dict(form=form)

@auth.requires_login()
def manage_pages():
    logger.debug("%s",'manage_pages()')
#    print lineno(),request.function,request.args,request.vars

    if request.ajax and '_toggle' in request.args:       # $.post('_toggle',...) lands here
        session.tinymce_enabled = request.vars.state
        return

    footnote = True
    custom_items=dict(page_title='Pages',button=dict(url=URL('manage_media'),label='Media'),visible=True)
    view_btn = XML('<span class="icon magnifier icon-zoom-in glyphicon glyphicon-eye-open"></span><span class="buttontext button" title="Preview">''</span>')
    custom_links = [dict(header='Preview¹',body=lambda row:A(view_btn,_class='button btn btn-default',_href=URL('create_page',args=['_preview',row.id,'']))),]

    if request.args == ['cm_pages', 'new', 'cm_pages']:
        grid = SQLFORM(db.cm_pages).process()
        grid[0].insert(-4,tinymce_checkbutton)   # position the tinymce checkbutton
        footnote = False
        if grid.accepted:
            session.flash="page accepted"
            redirect(URL())
        elif grid.errors:
            response.flash='form has errors'
        else:
            response.flash='please fill out the form'  

    else:
        grid=SQLFORM.smartgrid(db.cm_pages, 
           details=True, 
           csv=False, 
           create=True, 
           paginate=10,
           linked_tables=['cm_images'],
           links=dict(cm_pages=custom_links,cm_images=[]),
           oncreate=on_image_in_page_create,)

    if 'edit' in request.args:
        grid[2][0].insert(3,tinymce_checkbutton)   # postion the tinymce checkbutton
        footnote = False

    if 'view' in request.args or 'cm_images.in_page' in request.args:
        footnote = False
        
    return dict(grid=grid,custom_items=custom_items,footnote=footnote)

@auth.requires_login()
def manage_media():
    logger.debug("%s",'manage_media()')
#    print lineno(),request.function,request.args
    footnote=True
    custom_links = [dict(header='Media Link¹',body=lambda row: A('copy',_href=URL('copy_media_link',args=[row.id,row.title,row.file,row.in_page]))),]

    if 'new' in request.args:
        footnote=False
        grid = SQLFORM(db.cm_images)
        if grid.process().accepted:
            response.flash="media accepted"
            row = db(db.cm_images.id == grid.vars.id).select().first()
            redirect(URL('copy_media_link',args=[row.id,row.title,row.file,row.in_page]))
        elif grid.errors:
            response.flash='form has errors'
        else:
            response.flash='please fill out the form'  

    else:
        grid = SQLFORM.grid(db.cm_images,
             details=True,
             csv=False,
             create=True,
             paginate=10,
             links=custom_links)

    if 'view' in request.args or 'edit' in request.args:
        footnote=False

    return dict(grid=grid,footnote=footnote)

@auth.requires_login()
def copy_media_link():
    """ copy the media link to the page source """
    logger.debug("%s",'copy_media_link()')
#    print lineno(),request.function,request.args
    args = request.args
    if len(args) != 4: 
        session.flash = "Medium not linked to a page!"
        redirect(URL('manage_media'))
    args=dict(image_id=args[0],image_title=args[1],image_file=args[2],page_id=args[3])
    page = db.cm_pages[args['page_id']]
    body = page.body
    suffix = rsplit(args['image_file'],".",1)[1]
    media_link="@////"+str(args['image_id'])+"/"+args['image_title']+"."+suffix
    body = body+"\n<!-- "+media_link+" -->"
    page.update_record(body=body)
    session.flash="Link pasted to page \""+page.slug+"\""
    redirect(URL('manage_pages'))
    return

def fluid():
    logger.debug("%s",'fluid()')
    pages = db(db.cm_pages.id > 0 and db.cm_pages.dashboard == True).select()
#    pages = []    # test for empty table
    if len(pages) == 0:
        return dict(message=T('Welcome to Rotary!'),pages=[])
    for page in pages:   # all dashboard pages
        page.body = replace_at_urls(page.body,URLx)# here comes the hack! Function object URLx passed not URL!
    return dict(pages=pages)

def user():
    logger.debug("%s",'user()')
    if request.args[0] == "register":
        request.vars._next=URL("new_registration") # next action after registration form
    return dict(form=auth())  

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
    """ allows downloading of uploaded files http://..../[app]/default/download/[filename] """
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

#----------------------------------legacy and test stuff-------------------------------------------
#def show_media():
##    display individual media
#    logger.debug("%s",'show_media()')
#    image = db.cm_images(request.args(0,cast=int)) or redirect(URL('index'))
#    return locals()

#def iframe():
#    return XML('<iframe width="900" height="1200" scrolling="auto" src="http://matthewjamestaylor.com/blog/perfect-2-column-left-menu.htm"><p>Your browser does not support iframes.</p></iframe>')

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




