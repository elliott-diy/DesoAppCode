import os

import deso
from deta import Deta
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from models import Credentials, Post

load_dotenv()
middleware = [Middleware(SessionMiddleware, secret_key=os.urandom(24).hex())]
app = FastAPI(middleware=middleware)
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')
deta = Deta(os.getenv('DETA_PROJECT_KEY'))
post_db = deta.Base('posts')


async def get_credentials(request: Request):
    public_key = request.session.get('public_key')
    seed_hex = request.session.get('seed_hex')
    access_level = request.session.get('access_level')
    access_level_hmac = request.session.get('access_level_hmac')
    if not public_key or not seed_hex or not access_level or not access_level_hmac:
        raise HTTPException(401)
    credentials = Credentials(
        public_key=public_key,
        seed_hex=seed_hex,
        access_level=access_level,
        access_level_hmac=access_level_hmac,
    )
    return credentials


@app.get('/')
async def root():
    return RedirectResponse('/chain/root')


@app.get('/chain/{chain_name}', response_class=HTMLResponse)
async def show_chain(request: Request, chain_name: str):
    if not request.session.get('public_key'):
        show_login_button = True
        credentials = None
    else:
        show_login_button = False
        credentials = await get_credentials(request)
    context = {
        'request': request,
        'deso': deso,
        'show_login_button': show_login_button,
        'posts': post_db.fetch(query={'chain': chain_name}, limit=10).items,
    }
    if credentials:
        user = deso.User()
        profile_info = user.getSingleProfile(publicKey=credentials.public_key).json()
        photo_url = user.getProfilePicURL(credentials.public_key)
        context['username'] = profile_info['Profile']['Username']
        context['photo_url'] = photo_url
    return templates.TemplateResponse(
        'chain.html',
        context,
    )


@app.get('/user/{username}', response_class=HTMLResponse)
async def show_user(request: Request, username: str):
    user = deso.User()
    if username == 'me':
        credentials = await get_credentials(request)
        profile_info = user.getSingleProfile(publicKey=credentials.public_key).json()
        return RedirectResponse(f"/user/{profile_info['Profile']['Username']}")
    else:
        profile_info = user.getSingleProfile(username=username).json()
    if profile_info.get('error'):
        raise HTTPException(404)
    public_key = profile_info['Profile']['PublicKeyBase58Check']
    photo_url = user.getProfilePicURL(public_key)
    return templates.TemplateResponse(
        'user.html',
        {
            'request': request,
            'username': profile_info['Profile']['Username'],
            'description': profile_info['Profile']['Description'],
            'photo_url': photo_url,
        },
    )


# TODO: Add single post frontend page
# @app.get('/post/{id}', response_class=HTMLResponse)
# async def show_post(request: Request, id: str):
#     post = post_db.get(id)
#     if not post:
#         raise HTTPException(404)
#     post = Post.parse_obj(post)
#     return templates.TemplateResponse(
#         'post.html',
#         {
#             'request': request,
#             'title': post.title,
#             'content': post.content,
#         },
#     )


@app.get('/login')
async def login(request: Request):
    return templates.TemplateResponse(
        'login.html',
        {'request': request},
    )


@app.post('/api/auth')
async def api_auth(request: Request, credentials: Credentials):
    for key, value in credentials.dict().items():
        request.session[key] = value


@app.post('/api/create_post')
async def api_create_post(post: Post, credentials: Credentials = Depends(get_credentials)):
    if credentials.public_key != post.public_key:
        raise HTTPException(401)
    post_db.put(post.dict(), post.id)
    return {'id': post.id}


@app.exception_handler(401)
async def unauthorized_handler(request: Request, exception):
    if '/api' not in request.url.path and request.method == 'GET':
        return RedirectResponse(f'/login?returnUrl={str(request.url)}')
    else:
        return await http_exception_handler(request, exception)


@app.exception_handler(404)
async def not_found_handler(request: Request, exception):
    return templates.TemplateResponse(
        '404.html',
        {'request': request},
    )
