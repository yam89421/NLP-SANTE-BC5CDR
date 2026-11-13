from pathlib import Path
import json
import base64
import sys
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

# L'app est dans `streamlit_app/` (dépendances réduites pour Streamlit Cloud) ; le code partagé est à la racine
RACINE = Path(__file__).resolve().parent.parent   # chemins absolus : l'app marche quel que soit le dossier de lancement
sys.path.insert(0, str(RACINE))

# Imports des modules locaux du dossier src
from src.cdr import charger_jsonl
from src.dictionnaire_v4 import DictionnaireV4Fige
from src.negation import detecter
from src.apprise import construire_fenetres, predire
from tals import tokeniser_avec_offsets
from src.qa_recherche import construire_bm25, scores_bm25, premiers, IndexDense
from src.qa_llm import ClientLLM, formater_passages, ABSTENTION, FOURNISSEURS

# -----------------------------------------------------------------------------
# Configuration de la page Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ESIEE Paris - Traitement du Langage Médical",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = RACINE / "data"
ASSETS_DIR = RACINE / "assets"
LOGO_PATH = ASSETS_DIR / "ESIEE_Paris_logo.png"
PASSAGES_PATH = DATA_DIR / "passages.jsonl"
MODELE_APP_V3 = RACINE / "modeles" / "apprise_v3"   # copie locale (notebook 2.4c), non versionnée
DEPOT_HF_APP_V3 = "yam89421/app-v3-pubmedbert-bc5cdr"   # sinon téléchargé depuis Hugging Face (app déployée)
RESULTATS = RACINE / "resultats"
# Cache à part : les prompts de l'app diffèrent de ceux des notebooks, on ne mélange pas avec l'évaluation
CACHE_LLM_PATH = RACINE / "resultats" / "qa" / "cache_llm_app.json"

# -----------------------------------------------------------------------------
# Dictionnaire de Traduction Bilingue (FR / EN)
# -----------------------------------------------------------------------------
TRADUCTIONS = {
    "Français": {
        "menu_title": "NLP Médical",
        "nav_accueil": "Accueil",
        "nav_qa": "Assistant Chatbot (RAG)",
        "nav_ner": "Démonstration NER",
        "nav_metrics": "Tableau de bord & Métriques",
        "app_title": "Extraction et Analyse d'Informations Médicales (Règles & IA)",
        "app_subtitle": "Application de détection d'entités et de recherche documentaire sur données de santé",
        "home_welcome": "Présentation du Projet",
        "home_intro": "Bienvenue sur l'application de démonstration développée dans le cadre du projet Traitement Automatique de la Langue en Santé à ESIEE Paris (binôme AMARA Yanis & TOMAS Alban).",
        "home_ner_title": "1. Extraction d'Entités Nommées (NER)",
        "home_ner_desc": "* **Objectif** : Identifier et catégoriser les mentions de produits chimiques/médicaments (*Chemical*) et de pathologies/symptômes (*Disease*) dans les résumés biomédicaux PubTator.\n* **Approches** : Méthode par dictionnaire/règles + lexique MeSH (`DIC-v4`) et modèle PubMedBERT ajusté (`APP-v3`).\n* **Négation** : Module *NegEx* pour qualifier le statut des mentions (affirmé vs nié).",
        "home_rag_title": "2. Assistant Question-Réponse (RAG)",
        "home_rag_desc": "* **Objectif** : Répondre de manière vérifiable aux questions sur les soins de support en oncologie.\n* **Corpus** : 10 documents INCa découpés en 413 passages.\n* **Méthodes** : Recherche lexicale BM25 (REC-v2) et sémantique dense E5 avec génération sous contrainte par LLM.",
        "qa_title": "Assistant Chatbot (RAG)",
        "qa_subtitle": "Interrogation de la base documentaire de l'Institut National du Cancer (INCa).",
        "qa_placeholder": "Exemple : Que faire contre les nausées pendant la chimiothérapie ?",
        "qa_config": "Configuration RAG",
        "qa_method": "Méthode de recherche :",
        "qa_topk": "Passages extraits (Top-K) :",
        "qa_sources": "Consulter les passages sources transmis au modèle",
        "ner_title": "Extraction d'Entités Nommées (NER)",
        "ner_subtitle": "Détection des catégories Chemical et Disease sur le corpus BC5CDR.",
        "ner_method": "Méthode d'extraction :",
        "ner_negation": "Détection de négation (NegEx)",
        "ner_input_label": "Texte médical (Anglais) :",
        "ner_button": "Exécuter la détection",
        "ner_no_res": "Aucune entité détectée.",
        "ner_no_model": f"Modèle APP-v3 introuvable : ni dossier `modeles/apprise_v3`, ni dépôt Hugging Face `{DEPOT_HF_APP_V3}` accessible.",
        "metrics_title": "Évaluation et Métriques du Projet",
        "metrics_subtitle": "Scores sur TEST (BC5CDR : 500 résumés ; QA INCa : 8 questions), versions figées, lus dans `resultats/`.",
        "metrics_ner_f1": "F1 extraction (APP-v3, PubMedBERT)",
        "metrics_ner_f1_delta": "vs dictionnaire DIC-v4",
        "metrics_rag_hit": "Hit@5 recherche (BM25 REC-v2)",
        "metrics_rag_hit_delta": "avec la recherche dense E5",
        "metrics_bleu": "BLEU (Q2, BM25)",
        "metrics_rouge": "ROUGE-L (Q2, BM25)",
        "metrics_ner_tab": "Extraction des entités (BC5CDR, TEST)",
        "metrics_rag_tab": "Recherche de passages (INCa, k = 5)",
        "metrics_gen_tab": "Génération des réponses (BLEU / ROUGE)",
        "metrics_ner_intro": "Les deux méthodes figées sont appliquées aux 500 résumés de TEST, jamais utilisés pendant les réglages. Une mention n'est comptée juste que si ses limites et sa catégorie sont exactes. **Précision** : part des mentions trouvées qui sont justes. **Rappel** : part des mentions de référence retrouvées. **F1** : moyenne des deux.",
        "metrics_rag_intro": "Pour chacune des 8 questions de TEST, on regarde si les 5 premiers passages renvoyés contiennent les preuves attendues. **Hit@5** : part des questions avec au moins une preuve parmi les 5. **Rappel@5** : part des preuves retrouvées. BM25 compare les mots (ramenés à leur racine) ; la recherche dense (E5) compare le sens des phrases.",
        "metrics_gen_intro": "Les réponses produites sont comparées aux réponses de référence rédigées à la main. **Q0** : premier passage BM25 recopié tel quel ; **Q1** : LLM avec une consigne simple ; **Q2** : LLM avec une consigne stricte (s'appuyer sur les seuls passages, citer leurs identifiants, dire quand l'information manque). BLEU (0 à 100) et ROUGE (0 à 1) comptent les mots en commun : ils servent à comparer les configurations, pas à juger seuls si une réponse est correcte.",
        "github_btn": "Voir le code source",
        "api_key_label": "Clé API Mistral",
        "api_key_aide": "Utilisée seulement pendant cette session, jamais enregistrée.",
        "qa_sans_cle": "Renseigner une clé API Mistral dans la barre latérale pour obtenir une réponse générée. Passages trouvés :",
        "qa_echec": "Appel au LLM impossible (vérifier la clé API)",
    },
    "English": {
        "menu_title": "Medical NLP",
        "nav_accueil": "Home",
        "nav_qa": "Chatbot Assistant (RAG)",
        "nav_ner": "NER Demonstration",
        "nav_metrics": "Dashboard & Metrics",
        "app_title": "Medical Information Extraction & Analysis (Rules & AI)",
        "app_subtitle": "Named entity recognition and document retrieval system for healthcare data",
        "home_welcome": "Project Overview",
        "home_intro": "Welcome to the demonstration web application developed for the Healthcare Natural Language Processing course at ESIEE Paris (AMARA Yanis & TOMAS Alban).",
        "home_ner_title": "1. Named Entity Recognition (NER)",
        "home_ner_desc": "* **Goal**: Detect and classify mentions of chemicals/drugs (*Chemical*) and diseases/symptoms (*Disease*) in PubTator abstracts.\n* **Methods**: Rule-based dictionary + MeSH lexicon (`DIC-v4`) and fine-tuned PubMedBERT (`APP-v3`).\n* **Negation**: *NegEx* module to determine entity status (affirmed vs negated).",
        "home_rag_title": "2. Question-Answering Assistant (RAG)",
        "home_rag_desc": "* **Goal**: Provide accurate answers regarding oncological supportive care.\n* **Corpus**: 10 INCa documents split into 413 passages.\n* **Methods**: BM25 lexical and Dense E5 semantic retrieval combined with constrained LLM generation.",
        "qa_title": "Chatbot Assistant (RAG)",
        "qa_subtitle": "Searching through the National Cancer Institute (INCa) knowledge base.",
        "qa_placeholder": "Example (documents are in French): Que faire contre les nausées pendant la chimiothérapie ?",
        "qa_config": "RAG Configuration",
        "qa_method": "Retrieval Method:",
        "qa_topk": "Extracted Passages (Top-K):",
        "qa_sources": "View source passages sent to the model",
        "ner_title": "Named Entity Recognition (NER)",
        "ner_subtitle": "Detection of Chemical and Disease entities on the BC5CDR corpus.",
        "ner_method": "Extraction Method:",
        "ner_negation": "Negation Detection (NegEx)",
        "ner_input_label": "Medical Text (English):",
        "ner_button": "Run Detection",
        "ner_no_res": "No entities detected.",
        "ner_no_model": f"APP-v3 model not found: no `modeles/apprise_v3` folder and Hugging Face repo `{DEPOT_HF_APP_V3}` not reachable.",
        "metrics_title": "Project Evaluation & Metrics",
        "metrics_subtitle": "TEST scores (BC5CDR: 500 abstracts; INCa QA: 8 questions), frozen versions, read from `resultats/`.",
        "metrics_ner_f1": "Extraction F1 (APP-v3, PubMedBERT)",
        "metrics_ner_f1_delta": "vs DIC-v4 dictionary",
        "metrics_rag_hit": "Retrieval Hit@5 (BM25 REC-v2)",
        "metrics_rag_hit_delta": "with dense E5 retrieval",
        "metrics_bleu": "BLEU (Q2, BM25)",
        "metrics_rouge": "ROUGE-L (Q2, BM25)",
        "metrics_ner_tab": "Entity extraction (BC5CDR, TEST)",
        "metrics_rag_tab": "Passage retrieval (INCa, k = 5)",
        "metrics_gen_tab": "Answer generation (BLEU / ROUGE)",
        "metrics_ner_intro": "Both frozen methods are applied to the 500 TEST abstracts, never used during tuning. A mention counts as correct only if its boundaries and category are exact. **Precision**: share of found mentions that are correct. **Recall**: share of reference mentions found. **F1**: balance of the two.",
        "metrics_rag_intro": "For each of the 8 TEST questions, we check whether the top 5 returned passages contain the expected evidence. **Hit@5**: share of questions with at least one piece of evidence in the top 5. **Recall@5**: share of evidence found. BM25 compares words (reduced to their stem); dense retrieval (E5) compares sentence meaning.",
        "metrics_gen_intro": "Generated answers are compared to hand-written reference answers. **Q0**: first BM25 passage copied as is; **Q1**: LLM with a simple instruction; **Q2**: LLM with a strict instruction (rely only on the passages, cite their IDs, say when information is missing). BLEU (0 to 100) and ROUGE (0 to 1) count shared words: they compare configurations but do not, on their own, tell whether an answer is correct.",
        "github_btn": "View Source Code",
        "api_key_label": "Mistral API key",
        "api_key_aide": "Used only during this session, never stored.",
        "qa_sans_cle": "Enter a Mistral API key in the sidebar to get a generated answer. Retrieved passages:",
        "qa_echec": "LLM call failed (check the API key)",
    }
}

# -----------------------------------------------------------------------------
# Style CSS : Positionnement du Logo & Pied de Barre Latérale
# -----------------------------------------------------------------------------
CSS_THEME = """
<style>
    /* 1. Marges haut de la zone principale */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }

    /* 2. Style du logo ESIEE */
    .esiee-logo {
        max-width: 140px;
        height: auto;
        margin-bottom: 2rem !important;
    }
    
    @media (prefers-color-scheme: dark) {
        .esiee-logo { filter: brightness(0) invert(1); }
    }
    [data-theme="dark"] .esiee-logo,
    [data-testid="stAppViewContainer"].dark .esiee-logo {
        filter: brightness(0) invert(1);
    }

    /* 3. Ancrage du footer dans la Sidebar */
    [data-testid="stSidebarContent"] {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    
    .sidebar-footer {
        margin-top: auto;
        padding-top: 1rem;
    }
</style>
"""
st.markdown(CSS_THEME, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Chargement des ressources
# -----------------------------------------------------------------------------
@st.cache_resource
def charger_passages():
    passages = []
    if PASSAGES_PATH.exists():
        with open(PASSAGES_PATH, encoding="utf-8") as f:
            for line in f:
                passages.append(json.loads(line))
    else:
        passages = [
            {
                "passage_id": "DOC001_P001",
                "document_id": "DOC001",
                "texte": "Les nausées et vomissements sont des effets indésirables fréquents des chimiothérapies.",
                "localisation": {"section": "Effets secondaires", "pages_imprimees": "12"}
            },
            {
                "passage_id": "DOC001_P002",
                "document_id": "DOC001",
                "texte": "L'administration d'antiémétiques permet de prévenir efficacement les nausées.",
                "localisation": {"section": "Prise en charge", "pages_imprimees": "13"}
            }
        ]
    return passages


@st.cache_resource
def initialiser_index_bm25(_passages):
    textes = [p["texte"] for p in _passages]
    return construire_bm25(textes, racines=True)   # REC-v2 : racinisation Snowball


@st.cache_resource
def initialiser_index_dense(_passages):
    # Comme dans 5_evaluation : titre de section + texte
    return IndexDense([f'{p["localisation"]["section"]} {p["texte"]}' for p in _passages])


@st.cache_resource
def charger_dictionnaire_ner():
    """DIC-v4 figée : DIC-v3 reconstruite sur TRAIN + termes MeSH retenus par le notebook 2.3c (≈ 10 s, une seule fois)."""
    documents = charger_jsonl(DATA_DIR / "corpus_extraction.jsonl")
    return DictionnaireV4Fige(RESULTATS / "extraction" / "dictionnaire_v4_termes_mesh.tsv.gz").construire(
        [d for d in documents if d.partition == "train"])


@st.cache_resource
def charger_app_v3():
    """Modèle APP-v3 figé (PubMedBERT ajusté) : copie locale, sinon Hugging Face ; None si aucun des deux."""
    dossier = MODELE_APP_V3
    if not (dossier / "config.json").exists():
        try:
            from huggingface_hub import snapshot_download
            dossier = Path(snapshot_download(DEPOT_HF_APP_V3))   # ≈ 430 Mo, gardé en cache ensuite
        except Exception:
            return None
    from transformers import BertForTokenClassification, BertTokenizerFast
    # Version rapide (word_ids) : c'est ce que `BertTokenizer` donnait sous transformers 5 sur Colab
    tok = BertTokenizerFast.from_pretrained(dossier, do_lower_case=True)
    modele = BertForTokenClassification.from_pretrained(dossier)
    return tok, modele


def extraire_app_v3(texte, tok, modele):
    """Même découpage en mots et même prédiction que pour l'évaluation (sections 2.2 et 2.4)."""
    mots = tokeniser_avec_offsets(texte)
    doc = {"document_id": "DOC_DEMO", "tokens": [m for m, _, _ in mots], "offsets": [(a, b) for _, a, b in mots]}
    fenetres = construire_fenetres([doc], {"DOC_DEMO": texte}, tok, max_length=512)
    return predire(modele, tok, fenetres, {"DOC_DEMO": doc}, max_length=512)


passages = charger_passages()
index_bm25 = initialiser_index_bm25(passages)
dict_ner = charger_dictionnaire_ner()

# -----------------------------------------------------------------------------
# Gestion de la Langue via session_state
# -----------------------------------------------------------------------------
if "langue_select" not in st.session_state:
    st.session_state.langue_select = "Français"

langue = "Français" if "Français" in st.session_state.langue_select else "English"
txt = TRADUCTIONS[langue]

# -----------------------------------------------------------------------------
# Barre Latérale : Navigation principale & Options
# -----------------------------------------------------------------------------
if "nav_index" not in st.session_state:
    st.session_state.nav_index = 0

options_nav = [
    txt["nav_accueil"],
    txt["nav_qa"],
    txt["nav_ner"],
    txt["nav_metrics"],
]

with st.sidebar:
    choix_menu = option_menu(
        menu_title=txt["menu_title"],
        options=options_nav,
        icons=["house", "chat-dots", "tags", "bar-chart-fill"],
        menu_icon="heart-pulse",
        default_index=st.session_state.nav_index,
    )
    st.session_state.nav_index = options_nav.index(choix_menu)

st.sidebar.markdown("---")

if choix_menu == txt["nav_qa"]:
    st.sidebar.subheader(txt["qa_config"])
    methode_recherche = st.sidebar.radio(
        txt["qa_method"],
        ["BM25 REC-v2 (Lexical)", "Dense E5 (Sémantique)"]
    )
    top_k = st.sidebar.slider(txt["qa_topk"], min_value=1, max_value=10, value=5)
    # Clé saisie par l'utilisateur : gardée dans sa session, jamais dans os.environ (partagé entre visiteurs)
    cle_api = st.sidebar.text_input(txt["api_key_label"], type="password", help=txt["api_key_aide"], key="cle_api")

# -----------------------------------------------------------------------------
# Pied de Barre Latérale (Sélecteur de Langue + Bouton GitHub)
# -----------------------------------------------------------------------------
st.sidebar.markdown('<div class="sidebar-footer">', unsafe_allow_html=True)

st.sidebar.selectbox(
    "Langue / Language",
    ["Français", "English"],
    key="langue_select"
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

github_button_html = f"""
<a href="https://github.com/yam89421/NLP-SANTE-BC5CDR" target="_blank" style="text-decoration: none;">
    <div style="display: flex; align-items: center; justify-content: center; background-color: #24292e; color: #ffffff; padding: 10px 12px; border-radius: 6px; font-weight: 600; font-size: 0.88rem; gap: 8px; border: 1px solid #1b1f23;">
        <svg height="16" width="16" viewBox="0 0 16 16" fill="white">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.28.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
        </svg>
        {txt['github_btn']}
    </div>
</a>
"""
st.sidebar.markdown(github_button_html, unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Logo ESIEE Paris (Présent sur toutes les pages tout en haut)
# -----------------------------------------------------------------------------
if LOGO_PATH.exists():
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode()
    st.markdown(f'<img src="data:image/png;base64,{encoded}" class="esiee-logo" alt="ESIEE Paris">', unsafe_allow_html=True)
else:
    st.markdown("### ESIEE PARIS")

# =============================================================================
# SECTION : Accueil / Home
# =============================================================================
if choix_menu == txt["nav_accueil"]:
    st.title(txt["app_title"])
    st.caption(txt["app_subtitle"])
    st.markdown("---")

    st.subheader(txt["home_welcome"])
    st.markdown(txt["home_intro"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### {txt['home_ner_title']}")
        st.markdown(txt["home_ner_desc"])

    with col2:
        st.markdown(f"### {txt['home_rag_title']}")
        st.markdown(txt["home_rag_desc"])

# =============================================================================
# SECTION : Assistant Chatbot (RAG)
# =============================================================================
elif choix_menu == txt["nav_qa"]:
    st.title(txt["qa_title"])
    st.caption(txt["qa_subtitle"])
    st.markdown("---")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "passages" in message:
                with st.expander(txt["qa_sources"]):
                    for p in message["passages"]:
                        st.write(f"**[{p['passage_id']}]** (Section : {p['localisation'].get('section', 'N/A')})")
                        st.info(p["texte"])

    if query := st.chat_input(txt["qa_placeholder"]):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("..."):
                if methode_recherche.startswith("BM25"):
                    scores = scores_bm25(query, index_bm25)
                    top_indices = [idx for idx, _ in premiers(scores, k=top_k)]
                else:
                    try:
                        index_dense = initialiser_index_dense(passages)
                        scores = index_dense.scores(query)
                        top_indices = [int(i) for i in scores.argsort()[::-1][:top_k]]
                    except Exception as e:
                        st.error(f"Error: {e}. Fallback to BM25.")
                        scores = scores_bm25(query, index_bm25)
                        top_indices = [idx for idx, _ in premiers(scores, k=top_k)]

                passages_selectionnes = [passages[i] for i in top_indices]
                contexte_formate = formater_passages(passages_selectionnes)

                prompt_systeme = (
                    "Vous êtes un assistant médical. Répondez à la question en vous appuyant "
                    "exclusivement sur les passages fournis ci-dessous. Si l'information est absente, "
                    f"répondez exactement : '{ABSTENTION}'.\n\n"
                    f"Passages :\n{contexte_formate}\n\n"
                    f"Question : {query}"
                )

                try:
                    if not cle_api:
                        raise LookupError
                    client_llm = ClientLLM(   # Mistral, modèle de la comparaison LLM-MIS-v1 (notebook 4.4)
                        modele="mistral-medium-2604",
                        temperature=0.0,
                        seed=42,
                        max_tokens=500,
                        chemin_cache=CACHE_LLM_PATH,
                        fournisseur="mistral",
                    )
                    from openai import OpenAI
                    # API Mistral au format OpenAI ; la clé saisie remplace la lecture du .env
                    client_llm._client = OpenAI(api_key=cle_api, base_url=FOURNISSEURS["mistral"][1])
                    res = client_llm.generer(prompt_systeme)
                    if res.get("echec"):   # generer ne lève pas d'exception : l'échec est dans le résultat
                        raise RuntimeError(res["echec"])
                    reponse_texte = res.get("texte") or ABSTENTION
                except LookupError:
                    reponse_texte = f"{txt['qa_sans_cle']}\n\n{contexte_formate}"
                except Exception as err:
                    reponse_texte = f"{txt['qa_echec']} : {err}\n\nSources :\n\n{contexte_formate}"

                st.markdown(reponse_texte)
                
                with st.expander(txt["qa_sources"]):
                    for p in passages_selectionnes:
                        st.write(f"**[{p['passage_id']}]** (Section : {p['localisation'].get('section', 'N/A')})")
                        st.info(p["texte"])

        st.session_state.messages.append({
            "role": "assistant",
            "content": reponse_texte,
            "passages": passages_selectionnes
        })

# =============================================================================
# SECTION : Démonstration NER
# =============================================================================
elif choix_menu == txt["nav_ner"]:
    st.title(txt["ner_title"])
    st.caption(txt["ner_subtitle"])
    st.markdown("---")
    
    col_input, col_opt = st.columns([3, 1])
    
    with col_opt:
        modele_ner = st.radio(txt["ner_method"], ["Dictionnaire (DIC-v4)", "PubMedBERT (APP-v3)"])
        activer_negation = st.checkbox(txt["ner_negation"], value=True)
    
    with col_input:
        texte_defaut = (
            "The patient was treated with cisplatin and cyclophosphamide. "
            "No evidence of cardiotoxicity was observed, but severe nausea was reported."
        )
        texte_test = st.text_area(txt["ner_input_label"], value=texte_defaut, height=140)

    if st.button(txt["ner_button"], type="primary"):
        if modele_ner.startswith("PubMedBERT"):
            app_v3 = charger_app_v3()
            if app_v3 is None:
                st.error(txt["ner_no_model"])
                st.stop()
            with st.spinner("PubMedBERT..."):
                mentions_trouvees = extraire_app_v3(texte_test, *app_v3)
        else:
            mentions_trouvees = dict_ner.extraire(texte_test, doc="DOC_DEMO")
        mentions_trouvees = sorted(mentions_trouvees, key=lambda m: m.debut)
        
        if not mentions_trouvees:
            st.info(txt["ner_no_res"])
        else:
            data_res = []
            for m in mentions_trouvees:
                extrait_texte = texte_test[m.debut:m.fin]
                statut_neg = "N/A"
                
                if activer_negation:
                    try:
                        dec = detecter(texte_test, m.debut, m.fin, version="v0")
                        statut_neg = "Négative" if dec.label == "nie" else "Affirmée"
                    except Exception:
                        statut_neg = "Indéterminé"

                data_res.append({
                    "Mention": extrait_texte,
                    "Catégorie": m.type,
                    "Début": m.debut,
                    "Fin": m.fin,
                    "Statut Négation": statut_neg
                })

            df_res = pd.DataFrame(data_res)
            st.dataframe(df_res, width="stretch")

# =============================================================================
# SECTION : Tableau de bord & Métriques
# =============================================================================
elif choix_menu == txt["nav_metrics"]:
    st.title(txt["metrics_title"])
    st.caption(txt["metrics_subtitle"])
    st.markdown("---")
    
    # Scores TEST lus dans les fichiers écrits par 5_evaluation.ipynb (versions figées)
    ner = pd.read_csv(RESULTATS / "extraction" / "scores_test.csv")
    ner_global = ner[ner.categorie == "global (micro)"].set_index("methode")
    f1_app = ner_global.filter(like="APP-v3", axis=0)["F1"].iloc[0]
    f1_dic = ner_global.filter(like="dictionnaire", axis=0)["F1"].iloc[0]
    recherche = pd.read_csv(RESULTATS / "qa" / "recherche_test.csv").groupby("recherche")[["hit@5", "rappel@5"]].mean()
    hit_bm25 = recherche.filter(like="BM25", axis=0)["hit@5"].iloc[0]
    hit_dense = recherche.filter(like="dense", axis=0)["hit@5"].iloc[0]
    generation = pd.read_csv(RESULTATS / "qa" / "bleu_rouge.csv", index_col=0)
    q2 = generation.loc["Q2 v1 c2 (BM25)"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(label=txt["metrics_ner_f1"], value=f"{f1_app:.3f}",
              delta=f"{f1_app - f1_dic:+.3f} {txt['metrics_ner_f1_delta']}")
    c2.metric(label=txt["metrics_rag_hit"], value=f"{hit_bm25:.3f}",
              delta=f"{hit_dense - hit_bm25:+.3f} {txt['metrics_rag_hit_delta']}")
    c3.metric(label=txt["metrics_bleu"], value=f"{q2['BLEU']:.1f}")
    c4.metric(label=txt["metrics_rouge"], value=f"{q2['ROUGE-L']:.3f}")

    st.markdown("---")

    st.markdown(f"### {txt['metrics_ner_tab']}")
    st.markdown(txt["metrics_ner_intro"])
    st.table(ner[["methode", "categorie", "precision", "rappel", "F1"]]
             .rename(columns={"methode": "Méthode", "categorie": "Catégorie", "precision": "Précision", "rappel": "Rappel"})
             .style.format(precision=4))

    st.markdown(f"### {txt['metrics_rag_tab']}")
    st.markdown(txt["metrics_rag_intro"])
    st.dataframe(recherche.rename_axis("Méthode").round(3), width="stretch")

    st.markdown(f"### {txt['metrics_gen_tab']}")
    st.markdown(txt["metrics_gen_intro"])
    st.dataframe(generation[["BLEU", "ROUGE-1", "ROUGE-2", "ROUGE-L"]].rename_axis("Configuration"), width="stretch")
