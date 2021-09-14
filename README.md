# *KESS - Keyword Extraction, Summary, and Sorting* 

Vorab einmal folgenden Command im Terminal ausführen: `pip install -r requirements.txt`.

Teil 1 und 2 sind vertauscht, da in Teil 1 eine Funktion ausgeführt wird, die in Teil 2 definiert wurde. Die Reihenfolge wurde so gewählt, wie es der Nachvollziehbarkeit am nützlichsten ist. 

# TEIL 2 | HTML auslesen und Texte extrahieren
```python
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
        print (text.text)
        y = y + " " + text.text.replace('&', 'UND')
    return y
```
<br/>


# TEIL 1 | Links aus JSON File (über API) extrahieren
Hier werden alle Unterseiten zum Suchbegriff „Prostata“ auf der Website des deutschen *Instituts für Qualität und Wirtschaftlichkeit im Gesundheitswesen* extrahiert. Der Zugriff auf die einzelnen Unterseiten erfolgt über die Programmierschnittstelle (API) des Instituts.   
Die Elemente werden nach HTML-Text (y), dem Link zur Unterseite ("link") und dem Publikationsdatum ("pub_date") durchsucht. Der Text wird in *WebCR2* extrahiert und die Daten jeweils in den Variablen *x, l* und *r* gespeichert.
```python
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
```

## Zwischenteil 2.1 | Ergebnisse als CSV speichern
```python
source1 = ['Source_name'] + list(np.full(len(l), 'IQWIG'))
HTMLlink = ['HTMLlink'] + l
pubdate1 = ['Pub_Datum'] + r
HTMLtext = ['HTML-Text'] + x
np.savetxt('HTMLtexts_Liste_IQWIG_link_nodate6.csv', [p for p in zip(source1, HTMLlink, pubdate1, HTMLtext)], delimiter='&', fmt='%s')
```
Excel-Import mit Delimiter '&'.
<br/>
<br/>

# TEIL 3 | PDF Links aus JSON File extrahieren
```python
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
    g = [] #PDF-Links
    b = [] #Pubdates/Daten der Veröffentlichung der PDFs
    for result in s["results"]:
        if "doc_file_type" in result:
            print()
            print()
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
```

## Zwischenteil 3.1 | Ergebnisse als CSV speichern
```python
        import numpy as np
        source = ['Source_name'] + list(np.full(len(g), 'IQWIG'))
        PDFlink = ['PDFlink'] + g
        pubdate = ['Pub_Datum'] + b
        np.savetxt('PDFlinks_Liste_5_IQWIG_pubdate.csv', [p for p 
        in zip(source, PDFlink, pubdate)], delimiter='&', fmt='%s')
    
    return g, b
g, b = webCR3("https://iqwig-search-api.e-spirit.cloud/v1/prepared_search/IQWIG_PS/execute?query=Prostata&page=1&rows=1000")
```
Excel-Import mit Delimiter '&'.
<br/>
<br/>

# Teil 4 | PDFs auslesen
```python
import requests
import csv 
import io

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
```

## Zwischenteil 4.1 | PDF-Download (nur einmal ausführen)
Hier sind drei Dinge zu beachten:  
1) Der Zielordner muss schon existieren d.h. vor der Ausführung angelegt werden. (Hier: *PDFfiles_IQWIG*)  
2) Dies kann 1-2 GB Speicher in Anspruch nehmen und ein paar Minuten dauern.
3) Der Zielordner und das Python-File, das hierfür ausgeführt wird, müssen im selben Ordner liegen.

```python
# PDFnr ausserhalb der Schleife initialisieren.
PDFnr = 1
for w in g:
    url = w
    response = requests.get(url)
    PDFnr = PDFnr + 1
    with open(f'./PDFfiles_IQWIG/IQWIG{PDFnr}.pdf', 'wb') as f:
        f.write(response.content)
```
<br/>

### Weiter mit: Extrahieren und auslesen
```python
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
    e = [] # Variable, in der der Text aus PDFs gespeichert wird.
    for PDFnr in range(18, 141): 
        p = ""
        for page in extract_text_by_page(pdf_path=f'./PDFfiles_IQWIG/IQWIG{PDFnr}.pdf'):
            p = p + page.replace('&', 'UND')
        e.append(p)
    return e
e = extract_text()
```

## Zwischenteil 4.2 | Ergebnisse als CSV speichern
```python
source = ['Source_name'] + list(np.full(len(g), 'IQWIG'))
PDFlink = ['PDFlink'] + g
pubdate = ['Pub_Datum'] + b
PDFtext = ['PDFtext'] + e

np.savetxt('PDFtexts_Liste_IQWIG_link_date6.csv', [p for p in zip(source, PDFlink, pubdate, PDFtext)], delimiter='&', fmt='%s')
```
Excel-Import mit Delimiter '&'. PDF-Texte in CSV unvollstaendig. Eine Vermutung ist, dass Excel die Texte in der Darstellung aus Performane-Gründen kürzt.


<br/>

# Teil 5 | Keyword Extraction, PDF und HTML

YAKE! im Terminal mit pip installieren:
pip install git+https://github.com/LIAAD/yake

```python
import yake
```

## Zwischenteil 5.1 | Eine „Blacklist“ importieren

Eine Blacklist kann jeder Nutzer selbst anlegen, um die Qualität der Ergebnisse aus der Keyword Extraction zu verbessern. Hierzu lohnt es sich, *YAKE!* erstmal ohne Blacklist über die zu analysierenden Texte laufen zu lassen und anschließend alle redundanten Worte in einer CSV-Datei zu speichern.

```python
s2 = set()
with open('BlacklistIQWIG.csv', "r", encoding = 'utf-8') as csvfile:
    blacklistreader = csv.reader(csvfile, delimiter=',')
    s2 = set([p [0] for p in blacklistreader])
```
### Weiter mit: Keyword Extraction für PDFs
```python
print("PDF-Keywords:")
h1 = [] # Hierin sind die bereinigten PDF-Keywords gespeichert
for text in e: 
    kw_extractor = yake.KeywordExtractor(lan="de", n=3, top=30, dedupFunc='jaro')
```
Die *dedupFunc* ist per Default auf *seqm* gesetzt. Hier wurde *jaro* verwendet, da sich die Qualität der Ergebnisse dadurch verbessert.\
Außerdem wurde *"top"*, also die Zahl der Keywords, die *YAKE!* zurückgibt, von 20 (Default) auf 30 erhöht. So bleiben nach den Abzügen durch die Blacklist immer noch genügend Resultate übrig.

```python
    keywords = kw_extractor.extract_keywords(text)
    for kw in keywords:
        print(kw)
```
<br/>

## Zwischenteil 5.2 | Inhalte der Blacklist mit Mengenoperation aus den PDF-Ergebnissen entfernen
```python
    print("Bereinigte Keywords PDF:")
    s1 = set([p [0] for p in keywords])
    s3 = s1 - s2
    print(s3)
    print()
    h1 = h1 + list(s3)
```
<br/>
Dasselbe nochmal für die HTML-Texte:

```python
print("HTML-Keywords:")
h2 = []
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
```
Für den Output, den *YAKE!* zurückgibt, gilt: *"The lower the score, the more relevant the keyword is."* (Quelle: https://github.com/LIAAD/yake/blob/master/README.md)\
<br/>

## Abschluss Teil 5 | Listen bereinigter Keywords fusionieren
Das dient der Vorbereitung von Schritt 6. 
```python
h3 = h1 + h2
```
<br/>

# Teil 6 | Keywords aufsummieren / squishen und Top 30 behalten

Aufbauend könnte eine *"Distance"* implementiert werden, um die Ergebnisse der Counts zu verbessern und stark ähnliche Worte als ein Wort zu zählen.
Auf diese Art ließe sich auch die Bereinigung der Ergebnisse durch die Blacklist noch verbessern.
Geeignet scheint dafür das Package *jellyfish*.

```python
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

# Die Top 30 Keywords für HTML- und PDF-Texte zusammen
print(h11[:30])
```
<br/>

# Teil 7 | Eine Zusammenfassung erstellen mit DeepAI (basierend auf GPT-2)
Die HTML-Texte können direkt als String an DeepAI gesendet werden.
```python
print("Zusammenfassungen der HTML-Texte:")
m = []
for text in x: 
    y = requests.post("https://api.deepai.org/api/summarization", data={'text': text}, headers={'api-key': '>>INSERT YOUR OWN API-KEY FROM DEEPAI.ORG<<'})
    m.append(y.json())
print(m)
summary = ['HTML_Summary'] + m
```
<br/>
Wer testweise erstmal ein paar Anfragen an die DeepAI-API schicken möchte, um das Verfahren zu testen, kann folgenden Key verwenden:

```python
# Quickstart API-Key:
...headers={'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'}
```

## Zwischenteil 7.1 | Ergebnisse als CSV speichern
```python
np.savetxt('HTMLtexts_summary_link_pubdate_IQWIG2_delimiterUND.csv', [p for p in zip(source1, HTMLlink, pubdate1, HTMLtext, summary)], delimiter='&', fmt='%s')

# Problem: Das CSV sieht an einigen Stellen kaputt aus. 
```
Excel-Import mit Delimiter '&'.
<br/>

# Teil 8 | Resultate zu PDF- und HTML-Texten chronologisch ordnen
*Datetime* im Terminal mit pip installieren:\
pip install datetime
```python
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
```
## Zwischenteil 8.1 | Tupel erstellen aus: 
### Link, Date, Source_Name, Keywords – Zusatz bei HTML-Texten: Text, Summary

```python
OverallTupelHTML = zip(source1, HTMLlink, pubdate1, h2, HTMLtext, summary)
OverallTupelPDF = zip(source, PDFlink, pubdate, h1) 
# Bei PDFs: Text nicht gespeichert, da zu lang. Kein Summary, da im PDF enthalten.
```

### Weiter mit: HTMLs chronologisch ordnen
```python
print("HTMLs chronologisch ordnen:")
def unpackHTMLtuple(TupelDate):
    return TupelDate[2]                                                                 
sr = sorted(OverallTupelHTML, key = unpackHTMLtuple, reverse = False)                   
print(sr)                                                                               
print() 

print("PDFs chronologisch ordnen:")
def unpackPDFtuple(TupelDate):
    return TupelDate[2] 
sb = sorted(OverallTupelPDF, key = unpackPDFtuple, reverse = False)
print(sb)
# Problem: Pro Ausgangstext steht in der CSV-Liste nur ein einziges YAKE!-Keyword
```
## Endteil 8.2 | Sortierte Ergebnisse als CSV speichern:
```python
np.savetxt('PDF_allAtributes_DateSorted_IQWIG.csv', sb, delimiter='&', fmt='%s')
np.savetxt('HTML_allAtributes_DateSorted_IQWIG.csv', sr, delimiter='&', fmt='%s')
```
Excel-Import mit Delimiter '&'.
<br/>
<br/>

# Ende
### In der UI werden PDF- und HTML-Inhalte in einen Kontext gebracht.
<br/>