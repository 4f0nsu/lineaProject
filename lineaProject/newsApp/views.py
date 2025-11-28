# newsApp/views.py

import feedparser
from django.shortcuts import render
from django.core.paginator import Paginator
from sentence_transformers import SentenceTransformer, util

# --- Palavras-chave em inglês e português ---
keywords = [
    "art", "painting", "sculpture", "museum", "gallery", "exhibition",
    "installation", "drawing", "photography", "architecture", "design", "pritzker",
    "arte", "pintura", "escultura", "museu", "galeria", "exposição",
    "instalação", "desenho", "fotografia", "arquitetura", "design", "prémio pritzker",
    "poesia", "poetry", "literatura", "literature", "arquitetura", "arquiteto"
]

# --- Modelo multilingue ---
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
keywords_emb = model.encode(keywords, convert_to_tensor=True)

def news_relevance(texts):
    """
    Recebe um texto (string) ou lista de textos.
    Retorna um score ou lista de scores de relevância.
    """
    single_input = False
    if isinstance(texts, str):
        texts = [texts]
        single_input = True

    embs = model.encode(texts, convert_to_tensor=True)
    similarities = util.cos_sim(embs, keywords_emb).mean(dim=1)
    scores = similarities.cpu().tolist()
    return scores[0] if single_input else scores

# --- RSS FEEDS ---
RSS_FEEDS_INTERNATIONAL = {
    'the_archpaper': 'https://archpaper.com/feed/',
    'the_art_newspaper': 'https://www.theartnewspaper.com/rss.xml',
    'globalvoices': 'https://globalvoices.org/feeds/',
}

RSS_FEEDS_NATIONAL = {
    'rtp_noticias_cultura': 'https://www.rtp.pt/noticias/rss/feeds/Cultura',
    'observador': 'https://observador.pt/seccao/cultura/arte/feed',
    'cnn': 'https://cnnportugal.iol.pt/rss/arte',
}

# --- Classe NewsArticle ---
class NewsArticle:
    def __init__(self, source, title, link, summary=None, published=None,
                 published_parsed=None, score=0.0, is_national=False):
        self.source = source
        self.title = title
        self.link = link
        self.summary = summary
        self.published = published
        self.published_parsed = published_parsed
        self.score = score
        self.is_national = is_national

# --- Função para buscar artigos ---
def news_get_articles():
    articles = []

    # --- Internacionais ---
    for source, feed in RSS_FEEDS_INTERNATIONAL.items():
        parsed_feed = feedparser.parse(feed)
        for entry in parsed_feed.entries:
            article = NewsArticle(
                source=source,
                title=getattr(entry, 'title', 'No title'),
                link=getattr(entry, 'link', '#'),
                summary=getattr(entry, 'summary', ''),
                published=getattr(entry, 'published', ''),
                published_parsed=getattr(entry, 'published_parsed', None),
                is_national=False
            )
            articles.append(article)

    # --- Nacionais ---
    for source, feed in RSS_FEEDS_NATIONAL.items():
        parsed_feed = feedparser.parse(feed)
        for entry in parsed_feed.entries:
            article = NewsArticle(
                source=source,
                title=getattr(entry, 'title', 'No title'),
                link=getattr(entry, 'link', '#'),
                summary=getattr(entry, 'summary', ''),
                published=getattr(entry, 'published', ''),
                published_parsed=getattr(entry, 'published_parsed', None),
                is_national=True
            )
            articles.append(article)

    # --- Remover duplicados ---
    unique = {a.link: a for a in articles}
    articles = list(unique.values())

    # --- Calcular relevância ---
    texts = [f"{a.title} {a.summary}" for a in articles]
    scores = news_relevance(texts)
    for i, article in enumerate(articles):
        article.score = scores[i]

    # --- Ordenar por score e data ---
    articles = sorted(
        articles,
        key=lambda x: (x.score, x.published_parsed or x.published or ""),
        reverse=True
    )

    return articles

# --- View principal ---
def news_index(request):
    tab = request.GET.get('tab', 'all')
    articles = news_get_articles()

    if tab == "national":
        articles = [a for a in articles if a.is_national]
    elif tab == "international":
        articles = [a for a in articles if not a.is_national]

    page_number = request.GET.get('page', 1)
    paginator = Paginator(articles, 10)
    page_obj = paginator.get_page(page_number)

    return render(request, 'newsApp/index.html', {
        'articles': page_obj.object_list,
        'page_obj': page_obj,
        'tab': tab
    })

# --- View de pesquisa ---
def news_search(request):
    query = request.GET.get('q', '').lower()
    articles = news_get_articles()
    results = [a for a in articles if query in a.title.lower()]

    return render(request, 'newsApp/search_results.html', {
        'articles': results,
        'query': query
    })
