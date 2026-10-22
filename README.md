# SiteCloner

Clona un sito web per usarlo **offline** e, se vuoi, **modificarlo in locale con un editor visivo**.

Il progetto ha due parti:

1. **Cloner** (`sitecloner`): scarica HTML, CSS, JS, immagini, font, video e documenti, e riscrive i link perché tutto funzioni dal tuo PC.
2. **Editor visivo** (opzionale): una barra degli strumenti iniettata in ogni pagina, più un piccolo server locale che salva le modifiche su disco. Si seleziona un elemento nella pagina e lo si modifica dall'interfaccia, senza toccare il codice.

> **Uso responsabile.** Clona solo siti tuoi o per i quali hai il permesso. Rispetta copyright, condizioni d'uso e `robots.txt` (usa `--respect-robots`), e tieni un carico basso (`--rate`, pochi `--workers`). L'autore non è responsabile dell'uso che ne fai.

---

## Indice

- [Requisiti e installazione](#requisiti-e-installazione)
- [Avvio rapido](#avvio-rapido)
- [Clonare un sito](#clonare-un-sito)
- [Editor visivo](#editor-visivo)
- [Opzioni da riga di comando](#opzioni-da-riga-di-comando)
- [Uso come libreria](#uso-come-libreria)
- [Struttura dei file prodotti](#struttura-dei-file-prodotti)
- [Limiti noti](#limiti-noti)
- [Risoluzione dei problemi](#risoluzione-dei-problemi)
- [Sviluppo e test](#sviluppo-e-test)
- [Struttura del progetto](#struttura-del-progetto)
- [Licenza](#licenza)

---

## Requisiti e installazione

- **Python 3.9 o superiore** (provato su 3.11 e 3.12; Windows è la piattaforma di sviluppo, il codice è multipiattaforma).
- **Node.js** (facoltativo): serve solo all'editor per controllare la sintassi degli script `.js` prima di salvarli. Senza Node il salvataggio degli script resta bloccato finché non lo installi (o scegli tu di salvare senza verifica).
- Un browser moderno (Chrome, Edge, Firefox).

```bash
git clone https://github.com/Huawetto/sitecloner.git
cd sitecloner
pip install -r requirements.txt
```

Dipendenze (`requirements.txt`): `requests` e `beautifulsoup4` sono necessarie; `lxml` (parser più veloce), `colorama` (colori su Windows) e `brotli` (decodifica le risposte Brotli, che molti siti usano) sono consigliate ma facoltative.

In alternativa, come pacchetto con comando `sitecloner`:

```bash
pip install .            # solo le dipendenze necessarie
pip install ".[full]"    # con lxml, colorama e brotli
```

> Su Windows il lanciatore consigliato è `py` (negli esempi sotto puoi sostituire `python` con `py`).

---

## Avvio rapido

```bash
python crawl.py                       # modalità guidata: ti chiede URL, cartella, profondità, worker, toolbar
python crawl.py https://example.com   # direttamente da riga di comando
```

Alla fine del clone, se hai scelto la toolbar, puoi avviare subito il server di editing.

---

## Clonare un sito

```bash
# clone semplice, profondità 3 (default)
python crawl.py https://example.com

# cartella di output, profondità 5, 32 worker
python crawl.py https://example.com -o ./mirror -d 5 -w 32

# gentile con siti lenti o che limitano le richieste
python crawl.py https://example.com -w 3 --rate 1 --timeout 60

# al massimo 50 pagine HTML, rispettando robots.txt
python crawl.py https://example.com --max-pages 50 --respect-robots

# senza video/font e senza risorse da CDN esterne
python crawl.py https://example.com --no-media --no-fonts --no-external-assets

# escludere percorsi
python crawl.py https://example.com --ignore "/admin" --ignore "?print=1"
```

Il clone si apre anche **senza server**, con doppio click su `<cartella>/<dominio>/index.html`: i link sono riscritti in percorsi relativi. (Per modificare e salvare serve invece il server di editing, vedi sotto.)

### Cosa fa il cloner

- **Estrazione completa** da `<a>`, `<link>`, `<script>`, `<img>`, `srcset`, `<source>`, `<video>`, `<audio>`, `<iframe>`, `<form>`, SVG `<use>`, meta `og:image`, attributi lazy-load (`data-src`, ...), `url()` e `@import` nei CSS, stili inline.
- **Riscrittura dei link** in percorsi relativi. Le pagine non scaricate (fuori profondità, errori...) diventano URL assoluti, così non si rompono mai in percorsi inesistenti.
- **Redirect risolti**: un link che punta a un URL con redirect viene collegato alla pagina finale scaricata.
- **Concorrenza** con coda a priorità (HTML, poi CSS, poi asset), retry con backoff, rate-limit per dominio, circuit breaker che mette in pausa i worker quando il sito va in difficoltà invece di scartare i file.
- **Protezioni**: le pagine di login vengono escluse (non possono funzionare offline); gli endpoint tecnici dei CMS (`wp-json`, `xmlrpc.php`, oEmbed, feed, `wp-admin`) vengono ignorati; i file binari spacciati per pagine HTML non vengono mai passati al parser.
- **Deduplica** dei contenuti per hash, gestione di nomi riservati Windows e percorsi troppo lunghi, query string trasformate in suffissi.
- **Metadati**: email, telefoni e link social trovati nelle pagine vengono salvati in file di testo a parte (disattivabile con `--no-metadata`).
- **Avanzamento** stampato ogni 10 secondi, per capire se il sito risponde lentamente.

---

## Editor visivo

### Avvio

Dopo aver clonato con la toolbar (risposta `1` alla domanda, oppure `--editor-toolbar`):

```bash
cd <cartella-del-clone>
python /percorso/di/crawl.py --serve
```

Si apre un server **solo locale** (`http://127.0.0.1:8000`, o la prima porta libera successiva). Apri le pagine da quell'indirizzo, non con doppio click: solo così l'editor può salvare, verificare gli script e caricare file.

Hai già un clone senza toolbar? Non serve riscaricarlo:

```bash
python crawl.py --serve --add-toolbar       # la aggiunge a tutte le pagine (idempotente) e avvia il server
python crawl.py --serve --remove-toolbar    # la toglie
```

Ad ogni avvio il server aggiorna anche le copie di `toolbar.js` presenti nel clone all'ultima versione.

### Come si usa

1. Premi **Modifica: ON**. Il sito smette di reagire ai click normali.
2. **Clicca un elemento** per selezionarlo: a destra compaiono gli strumenti adatti. Doppio click su un testo per scriverci.
3. **Ctrl+S** (o "Salva su disco") scrive la pagina nel suo file `.html`, creando prima un backup.

Scorciatoie: `Ctrl+Z`/`Ctrl+Y` annulla/ripeti, `Ctrl+C`/`X`/`V`/`D` copia/taglia/incolla/duplica l'elemento selezionato, `Canc` elimina, frecce spostano di 1 px (Maiusc = 10 px), `Esc` deseleziona.

### Schede

| Scheda | Cosa permette |
|---|---|
| **Elemento** | **Immagini**: sostituzione con un file del PC (anche immagini di sfondo CSS e immagini dentro link/slider), tinta unita o gradient, Paint integrato (penna, gomma, forme, secchiello, contagocce, testo, rotazione, specchio), filtri. **Testo**: colore, gradient a più colori, outline (anche gradient), font (anche caricandone uno), stili, ombra, effetti animati. **Video/audio**: sostituzione, eliminazione, velocità predefinita. **Sfondo**: colore, gradient, immagine, luminosità/contrasto, animazioni, marquee. Posizione, dimensione, rotazione, specchio, contorno, angoli. |
| **Inserisci** | Nuovi elementi (titoli, paragrafi, link, elenchi, citazioni, linee, contenitori, colonne, tabelle, iframe, immagini/video/audio dal PC, HTML libero), copia/incolla anche **tra pagine diverse**, e il **costruttore di bottoni**: apre una pagina del sito (scelta da un elenco), un link esterno, un popup con titolo/testo/bottoni propri o un avviso, con colori, gradient, forma, bordo, ombra ed effetti hover. |
| **Tag** | Nome tag, id, classi, attributi, tutti i collegamenti (`href`, `src`...) modificabili con scelta delle pagine locali, HTML interno. |
| **Script** | Elenco degli script (`.js`, `.css`, inline) ordinabile per grandezza, data o nome, con editor integrato. Prima di salvare un `.js` il codice viene verificato con `node --check`: se ci sono errori il file **non viene scritto**. |
| **Tema** | Palette principale del sito letta dai CSS, modificabile (anche con gradient) e applicabile a tutte le pagine. |
| **Utils** | Patch reversibili accendibili/spegnibili, anche su tutto il sito: colori random, una lettera un colore, testi mescolati/casuali/base64, immagini sostituite da un gradient o da un'immagine, marquee, bianco e nero, arcobaleno, specchio, Comic Sans, e altre. Non alterano layout, animazioni o elementi fissi del sito. |
| **Upload** | Carica file nel sito (immagini, video, audio, html, css, js, font...). I nomi vengono sostituiti con un UUID casuale: niente collisioni. |
| **Altro** | Trova e sostituisci (pagina corrente o tutto il sito), backup e ripristino, scorciatoie, informazioni. |

### Sicurezza del server di editing

- Ascolta **solo su 127.0.0.1**; controlla `Host` e `Origin` e richiede un **token casuale** per ogni avvio (iniettato nel `toolbar.js` servito dal server stesso).
- Non scrive mai fuori dalla cartella del sito (path traversal bloccato).
- **Non esegue nulla** di ciò che carichi. I file **PHP e database** (`.php`, `.sql`, `.db`, `.sqlite`...) vengono rifiutati sia in upload sia in salvataggio.
- Ogni salvataggio crea un backup in `_sitecloner_backups/` (ultimi 30 per file).

---

## Opzioni da riga di comando

```text
python crawl.py [url] [opzioni]
```

| Opzione | Descrizione |
|---|---|
| `-o, --output` | Cartella di output (default `./mirror_<dominio>`) |
| `-d, --depth` | Profondità massima di navigazione (default 3) |
| `-w, --workers` | Thread paralleli (default 16) |
| `--max-pages` | Massimo di pagine HTML (0 = illimitato) |
| `--timeout` | Timeout per richiesta in secondi (default 20) |
| `--rate` | Pausa in secondi fra richieste, per dominio |
| `--respect-robots` | Rispetta `robots.txt` (di default è ignorato) |
| `--ignore` | Ignora gli URL che contengono il testo indicato (ripetibile) |
| `--no-rewrite` | Non riscrivere i link |
| `--no-external-assets` | Non scaricare risorse da domini esterni (CDN) |
| `--exclude-subdomains` | Tratta i sottodomini come esterni |
| `--no-fonts`, `--no-media`, `--no-documents` | Salta font, audio/video, documenti |
| `--max-asset-mb` | Salta gli asset più grandi di N MB |
| `--no-parse-js`, `--no-parse-sitemap` | Non cercare URL dentro i JS / nelle sitemap |
| `--keep-login-pages` | Non escludere le pagine di login |
| `--keep-cms-endpoints` | Non ignorare `wp-json`, `xmlrpc.php`, feed, `wp-admin` |
| `--no-metadata` | Non salvare email/telefoni/social |
| `--no-verify-tls` | Non verificare i certificati TLS (solo per siti di test) |
| `--user-agent` | User-Agent personalizzato |
| `--log-level`, `--log-file` | Livello di log e file di log |
| `--cb-threshold`, `--cb-reset` | Soglia e pausa del circuit breaker |
| `--no-priority-queue`, `--rewrite-workers` | Opzioni di tuning |
| `--editor-toolbar` / `--no-editor-toolbar` | Aggiungi/non aggiungere la toolbar (salta la domanda) |
| `--serve [CARTELLA]` | Non clonare: avvia il server di editing (senza valore: cartella corrente) |
| `--add-toolbar` / `--remove-toolbar` | Con `--serve`: aggiungi/togli la toolbar a un clone già scaricato |
| `--port`, `--open-path` | Con `--serve`: porta e pagina da aprire nel browser |

---

## Uso come libreria

```python
from sitecloner import CrawlerConfig, Crawler, setup_logging

setup_logging(level="INFO")
cfg = CrawlerConfig(
    start_url="https://example.com",
    output_dir="./mirror_example",
    max_depth=4,
    max_workers=8,
    rate_limit_delay=0.3,
    add_editor_toolbar=True,
)
stats = Crawler(cfg).run()
print(stats)
```

Per il server di editing: `from sitecloner.editor_server import serve; serve("./mirror_example", port=8000)`.

---

## Struttura dei file prodotti

```text
mirror_<dominio>/
├── <dominio>/                  # pagine e asset, con i link riscritti
│   └── ...
├── _sitecloner_editor/toolbar.js   # toolbar (se abilitata)
├── _url_mapping.json           # mappa URL originale -> file locale
├── 00_emails.txt, 00_phones.txt, 00_social_links.txt   # metadati (opzionali)
├── _uploads/                   # file caricati dall'editor
├── _sitecloner_backups/        # copie di sicurezza dei salvataggi
└── .gitignore                  # contiene "*": un clone non finisce per sbaglio in un repository
```

---

## Limiti noti

- **Il sito clonato è statico.** Tutto ciò che sul sito originale dipende dal server (login, ricerca, form, commenti, carrelli, aree riservate, PHP, database) **non può funzionare offline**. I form di login vengono esclusi; i form di contatto restano ma non inviano nulla.
- **JavaScript non eseguito dal cloner.** Le SPA (React/Vue...) che costruiscono la pagina nel browser non vengono clonate fedelmente: servirebbe un browser headless.
- **Paint** richiede il server di editing (da `file://` il browser blocca la lettura dei pixel).
- **Contorno gradient** attorno a elementi molto particolari può ripiegare su un colore pieno: l'editor lo segnala quando succede.
- L'**annulla** (Ctrl+Z) ricostruisce la pagina: i comportamenti dinamici del sito (menu a tendina...) tornano attivi dopo un ricaricamento.

---

## Risoluzione dei problemi

| Problema | Causa e rimedio |
|---|---|
| Il clone sembra fermo | Il sito risponde lentamente. Guarda le righe `[...] in corso:` ogni 10 s. Prova `-w 3 --rate 1 --timeout 60`. Se la homepage non risponde dopo 4 tentativi lo dice a fine esecuzione. |
| `429`, `502` o timeout | Il sito limita o è sovraccarico: meno worker, `--rate`, riprova più tardi. Il crawler mette in pausa i worker da solo. |
| `encoding error: input conversion failed...` | Un file binario veniva letto come HTML (corretto). Installa `brotli` (`pip install brotli`) se il sito risponde in Brotli. |
| La toolbar non mostra le funzioni nuove | Riavvia il server (`--serve`, che aggiorna i file) e ricarica con **Ctrl+Shift+R**. Apri il sito da `http://127.0.0.1:PORTA/...`. |
| In alto compare "server: assente" | La pagina non è servita dal server di editing: avvia `--serve` e usa quell'indirizzo. |
| Upload o salvataggio rifiutato | PHP e database non sono ammessi. Per i `.js` serve Node.js nel `PATH`. |
| Percorsi troppo lunghi su Windows | I backup usano cartelle con nomi corti; per i cloni molto profondi scegli una cartella di output vicina alla radice del disco. |

---

## Sviluppo e test

```bash
python -m unittest discover -s tests -v
```

I test coprono normalizzazione URL, classificazione e rilevamento di file binari, riscrittura dei link, riconciliazione dei redirect, rilevamento delle pagine di login, build e sintassi della toolbar (con Node, se presente) e il server di editing (autenticazione, path traversal, upload con UUID, blocco PHP/database, salvataggio pagine, backup, verifica del compilatore).

Il JavaScript dell'editor sta in `sitecloner/editor_js/*.js` (un file per area, concatenati in ordine alfabetico da `editor_toolbar.py`): non c'è nessuna fase di build, basta modificare i file e ricaricare la pagina.

---

## Struttura del progetto

```text
├── crawl.py                    # entry point (python crawl.py ...)
├── pyproject.toml              # pacchetto installabile (comando `sitecloner`)
├── requirements.txt
├── LICENSE
├── tests/test_core.py
└── sitecloner/
    ├── __main__.py             # CLI (argparse + modalità guidata)
    ├── config.py               # CrawlerConfig, costanti, regex
    ├── crawler.py              # orchestratore (code, worker, riscrittura)
    ├── http_client.py          # sessione HTTP, retry, rate-limit, circuit breaker
    ├── registry.py             # stato URL thread-safe, redirect, mapping
    ├── parsers.py              # estrazione URL da HTML/CSS
    ├── rewriter.py             # riscrittura link per la navigazione offline
    ├── storage.py              # scrittura atomica, collisioni, mapping
    ├── utils.py                # normalizzazione URL, classificazione, rilevamenti
    ├── logging_setup.py
    ├── editor_server.py        # server di editing (API salvataggio/upload/verifica)
    ├── editor_toolbar.py       # assembla il JS della toolbar
    └── editor_js/              # codice della toolbar (core, shell, elemento, inserisci, ...)
```

---

## Licenza

[MIT](LICENSE).
