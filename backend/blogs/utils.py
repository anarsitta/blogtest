from django.db import models
from django.core.paginator import Paginator


def filter_visible_blogs(blogs, user):
    """
    Фильтрация блогов по видимости для пользователя
    Учитывает взаимные черные списки:
    - Если пользователь в черном списке автора ИЛИ
    - Если автор в черном списке пользователя
    то блог не отображается
    """
    visible_blogs = []
    for blog in blogs:
        author = blog.author
        
        user_in_author_blacklist = hasattr(author, 'blacklist') and user in author.blacklist.all()
        author_in_user_blacklist = hasattr(user, 'blacklist') and author in user.blacklist.all()
        
        if user_in_author_blacklist or author_in_user_blacklist:
            continue
            
        if blog.is_private:
            if user == author or (hasattr(author, 'whitelist') and user in author.whitelist.all()):
                visible_blogs.append(blog)
                
        else:
            visible_blogs.append(blog)
    return visible_blogs

def paginate_blogs(blogs, page_number, per_page=20):
    paginator = Paginator(blogs, per_page)
    page = paginator.get_page(page_number)
    return page, paginator
