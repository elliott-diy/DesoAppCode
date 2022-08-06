import deso
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import models

app = FastAPI()
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


@app.get('/login', response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse(
        'login.html',
        {'request': request}
    )


@app.get('/user', response_class=HTMLResponse)
def user(request: Request, name: str):
    print(name)
    user = deso.User()
    profile_info = user.getSingleProfile(username=name).json()
    if not profile_info:
        return templates.TemplateResponse(
            '404.html',
            {'request': request}
        )
    print(profile_info['Profile'])
    return templates.TemplateResponse(
        'profile.html',
        {
            'request': request,
            'name': profile_info['Profile']['Username'],
            'bio': profile_info['Profile']['Description'],
            'photo': profile_info['Profile']['ExtraData']['HighQualityProfilePicUrl'],
        }
    )
