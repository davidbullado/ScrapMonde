import unittest
import scrap

class TestScrap(unittest.TestCase):

    def check_article(self, articleType, url):
        article = scrap.scrap_article(url)
        self.assertEqual(articleType,article['articleType'])
        self.assertGreater(len(article['headline']), 0)
        self.assertGreater(len(article['description']), 0)
        self.assertRegex(article['image']['url'], r"http(s)?://.*[.][a-z]{3,4}")
        self.assertRegex(article['dateCreated'], r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\+[0-9]{4})?")
        self.assertGreater(len(article['body']),0)
        #self.assertNotRegex(article['body'],article['headline'])
        self.assertNotRegex(article['body'],article['image']['url'])

    #def test_afr(self):
    #    self.check_article("afrique",'https://www.lemonde.fr/afrique/article/2018/10/05/comment-l-eswatini-a-mis-sous-controle-la-double-epidemie-sida-tuberculose_5365419_3212.html')
    def test_article(self):
        urllist = ['https://www.lemonde.fr/europe/article/2018/10/07/meurtre-d-une-journaliste-en-bulgarie_5366029_3214.html']
        map(lambda url: self.check_article('article', url), urllist)
        self.check_article("article",'https://www.lemonde.fr/europe/article/2018/09/29/moscou-diffuse-une-nouvelle-photo-du-cineaste-en-greve-de-la-faim-oleg-sentsov_5362172_3214.html')
        self.check_article("article",'https://www.lemonde.fr/afrique/article/2018/10/05/comment-l-eswatini-a-mis-sous-controle-la-double-epidemie-sida-tuberculose_5365419_3212.html')
    def test_blog(self):
        self.check_article("blog",'http://sosconso.blog.lemonde.fr/2018/10/05/la-testatrice-etait-elle-atteinte-de-la-maladie-dalzheimer/')
    def test_longformat(self):
        self.check_article("grandformat","https://www.lemonde.fr/long-format/article/2018/10/07/l-inde-et-ses-villes-mirages_5365988_5345421.html")
    def test_reportage(self):
        self.check_article("reportage", "https://www.lemonde.fr/economie/portfolio/2018/10/07/inde-comment-le-projet-urbain-de-lavasa-a-vire-au-cauchemar_5365974_3234.html")
    #def test_live(self):
    #    self.check_article("live", "https://www.lemonde.fr/ligue-1/live/2018/10/07/ligue-1-suivez-psg-lyon-en-direct_5366017_1616940.html")
        
if __name__ == '__main__':
    unittest.main()