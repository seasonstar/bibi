# -*- coding: utf-8 -*-

SOCIALOAUTH_SITES = (
    ('wechat', 'socialoauth.sites.wechat.Wechat', '微信',
        {
          'redirect_uri': 'http://m.maybi.cn/account/oauth/wechat',
          'client_id': '',
          'client_secret': '',
          'scope': 'snsapi_userinfo'
        }
    ),
    ('wechat_app', 'socialoauth.sites.wechat_app.WechatApp', '微信客户端',
        {
          'redirect_uri': 'http://m.maybi.cn/account/oauth/wechat',
          'client_id': '',
          'client_secret': '',
          'scope': 'snsapi_userinfo'
        }
    ),
    ('weibo', 'socialoauth.sites.weibo.Weibo', '新浪微博',
        {
          'redirect_uri': 'http://m.maybi.cn/account/oauth/weibo',
          'client_id': '',
          'client_secret': '',
        }
    ),
    ('weibo_app', 'socialoauth.sites.weibo_app.WeiboApp', '新浪微博客户端',
        {
          'redirect_uri': 'http://m.maybi.cn/account/oauth/weibo',
          'client_id': '',
          'client_secret': '',
        }
    ),
    ('qq', 'socialoauth.sites.qq.QQ', 'QQ',
        {
          'redirect_uri': 'http://m.maybi.cn/account/oauth/qq',
          'client_id': '',
          'client_secret': '',
        }
    ),
    ('qq_app', 'socialoauth.sites.qq_app.QQApp', 'QQ客户端',
        {
          'redirect_uri': 'http://m.maybi.cn/account/oauth/qq',
          'client_id': '',
          'client_secret': '',
        }
    ),
    ('facebook', 'socialoauth.sites.facebook.Facebook', 'Facebook',
        {
          'redirect_uri': 'http://m.maybi.cn/account/oauth/facebook',
          'client_id': '',
          'client_secret': '',
        }
    ),
    ('facebook_app', 'socialoauth.sites.facebook_app.FacebookApp', 'Facebook客户端',
        {
          'redirect_uri': 'http://m.maybi.cn/account/oauth/facebook',
          'client_id': '',
          'client_secret': '',
        }
    ),
)


AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

OPENEXCHANGERATES_APPID = ""

FOURPX_TOKEN = ""

BING_APPID = ''
BING_APPSECRET = '='


GOOGLE_APIKEY = ""
