# TEIL 2 | HTML auslesen und Texte extrahieren
import requests
import numpy as np
from bs4 import BeautifulSoup
def webCR2(WebUrl):
    y = ""
    url = WebUrl
    code = requests.get(url)
    plain = code.text
    s = BeautifulSoup(plain, "html.parser")
    for text in s.findAll("p", {"class":"ta--left"}):
        print (text.text) #Das ist optional und dient der Kontrolle
        y = y + " " + text.text.replace('&', 'UND')
    return y



# TEIL 1 | Links aus JSON File (ueber API) extrahieren
import requests
import json
def webCR1(WebUrl):
    x = [] #HTML-Texte
    l = [] #HTML-Links
    r = [] #Pubdates/Daten der Veröffentlichung
    url = WebUrl
    code = requests.get(url)
    plain = code.text
    s = json.loads(plain)
    print("Zahl der HTML-Ergebnisse:", len(s["results"])) 
    for link in s["results"]: 
        if link["link"][0] != "/":
            print(link["link"])
            y = webCR2(link["link"])
            x.append(y)
            l.append(link["link"])
            r.append(link["pub_date"]) 
    return x, l, r
x, l, r = webCR1("https://iqwig-search-api.e-spirit.cloud/v1/prepared_search/IQWIG_PS/execute?query=Prostata&page=1&rows=1000")

# Zwischenteil 2.1 | Ergebnisse als CSV speichern
source1 = ['Source_name'] + list(np.full(len(l), 'IQWIG'))
HTMLlink = ['HTMLlink'] + l
pubdate1 = ['Pub_Datum'] + r
HTMLtext = ['HTML-Text'] + x
np.savetxt('HTMLtexts_Liste_IQWIG_link_nodate6.csv', [p for p in zip(source1, HTMLlink, pubdate1, HTMLtext)], delimiter=',', fmt='%s')



# TEIL 3 | PDF Links aus JSON File extrahieren
import requests
import json
def webCR3(WebUrl):
    url = WebUrl
    code = requests.get(url)
    plain = code.text
    s = json.loads(plain)
    print(len(s["results"]))
    for result in s["results"]:
        print(result["link"])
    g = [] # PDF-Links
    b = [] # Pubdates/Daten der Veröffentlichung der PDFs
    for result in s["results"]:
        if "doc_file_type" in result:
            d = result["doc_file_type"]
            if "PDF" in d:
                print(result["link"])
                print()  
                if "pub_date" in result: 
                    print(result["pub_date"])
                    b.append(result["pub_date"])
                else:
                    print("no date")
                    b.append("no date")
                e = 'https://www.iqwig.de' 
                if result["link"][0] == '/':
                    f = e + result["link"]
                    print("Vollstaendiger PDF-Link:")
                    print(f)
                else:
                    print(result["link"])
                    f = result["link"]
                g.append(f)

    # Zwischenteil 3.1 | Ergebnisse als CSV speichern:
    import numpy as np
    source = ['Source_name'] + list(np.full(len(g), 'IQWIG'))
    PDFlink = ['PDFlink'] + g
    pubdate = ['Pub_Datum'] + b
    np.savetxt('PDFlinks_Liste_5_IQWIG_pubdate.csv', [p for p in zip(source, PDFlink, pubdate)], delimiter=',', fmt='%s')
    return g, b
g, b = webCR3("https://iqwig-search-api.e-spirit.cloud/v1/prepared_search/IQWIG_PS/execute?query=Prostata&page=1&rows=1000")



# TEIL 4 | PDFs auslesen
import requests
import csv 
import io

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage


# Zwischenteil 4.1 | PDF-Download (nur einmal ausfuehren)
# PDFnr ausserhalb der Schleife initialisieren.
PDFnr = 1
for w in g:
    url = w
    response = requests.get(url)
    PDFnr = PDFnr + 1
    with open(f'./PDFfiles_IQWIG/IQWIG{PDFnr}.pdf', 'wb') as f:
        f.write(response.content)

# PDF-Texte extrahieren und auslesen, CSV erstellen
def extract_text_by_page(pdf_path):
    try:
        with open(pdf_path, 'rb') as fh:
            for page in PDFPage.get_pages(fh, caching=True,check_extractable=True):
                resource_manager = PDFResourceManager()
                fake_file_handle = io.StringIO()
                converter = TextConverter(resource_manager, fake_file_handle)
                page_interpreter = PDFPageInterpreter(resource_manager, converter)
                page_interpreter.process_page(page)
    
                text = fake_file_handle.getvalue()
                yield text
    
                converter.close()
                fake_file_handle.close()
    except:
        print("no PDF")
        return['no PDF']

def extract_text():
    e = [] # PDF-Texte
    for PDFnr in range(18, 141):  
        p = ""
        for page in extract_text_by_page(pdf_path=f'./PDFfiles_IQWIG/IQWIG{PDFnr}.pdf'):
            p = p + page.replace('&', 'UND')
        e.append(p)
    return e
e = extract_text()

# Zwischenteil 4.2 | Ergebnisse als CSV speichern
source = ['Source_name'] + list(np.full(len(g), 'IQWIG'))
PDFlink = ['PDFlink'] + g
pubdate = ['Pub_Datum'] + b
PDFtext = ['PDFtext'] + e
np.savetxt('PDFtexts_Liste_IQWIG_link_date6.csv', [p for p in zip(source, PDFlink, pubdate, PDFtext)], delimiter='&', fmt='%s')



# TEIL 5 | Keyword Extraction, PDF und HTML
import yake

# Zwischenteil 5.1 | Eine „Blacklist“ importieren
s2 = set()
with open('BlacklistIQWIG.csv', "r", encoding = 'utf-8') as csvfile:
    blacklistreader = csv.reader(csvfile, delimiter=',')
    s2 = set([p [0] for p in blacklistreader])

# Keyword Extraction für PDFs
print("PDF-Keywords:")
h1 = [] # Liste bereinigter PDF-Keywords
for text in e: 
    kw_extractor = yake.KeywordExtractor(lan="de", n=3, top=30, dedupFunc='jaro')
    keywords = kw_extractor.extract_keywords(text)
    for kw in keywords:
        print(kw)

    # Zwischenteil 5.2 | Inhalte der Blacklist mit Mengenoperation aus den PDF-Ergebnissen entfernen    
    print("Bereinigte Keywords PDF:")
    s1 = set([p [0] for p in keywords])
    s3 = s1 - s2
    print(s3)
    print()
    h1 = h1 + list(s3)

# Keyword Extraction und Bereinigung für HTML
print("HTML-Keywords:")
h2 = [] # Liste bereinigter HTML-Keywords
for text in x: 
    kw_extractor = yake.KeywordExtractor(lan="de", n=3, top=30, dedupFunc='jaro')
    keywords = kw_extractor.extract_keywords(text)
    for kw in keywords:
        print(kw)
    print()
    
    print("Bereinigte Keywords HTML:")
    s4 = set([p [0] for p in keywords])
    s5 = s4 - s2
    print(s5)
    print()
    h2 = h2 + list(s5)

# Abschluss Teil 5 | Listen bereinigter Keywords fusionieren
h3 = h1 + h2



# TEIL 6 | Keywords aufsummieren / squishen und Top-Ten behalten

print("Textübergreifend wichtigste Keywords im IQWIG-Datenset:")
# Zählen
h4 = []
for kwRank in h3:
    o = h3.count(kwRank)
    h4.append((kwRank, o)) 
print(h4)

# Sortieren
def sortKw(TupelKw):
    return TupelKw[1]
h5 = sorted(h4, key = sortKw, reverse = True) 
print(h5)

# alle Ergebisse >10 Positionen entfernen
h6 = h5[:10] 
print(h6)

# Dubletten entfernen mit Mengenoperation
print("Dubletten entfernen")
print("Variante set():")       
h9 = set(h5)
h10 = list(h9)

# Sortieren 
def sortKw1(TupelKw):
    return TupelKw[1]
h11 = sorted(h10, key = sortKw1, reverse = True) 
print(h11) 
print()
print()

# Die Top 30 Keywords für HTML- und PDF-Texte zusammen
print(h11[:30])



# TEIL 7 | Creating a summary with DeepAI, based on GPT-2
import os
print("Zusammenfassungen HTML-Texte:")
m = []
for text in x: 
    y = requests.post("https://api.deepai.org/api/summarization", data={'text': text}, headers={'api-key': os.environ.get("DEEPAI_KEY")})
    m.append(y.json())
print(m)
summary = ['HTML_Summary'] + m

"""
# Quickstart API-Key für alle, die DeepAI erstmal testen wollen:
...headers={'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'}
"""

# Zwischenteil 7.1 | Ergebnisse als CSV speichern
np.savetxt('HTMLtexts_summary_link_pubdate_IQWIG2_delimiterUND.csv', [p for p in zip(source1, HTMLlink, pubdate1, HTMLtext, summary)], delimiter='&', fmt='%s')
# Problem: Das CSV sieht an einigen Stellen kaputt aus.



# TEIL 8 | Beobachtungen chronologisch ordnen

from datetime import*

print("HTML Dates:")
for datum in r:
    z1 = datetime.fromisoformat(datum)
    print(z1)
print()

print("PDF Dates:")
for datum in b:
    try:
        z2 = datetime.fromisoformat(datum)
        print(z2)
    except:
        print("no date")

# Zwischenteil 8.1 | Tupel erstellen aus: Link, Date, SourceName, Keywords – Zusatz HTML: Text, Summary.
OverallTupelHTML = zip(source1, HTMLlink, pubdate1, h2, HTMLtext, summary)
OverallTupelPDF = zip(source, PDFlink, pubdate, h1) 

# HTMLs chronologisch ordnen
print("HTMLs chronologisch ordnen:")
def unpackHTMLtuple(TupelDate):
    return TupelDate[2]                                                                 # F: Bezieht sich eine Funktion wie unpackHTMLtuple immer auf die vorangegangene Liste? 
sr = sorted(OverallTupelHTML, key = unpackHTMLtuple, reverse = False)                   # A: Nein. Die Funktion unpackHTMLtuple wird dort nur definiert. Ausgefuehrt wird sie erst innerhalb sorted() und dieser Funktion uebergibt man die Liste.
print(sr)                                                                               # F: Weshalb steht in jedem Element der Liste nur ein einziges Keyword? 
print()

# PDFs chronologisch ordnen
print("PDFs chronologisch ordnen:")
def unpackPDFtuple(TupelDate):
    return TupelDate[2] 
sb = sorted(OverallTupelPDF, key = unpackPDFtuple, reverse = False)
print(sb)

# Endteil 8.2 | Sortierte Endergebisse als CSV speichern
np.savetxt('HTML_allAtributes_DateSorted_IQWIG.csv', sr, delimiter='&', fmt='%s')  
np.savetxt('PDF_allAtributes_DateSorted_IQWIG.csv', sb, delimiter='&', fmt='%s')
