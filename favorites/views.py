from django.views.generic.list_detail import object_list, object_detail
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from models import Favorite
from forms import DeleteFavoriteForm


@login_required
def create_favorite(request, object_id, queryset, redirect_to=None,
        template_name=None, extra_context=None):
    """
    Generic `add to favorites` view

    `queryset` - required for content object retrieving
    `redirect_to` is set to `favorites` by default - change it if needed

    Raises Http404 if content object does not exist.

    Example of usage (urls.py):
        url(r'favorites/add/(?P<object_id>\d+)/$', 
            'favorites.views.create_favorite', kwargs={
                'queryset': MyModel.objects.all(),
            }, name='add-to-favorites')
        
    """
    obj = get_object_or_404(queryset, pk=object_id)
    content_type=ContentType.objects.get_for_model(obj)

    if Favorite.objects.filter(content_type=content_type, object_id=object_id,\
                              user=request.user):
        return redirect(redirect_to or 'favorites')

    favorite = Favorite.objects.create_favorite(obj, request.user)
    return redirect(redirect_to or 'favorites')


@login_required
def favorite_list(request, model_class, **kwargs):
    """
    Generic `favorites list` view based on generic object_list

    `model_class` - required valid model class
    `template_name` - default is "favorites/favorite_list.html"
                      used by generic object_list view

    Other parameters are same as object_list.

    Example of usage (urls.py):
        url(r'favorites/my_model/$', 
            'favorites.views.favorite_list', kwargs={
                'template_name': 'favorites/mymodel_list.html',
                'model_class': get_model('my_app.MyModel'),
                'paginate_by': 25,
            }, name='favorites-mymodel')
    """
    queryset = kwargs.get('queryset',Favorite.objects.favorites_for_model(
        model_class, request.user))
    return object_list(request, queryset, **kwargs)


@login_required
def delete_favorite(request, object_id, form_class=None, redirect_to=None,
           template_name=None, extra_context=None):
    """
    Generic Favorite object delete view

    GET: displays question to delete favorite
    POST: deletes favorite object and returns to `redirect_to`

    Default context:
        `form` - delete form

    `object_id` - required object_id (favorite pk)
    `template_name` - default "favorites/favorite_delete.html"
    `form_class` - default DeleteFavoriteForm
    `redirect_to` - default set to "favorites", change it if needed
    `extra_context` - provide extra context if needed
    """

    favorite = get_object_or_404(Favorite, pk=object_id, user=request.user)
    form_class = form_class or DeleteFavoriteForm

    if request.method == 'POST':
        form = form_class(instance=favorite, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(redirect_to or 'favorites')
    else:
        form = form_class(instance=favorite)
    ctx = extra_context or {}
    ctx.update({
        'form': form,
    })

    return render_to_response(template_name or 'favorites/favorite_delete.html',
            RequestContext(request, ctx))

