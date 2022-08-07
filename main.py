import os

import deso
from deta import Deta
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Depends
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

SEED_HEX = '3467f503105e1e54ae76ce585bac1defb356f9356cc986461f0c6781de5cf023dbf7cbb1dc75434e80740746bb963496b0200006fd71897c500a515029e9b9d3'
PUBLIC_KEY = 'BC1YLiN6G2ymqYrXwGSEcYwzWAXyTuUT1REkGgXwXf6Jrp49JXDKeT8'
deso_social = deso.Social(PUBLIC_KEY, SEED_HEX)
print(deso_social.submitPost("This is a test post"))
deso_posts = deso.Posts()
print(deso_posts.getHotFeed(taggedUsername="TESTACC").json())


# @app.get('/', response_class=HTMLResponse)
@app.get('/')
def root():
    posts = deso.Posts()
    hot_feed = posts.getHotFeed(taggedUsername="ItsAditya").json()
    return hot_feed

@app.get('/')
async def root():
    return RedirectResponse('/chain/root')

@app.get('/login', response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse(
        'login.html',
        {'request': request}
    )


@app.get('/user/{username}', response_class=HTMLResponse)
async def show_user(request: Request, username: str):
    user = deso.User()
    if username == 'me':
        credentials = await get_credentials(request)
        profile_info = user.getSingleProfile(publicKey=credentials.public_key).json()
    else:
        profile_info = user.getSingleProfile(username=username).json()
    if profile_info.get('error'):
        raise HTTPException(404)
    public_key = profile_info['Profile']['PublicKeyBase58Check']
    photo_url = user.getProfilePicURL(public_key)
    return templates.TemplateResponse(
        'profile.html',
        {
            'request': request,
            'name': profile_info['Profile']['Username'],
            'bio': profile_info['Profile']['Description'],
            'photo': photo_url,
        },
    )


# @app.get('/chain/{chain}', response_class=HTMLResponse)
# async def show_community(request: Request, chain: str):
#     # code to get posts from chain
#     return templates.TemplateResponse(
#         'chain.html',
#         {'request': request, 'chain_name': chain},
#     )


# @app.get('/post/new', response_class=HTMLResponse)
# async def new_post(request: Request, credentials: Credentials = Depends(get_credentials)):
#     return templates.TemplateResponse(
#         'new_post.html',
#         {'request': request},
#     )


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


@app.post('/api/auth')
async def api_auth(request: Request, credentials: Credentials):
    # TODO: do iteration over model instead
    request.session['public_key'] = credentials.public_key
    request.session['seed_hex'] = credentials.seed_hex
    request.session['access_level'] = credentials.access_level
    request.session['access_level_hmac'] = credentials.access_level_hmac


@app.post('/api/create_post')
async def api_create_post(post: Post, credentials: Credentials = Depends(get_credentials)):
    if credentials.public_key != post.public_key:
        raise HTTPException(401)
    post_db.put(post.dict(), post.id)
    return {'id': post.id}


@app.exception_handler(401)
async def unauthorized_handler(request: Request, exception):
    if '/api' not in request.url.path and request.method == 'GET':
        return RedirectResponse('/login')
    else:
        raise exception


@app.exception_handler(404)
async def not_found_handler(request: Request, exception):
    return templates.TemplateResponse(
        '404.html',
        {'request': request},
    )
