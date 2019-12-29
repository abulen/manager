from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.html import escape, format_html
from django.utils.safestring import SafeData, mark_safe
import re

register = template.Library()


@register.filter
def classname(obj):
    return obj.__class__.__name__


@register.simple_tag
def optional_login(request):
    """
    Include a login snippet if REST framework's login view is in the URLconf.
    """
    try:
        login_url = reverse('rest_framework:login')
    except NoReverseMatch:
        return ''

#   snippet = "<li><a href='{href}?next={next}'>Log in</a></li>"
    snippet = '<button class="btn btn-primary"><a href="{href}?next={next}">Log in</a></button>'
    snippet = format_html(snippet, href=login_url, next=escape(request.path))

    return mark_safe(snippet)


@register.simple_tag
def optional_logout(request, user):
    """
    Include a logout snippet if REST framework's logout view is in the URLconf.
    """
    try:
        logout_url = reverse('rest_framework:logout')
    except NoReverseMatch:
        snippet = format_html(
            '<button class="btn btn-primary"><a href="#">{user}</a></button>',
            user=escape(user))
        return mark_safe(snippet)

    snippet = """<div class="dropdown">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">
              {user}
                </button>
                <div class="dropdown-menu">
                    <a class="dropdown-item" href="{href}?next={next}">Logout</a>
                </div>
            </div>"""

    # snippet = """<li class="dropdown">
    #     <a href="#" class="dropdown-toggle" data-toggle="dropdown">
    #         {user}
    #         <b class="caret"></b>
    #     </a>
    #     <ul class="dropdown-menu">
    #         <li><a href='{href}?next={next}'>Log out</a></li>
    #     </ul>
    # </li>"""
    snippet = format_html(snippet, user=escape(user), href=logout_url, next=escape(request.path))

    return mark_safe(snippet)


@register.filter
def breadcrumbs(url):
    home = ['<li> <a href="/" title="Breadcrumb link to the homepage.">home</a> &raquo;</li>',]
    links = url.strip('/').split('/')
    bread = []
    total = len(links)-1
    for i, link in enumerate(links):
        if len(link) > 0 and link[0] == '?':
            break
        if not link == '':
            bread.append(link)
            this_url = "/".join(bread)
            sub_link = re.sub('-', ' ', link)
            if not i == total and not links[i+1][0] == '?':
                tlink = '<li>&nbsp;<a href="/%s/" title="Breadcrumb link to %s">%s</a> &raquo; </li>' % (this_url, sub_link, sub_link)
            else:
                tlink = '<li>&nbsp;%s</li>' % sub_link
            home.append(tlink)
    bcrumb = "".join(home)
    return mark_safe(bcrumb)