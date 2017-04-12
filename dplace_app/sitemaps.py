from django.core.urlresolvers import reverse
from django.contrib.sitemaps import Sitemap
from dplace_app.models import Society, Language


class SocietySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Society.objects.all()


# TODO Should we provide this? If so, what kind of URLs should be generated?
# class LanguageSitemap(Sitemap):
#     changefreq = "weekly"
#     priority = 0.5
#
#     def items(self):
#         return Language.objects.all()


class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        return ['home', 'about', 'howto', 'howtocite', 
                'source', 'team', 'publication']

    def location(self, item):
        return reverse(item)


SITEMAP = {
    'society': SocietySitemap(),
    # 'language': LanguageSitemap(),
    'static': StaticViewSitemap(),
}
