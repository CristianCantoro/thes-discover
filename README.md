thes-discover
=============

(English)
Script using [Dandelion API](https://dandelion.eu/) by
[Spaziodati](http://spaziodati.eu/) to link terms in the 
[Italian Thesarus](http://thes.bncf.firenze.sbn.it/) of the 
[Central National Library of Florence](http://www.bncf.firenze.sbn.it/)
to [Italian Wikipedia](http://it.wikipedia.org)

(Italian)
Script che usa le [API Dandelion](https://dandelion.eu/) di
[Spaziodati](http://spaziodati.eu/) per linkare i termini del
[Thesaruso del Nuovo Soggettario](http://thes.bncf.firenze.sbn.it/) della
[Biblioteca Nazionale Centrale di Firenze](http://www.bncf.firenze.sbn.it/)
a [Wikipedia in lingua italiana](http://it.wikipedia.org)

Il file contenenti le annotazioni (`.map`) sono stati applicati a:
* NS-SKOS-Agenti-Organismi.xml
* NS-SKOS-Agenti-Organizzazioni.xml
* NS-SKOS-Agenti-Persone-Gruppi.xml
* NS-SKOS-Azioni-Attivita.xml
* NS-SKOS-Azioni-Discipline.xml
* NS-SKOS-Azioni-Processi.xml
* NS-SKOS-Cose-Forme.xml
* NS-SKOS-Cose-Materia.xml
* NS-SKOS-Cose-Oggetti.xml
* NS-SKOS-Cose-Spazio.xml
* NS-SKOS-Cose-Strumenti.xml
* NS-SKOS-Cose-Strutture.xml
* NS-SKOS-Tempo.xml
* NS-Thes.xml

Installazione
-------------
È possibile installare tutti i pacchetti necessari tramite pip.

```
(sudo) pip install -r requirements.txt
```

`sudo` è necessario qualora si vogliano installare i pacchetti in modo globale
in tutto il sistema. È consigliabile comunque utilizzare un _virtualenv_.

Comandi utili
-------------

Riunire tutti i risultati in un unico file:
```bash
cat new_annotations-* > new_annotations_all.map
cat different_annotations-* > different_annotations_all.map
```

Per ordinare i risultati per termine (THES) e quindi per punteggio:
```bash
sort --field-separator=',' --key=2,4 annotations.map > sorted_annotations.map
```

Grafico
-------
Nella cartella `utils` il file `graph.py` permette di reallizzare un grafico
interattivo che mostra le varie associazioni con i punteggi.

Si può lanciare, ad esempio con il comando:
```bash
:thes-discover/utils$ python graph.py ../new_annotations.map 
````