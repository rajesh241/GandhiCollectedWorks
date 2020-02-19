


def update_user(*args, **kwargs):
    print("I am in this function wow this is col")
    print(args)
    print(kwargs)
    user = kwargs.get('user', None)
    avatar_url = None
    name = None
    backend = kwargs.get('backend', None)
    response = kwargs.get("response", None)
    if "GoogleOAuth2" in str(backend):
        provider = 'google'
    elif "facebook" in str(backend):
        provider = 'facebook'
    else:
        provider = None
    print(provider)
    if provider == 'google':
        if response is not None:
            avatar_url = response.get("picture", None)
            name = response.get("name", None)
    elif provider == "facebook":
        ## Another way to get picture
        #if backend.__class__ == FacebookBackend:
           #url = "http://graph.facebook.com/%s/picture?type=large" % response['id']
        if response is not None:
            try:
                avatar_url = "http://graph.facebook.com/%s/picture?type=large" % response['id']
               # avatar_url = response.get("picture").get("data").get("url")
            except:
                avatar_url = None
            name = response.get("name", None)
    if user:
        if avatar_url:
            user.avatar_url = avatar_url
        if name:
            user.name = name
        user.provider = provider
        user.save()

