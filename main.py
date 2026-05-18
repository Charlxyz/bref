"""
╔══════════════════════════════════════════════════════════════╗
║                        MERCATOR                              ║
║              Jeu de commerce stratégique                     ║
╚══════════════════════════════════════════════════════════════╝

Auteur : version améliorée à partir d'un code NSI
Niveau  : Lycée / NSI (Python pur, bibliothèque standard uniquement)
"""

import random
import time
import os
import sys

# ──────────────────────────────────────────────
#  CODES ANSI pour la couleur et le style
# ──────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    # Texte
    BLANC   = "\033[97m"
    JAUNE   = "\033[93m"
    CYAN    = "\033[96m"
    VERT    = "\033[92m"
    ROUGE   = "\033[91m"
    MAGENTA = "\033[95m"
    BLEU    = "\033[94m"
    GRIS    = "\033[90m"

    # Fond
    FOND_NOIR   = "\033[40m"
    FOND_ROUGE  = "\033[41m"
    FOND_VERT   = "\033[42m"
    FOND_JAUNE  = "\033[43m"
    FOND_BLEU   = "\033[44m"


# ──────────────────────────────────────────────
#  CONSTANTES DE JEU
# ──────────────────────────────────────────────
ARGENT_DEPART   = 200
LIMITE_STOCK    = 20
OBJECTIF        = 1500
JOURS_MAX       = 30

# ── Saisons ───────────────────────────────────────────────────────────────────
SAISONS = [
    {
        "nom": "Printemps", "emoji": "🌸",
        "modificateurs": {
            "ble":     {"offre": +20, "demande": +5},
            "poisson": {"offre": +10, "demande": +10},
            "soie":    {"offre": +5,  "demande": +15},
            "epices":  {"offre": 0,   "demande": +5},
            "or":      {"offre": 0,   "demande": 0},
        },
        "desc": "Bonnes récoltes de blé. Soie prisée.",
    },
    {
        "nom": "Été", "emoji": "☀",
        "modificateurs": {
            "ble":     {"offre": +10, "demande": 0},
            "poisson": {"offre": +25, "demande": +5},
            "soie":    {"offre": +10, "demande": +5},
            "epices":  {"offre": +15, "demande": +10},
            "or":      {"offre": 0,   "demande": +5},
        },
        "desc": "Poisson abondant. Épices accessibles.",
    },
    {
        "nom": "Automne", "emoji": "🍂",
        "modificateurs": {
            "ble":     {"offre": 0,   "demande": +10},
            "poisson": {"offre": -5,  "demande": +5},
            "soie":    {"offre": -10, "demande": +20},
            "epices":  {"offre": -5,  "demande": +15},
            "or":      {"offre": 0,   "demande": +10},
        },
        "desc": "Soie et épices très demandées. Réserves pour l'hiver.",
    },
    {
        "nom": "Hiver", "emoji": "❄",
        "modificateurs": {
            "ble":     {"offre": -20, "demande": +25},
            "poisson": {"offre": -15, "demande": +10},
            "soie":    {"offre": -5,  "demande": +5},
            "epices":  {"offre": -10, "demande": +20},
            "or":      {"offre": +5,  "demande": -5},
        },
        "desc": "Blé et poisson rares. Épices très chères.",
    },
]

def get_saison():
    """Retourne la saison actuelle selon le jour."""
    idx = ((jour - 1) // 8) % 4
    return SAISONS[idx]

# ── Concurrents PNJ ────────────────────────────────────────────────────────────
CONCURRENTS_BASE = [
    {"nom": "Marchande Lysa",   "emoji": "👩", "capital": 180, "style": "prudent"},
    {"nom": "Negociant Borras", "emoji": "🧔", "capital": 250, "style": "agressif"},
    {"nom": "Dame Orianne",     "emoji": "👸", "capital": 150, "style": "speculateur"},
]

concurrents = []   # liste d'états mutables, initialisée dans reinitialiser()

PRODUITS = {
    "ble":     {"nom": "Blé",       "prix_base": 8,  "volatilite": 0.3, "emoji": "🌾"},
    "soie":    {"nom": "Soie",      "prix_base": 25, "volatilite": 0.5, "emoji": "🧵"},
    "epices":  {"nom": "Épices",    "prix_base": 40, "volatilite": 0.6, "emoji": "🌶"},
    "or":      {"nom": "Or",        "prix_base": 80, "volatilite": 0.7, "emoji": "✨"},
    "poisson": {"nom": "Poisson",   "prix_base": 12, "volatilite": 0.4, "emoji": "🐟"},
    "sel":     {"nom": "Sel",       "prix_base": 6,  "volatilite": 0.2, "emoji": "🧂"},
}

employe = {
    "actif": False,
    "niveau": 0,
    "salaire": 0,
    "cout_embauche": 0,
    "nom": None,
    "fiabilite": 0.0,
    "moral": 100,          # 0-100, impacte l'efficacité réelle
    "jours_travailles": 0, # pour l'évolution de carrière
    "salaires_impaye": 0,  # compteur de jours sans paiement
}

# ── Conserves (poisson + sel → conserves) ────────────────────────────────────
CONSERVERIES = {
    1: {
        "nom": "Cuve de saumure",
        "emoji": "🪣",
        "cout": 120,
        "poisson_par_boite": 2,
        "sel_par_boite": 1,
        "capacite_jour": 3,
        "entretien": 3,
        "desc": "Simple. Produit des conserves basiques.",
    },
    2: {
        "nom": "Atelier de conserverie",
        "emoji": "🏺",
        "cout": 350,
        "poisson_par_boite": 1,
        "sel_par_boite": 1,
        "capacite_jour": 7,
        "entretien": 9,
        "desc": "Rendement élevé. Conserves de qualité.",
    },
    3: {
        "nom": "Manufacture royale de conserves",
        "emoji": "🏭",
        "cout": 750,
        "poisson_par_boite": 1,
        "sel_par_boite": 1,
        "capacite_jour": 15,
        "entretien": 18,
        "desc": "Production en série. Très rentable.",
    },
}
CONSERVES_PRIX_BASE = 28  # vs poisson 12 + sel 6 = coût 18 → marge nette

conserveur = {
    "actif": False, "niveau": 0, "salaire": 0,
    "nom": None, "efficacite": 0.0,
    "moral": 100, "jours_travailles": 0, "salaires_impaye": 0,
}
conserverie = {
    "possede": False, "niveau": 0, "nom": None, "emoji": "",
    "poisson_par_boite": 0, "sel_par_boite": 0,
    "capacite_jour": 0, "entretien": 0,
    "usure": 0, "usure_max": 40, "en_panne": False,
}
stock_conserves          = 0
prix_conserves           = CONSERVES_PRIX_BASE
conserves_produites_total = 0
offre_demande_conserves  = {"offre": 100, "demande": 100}

# ── Tissu brodé (épices + soie → tissu brodé) ────────────────────────────────
ATELIERS_TISSU = {
    1: {
        "nom": "Métier à broder",
        "emoji": "🪡",
        "cout": 200,
        "soie_par_tissu": 2,
        "epices_par_tissu": 1,
        "capacite_jour": 2,
        "entretien": 5,
        "desc": "Artisanal. Tissus brodés de belle facture.",
    },
    2: {
        "nom": "Atelier de broderie",
        "emoji": "🧵",
        "cout": 500,
        "soie_par_tissu": 1,
        "epices_par_tissu": 1,
        "capacite_jour": 5,
        "entretien": 12,
        "desc": "Cadence soutenue. Bonne rentabilité.",
    },
    3: {
        "nom": "Manufacture de luxe",
        "emoji": "✨",
        "cout": 1000,
        "soie_par_tissu": 1,
        "epices_par_tissu": 1,
        "capacite_jour": 10,
        "entretien": 25,
        "desc": "Tissus de prestige. Prix de vente record.",
    },
}
TISSU_PRIX_BASE = 90  # vs soie 25 + épices 40 = coût 65 → marge 25+

brodeur = {
    "actif": False, "niveau": 0, "salaire": 0,
    "nom": None, "efficacite": 0.0,
    "moral": 100, "jours_travailles": 0, "salaires_impaye": 0,
}
atelier_tissu = {
    "possede": False, "niveau": 0, "nom": None, "emoji": "",
    "soie_par_tissu": 0, "epices_par_tissu": 0,
    "capacite_jour": 0, "entretien": 0,
    "usure": 0, "usure_max": 35, "en_panne": False,
}
stock_tissu          = 0
prix_tissu           = TISSU_PRIX_BASE
tissu_produit_total  = 0
offre_demande_tissu  = {"offre": 100, "demande": 100}

# Usure aussi sur les machines existantes
USURE_MAX_MACHINE  = 50
USURE_MAX_METIER   = 45
USURE_MAX_ATELIER_OR = 40

# ──────────────────────────────────────────────
#  SYSTEME DE TRANSFORMATION BLE → FARINE
# ──────────────────────────────────────────────

MACHINES = {
    1: {
        "nom":            "Meule manuelle",
        "emoji":          "🪨",
        "cout":           80,
        "ble_par_farine": 3,
        "capacite_jour":  2,
        "entretien":      2,
        "desc":           "Lente mais bon marche. Rendement mediocre.",
    },
    2: {
        "nom":            "Moulin a vent",
        "emoji":          "🌬",
        "cout":           250,
        "ble_par_farine": 2,
        "capacite_jour":  5,
        "entretien":      6,
        "desc":           "Bon equilibre cout/rendement. Populaire.",
    },
    3: {
        "nom":            "Moulin industriel",
        "emoji":          "⚙",
        "cout":           600,
        "ble_par_farine": 1,
        "capacite_jour":  12,
        "entretien":      15,
        "desc":           "Tres efficace. Rentable a grande echelle.",
    },
}

FARINE_PRIX_BASE = 18

meunier = {
    "actif":      False,
    "niveau":     0,
    "salaire":    0,
    "nom":        None,
    "efficacite": 0.0,
    "moral": 100, "jours_travailles": 0, "salaires_impaye": 0,
}

machine = {
    "possede":        False,
    "niveau":         0,
    "nom":            None,
    "emoji":          "",
    "ble_par_farine": 0,
    "capacite_jour":  0,
    "entretien":      0,
    "usure":          0,
    "usure_max":      USURE_MAX_MACHINE,
    "en_panne":       False,
}

stock_farine          = 0
prix_farine           = FARINE_PRIX_BASE
farine_produite_total = 0
offre_demande_farine  = {"offre": 100, "demande": 100}

EVENEMENTS = [
    # ── Négatifs ──────────────────────────────────────────────────────────────
    {"msg": "⚡ Tempête ! Vos marchandises sont endommagées.",              "argent":  0,   "mult": 1.0,  "cible": None,      "perte_stock": 0.30},
    {"msg": "🔥 Incendie au marché ! Le blé part en fumée.",               "argent":  0,   "mult": 1.4,  "cible": "ble",     "perte_stock": 0},
    {"msg": "🏴‍☠️  Pirates ! Ils vous délestent de votre bourse.",          "argent": -60,  "mult": 1.0,  "cible": None,      "perte_stock": 0},
    {"msg": "🌊 Inondation ! Le stock de poisson est gâté.",               "argent":  0,   "mult": 1.3,  "cible": "poisson", "perte_stock": 0},
    {"msg": "🕵️  Contrebandiers ! Les épices se font rares.",              "argent":  0,   "mult": 1.5,  "cible": "epices",  "perte_stock": 0},
    {"msg": "🦠 Maladie du vers à soie ! La soie s'effondre.",             "argent":  0,   "mult": 0.4,  "cible": "soie",    "perte_stock": 0},
    {"msg": "🐀 Invasion de rats ! Une partie du blé est perdue.",         "argent":  0,   "mult": 0.9,  "cible": "ble",     "perte_stock": 0.20},
    {"msg": "⚔️  Guerre commerciale ! Les taxes explosent.",               "argent": -80,  "mult": 1.0,  "cible": None,      "perte_stock": 0},
    {"msg": "🌪  Ouragan au port ! Les cales sont à moitié vides.",        "argent":  0,   "mult": 1.0,  "cible": None,      "perte_stock": 0.15},
    {"msg": "💀 Épidémie ! Les marchands fuient la ville.",                "argent": -40,  "mult": 0.8,  "cible": None,      "perte_stock": 0},
    {"msg": "🏦 Banquier véreux ! Il saisit une partie de votre capital.", "argent": -50,  "mult": 1.0,  "cible": None,      "perte_stock": 0},
    {"msg": "🦟 Nuée d'insectes ! Les épices sont contaminées.",           "argent":  0,   "mult": 0.7,  "cible": "epices",  "perte_stock": 0.10},
    {"msg": "🌧  Pluies interminables ! Le poisson abonde, les prix chutent.", "argent": 0, "mult": 0.5, "cible": "poisson", "perte_stock": 0},
    {"msg": "💸 Fraude fiscale ! L'inspecteur vous réclame une amende.",   "argent": -70,  "mult": 1.0,  "cible": None,      "perte_stock": 0},
    {"msg": "🔨 Sabotage ! Un concurrent brise votre stock d'or.",         "argent":  0,   "mult": 1.0,  "cible": "or",      "perte_stock": 0.25},
    # ── Positifs ──────────────────────────────────────────────────────────────
    {"msg": "☀️  Bonne récolte ! Le blé est bradé sur les marchés.",       "argent":  0,   "mult": 0.6,  "cible": "ble",     "perte_stock": 0},
    {"msg": "👑 Commande royale ! L'or est très demandé.",                 "argent":  0,   "mult": 1.6,  "cible": "or",      "perte_stock": 0},
    {"msg": "🎉 Fête du village ! Un bonus vous est offert.",               "argent": 50,   "mult": 1.0,  "cible": None,      "perte_stock": 0},
    {"msg": "💎 Caravane de soie ! Les marchands inondent le port.",       "argent":  0,   "mult": 0.5,  "cible": "soie",    "perte_stock": 0},
    {"msg": "🏆 Concours de commerce ! Vous remportez la mise.",           "argent": 90,   "mult": 1.0,  "cible": None,      "perte_stock": 0},
    {"msg": "🤝 Alliance marchande ! Un partenaire vous verse une part.",  "argent": 60,   "mult": 1.0,  "cible": None,      "perte_stock": 0},
    {"msg": "⚓ Flotte commerciale ! Le poisson arrive en masse.",         "argent":  0,   "mult": 0.55, "cible": "poisson", "perte_stock": 0},
    {"msg": "🌿 Récolte exceptionnelle d'épices dans les colonies.",       "argent":  0,   "mult": 0.6,  "cible": "epices",  "perte_stock": 0},
    {"msg": "🏰 Noble mécène ! Il finance vos affaires.",                  "argent": 120,  "mult": 1.0,  "cible": None,      "perte_stock": 0},
    {"msg": "📜 Contrat lucratif ! La demande d'or grimpe.",               "argent": 30,   "mult": 1.5,  "cible": "or",      "perte_stock": 0},
    {"msg": "🎊 Festival des tissus ! La soie est très prisée.",           "argent":  0,   "mult": 1.7,  "cible": "soie",    "perte_stock": 0},
    {"msg": "🌾 Grenier royal ouvert ! Bénéfice partagé.",                 "argent": 40,   "mult": 0.8,  "cible": "ble",     "perte_stock": 0},
    # ── Neutres ───────────────────────────────────────────────────────────────
    {"msg": "📈 Marché calme. Les marchands attendent.",                   "argent":  0,   "mult": 1.0,  "cible": None,      "perte_stock": 0},
    {"msg": "🌤  Journée ordinaire. Rien de notable.",                     "argent":  0,   "mult": 1.0,  "cible": None,      "perte_stock": 0},
    {"msg": "🔔 Rumeurs de pénurie. Les spéculateurs s'agitent.",          "argent":  0,   "mult": 1.1,  "cible": None,      "perte_stock": 0},
    {"msg": "🗺  Nouveau comptoir ouvert. Le marché se rééquilibre.",      "argent":  0,   "mult": 0.95, "cible": None,      "perte_stock": 0},
    {"msg": "⚖️  Inspection des balances. Les prix stagnent.",             "argent":  0,   "mult": 1.0,  "cible": None,      "perte_stock": 0},
    {"msg": "🌙 Nuit agitée au port. Les rumeurs font monter les prix.",   "argent":  0,   "mult": 1.05, "cible": None,      "perte_stock": 0},
]

# ──────────────────────────────────────────────
#  SYSTEME TISSAGE — SOIE → VÊTEMENTS
# ──────────────────────────────────────────────

METIERS = {
    1: {
        "nom":              "Rouet à bras",
        "emoji":            "🪡",
        "cout":             100,
        "soie_par_vetement": 3,
        "capacite_jour":    2,
        "entretien":        3,
        "desc":             "Simple et lent. Produit des vetements basiques.",
    },
    2: {
        "nom":              "Metier a tisser",
        "emoji":            "🧶",
        "cout":             300,
        "soie_par_vetement": 2,
        "capacite_jour":    5,
        "entretien":        8,
        "desc":             "Bon rendement. Vetements de qualite courante.",
    },
    3: {
        "nom":              "Manufacture royale",
        "emoji":            "🏭",
        "cout":             700,
        "soie_par_vetement": 1,
        "capacite_jour":    12,
        "entretien":        18,
        "desc":             "Elite. Produit des vetements de luxe en serie.",
    },
}

VETEMENTS_PRIX_BASE = 55  # bien supérieur à la soie (25 €)

tisserand = {
    "actif":      False,
    "niveau":     0,
    "salaire":    0,
    "nom":        None,
    "efficacite": 0.0,
    "moral": 100, "jours_travailles": 0, "salaires_impaye": 0,
}

metier_a_tisser = {
    "possede":           False,
    "niveau":            0,
    "nom":               None,
    "emoji":             "",
    "soie_par_vetement": 0,
    "capacite_jour":     0,
    "entretien":         0,
    "usure":             0,
    "usure_max":         USURE_MAX_METIER,
    "en_panne":          False,
}

stock_vetements           = 0
prix_vetements            = VETEMENTS_PRIX_BASE
vetements_produits_total  = 0
offre_demande_vetements   = {"offre": 100, "demande": 100}

# ──────────────────────────────────────────────
#  SYSTEME ORFEVRERIE — OR → BIJOUX → ENCHERES
# ──────────────────────────────────────────────

ATELIERS_OR = {
    1: {
        "nom":             "Etabli d'artisan",
        "emoji":           "🔨",
        "cout":            150,
        "or_par_bijou":    2,
        "capacite_jour":   1,
        "entretien":       4,
        "qualite_min":     1,
        "qualite_max":     3,
        "desc":            "Produit des bijoux simples. Qualite variable.",
    },
    2: {
        "nom":             "Forge du joaillier",
        "emoji":           "⚒",
        "cout":            400,
        "or_par_bijou":    1,
        "capacite_jour":   3,
        "entretien":       10,
        "qualite_min":     2,
        "qualite_max":     4,
        "desc":            "Bonne qualite, rendement correct.",
    },
    3: {
        "nom":             "Atelier du maitre",
        "emoji":           "💎",
        "cout":            900,
        "or_par_bijou":    1,
        "capacite_jour":   5,
        "entretien":       22,
        "qualite_min":     3,
        "qualite_max":     5,
        "desc":            "Chef-d'oeuvres garantis. Tres rentable aux encheres.",
    },
}

NOMS_BIJOUX = [
    "Collier d'or", "Bracelet cisele", "Bague gravee", "Pendentif royal",
    "Broche doree", "Diademe fin", "Chevaliere", "Medallion",
    "Boucles d'oreilles", "Fibule ouvragee",
]

BIJOU_PRIX_BASE = {1: 120, 2: 200, 3: 320, 4: 500, 5: 800}
QUALITE_NOMS    = {1: "⚪ Commun", 2: "🟢 Bon", 3: "🔵 Rare", 4: "🟣 Precieux", 5: "🟡 Legendaire"}

orfèvre = {
    "actif":      False,
    "niveau":     0,
    "salaire":    0,
    "nom":        None,
    "talent":     0.0,
    "moral": 100, "jours_travailles": 0, "salaires_impaye": 0,
}

atelier_or = {
    "possede":       False,
    "niveau":        0,
    "nom":           None,
    "emoji":         "",
    "or_par_bijou":  0,
    "capacite_jour": 0,
    "entretien":     0,
    "qualite_min":   0,
    "qualite_max":   0,
    "usure":         0,
    "usure_max":     USURE_MAX_ATELIER_OR,
    "en_panne":      False,
}

# Stock bijoux = liste de dicts {"qualite": N, "nom": str}
stock_bijoux          = []
bijoux_produits_total = 0


# ──────────────────────────────────────────────
#  ÉTAT DU JEU
# ──────────────────────────────────────────────
argent          = ARGENT_DEPART
stock           = {}
prix_actuels    = {}
offre_demande   = {}
jour            = 1
historique      = []
evenement_actif = None


# ──────────────────────────────────────────────
#  FONCTIONS UTILITAIRES D'AFFICHAGE
# ──────────────────────────────────────────────

def effacer():
    os.system("cls" if os.name == "nt" else "clear")


def pause(secondes=0.03):
    time.sleep(secondes)


def taper(texte, delai=0.012):
    for c in texte:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(delai)
    print()


def ligne(caractere="─", largeur=64, couleur=C.GRIS):
    print(f"{couleur}{caractere * largeur}{C.RESET}")


def titre_bloc(texte, couleur=C.CYAN):
    largeur = 64
    print(f"{couleur}╔{'═' * (largeur - 2)}╗{C.RESET}")
    texte_centre = texte.center(largeur - 2)
    print(f"{couleur}║{C.BOLD}{C.BLANC}{texte_centre}{C.RESET}{couleur}║{C.RESET}")
    print(f"{couleur}╚{'═' * (largeur - 2)}╝{C.RESET}")


def barre_progression(valeur, maximum, largeur=20, couleur=C.VERT):
    rempli = int((valeur / maximum) * largeur) if maximum > 0 else 0
    rempli = min(rempli, largeur)
    vide = largeur - rempli
    pourcent = int((valeur / maximum) * 100) if maximum > 0 else 0
    barre = f"{couleur}{'█' * rempli}{C.DIM}{'░' * vide}{C.RESET}"
    return f"[{barre}] {pourcent:3d}%"


def badge(texte, couleur_fond=C.FOND_BLEU):
    return f"{couleur_fond}{C.BLANC}{C.BOLD} {texte} {C.RESET}"


# ──────────────────────────────────────────────
#  LOGIQUE DE JEU
# ──────────────────────────────────────────────

def initialiser_prix():
    """Initialise les prix, le stock et l'offre/demande."""
    global prix_actuels, offre_demande

    for cle, prod in PRODUITS.items():
        prix_actuels[cle] = prod["prix_base"]
        stock[cle] = 0

        # 100 = marché équilibré
        offre_demande[cle] = {
            "offre": 100,
            "demande": 100
        }


def limiter(valeur, minimum=20, maximum=180):
    """Empêche une valeur de sortir d'un intervalle."""
    return max(minimum, min(maximum, valeur))


def facteur_offre_demande(cle):
    """
    Calcule un multiplicateur selon l'offre et la demande.

    Si demande > offre : le prix augmente.
    Si offre > demande : le prix baisse.
    """
    offre = offre_demande[cle]["offre"]
    demande = offre_demande[cle]["demande"]

    ratio = demande / offre

    # Effet assez visible, mais contrôlé
    facteur = 1 + (ratio - 1) * 0.45

    return max(0.65, min(1.75, facteur))


def tendance_marche(cle):
    """Retourne l'état du marché pour un produit."""
    offre = offre_demande[cle]["offre"]
    demande = offre_demande[cle]["demande"]

    if demande >= offre + 35:
        return f"{C.VERT}Demande +{C.RESET}"
    elif offre >= demande + 35:
        return f"{C.ROUGE}Offre +{C.RESET}"
    else:
        return f"{C.GRIS}Stable{C.RESET}"


def actualiser_offre_demande(evenement=None):
    """
    Met à jour l'offre et la demande chaque jour.
    Chaque ressource évolue différemment.
    Intègre les effets saisonniers.
    """
    saison = get_saison()

    for cle in PRODUITS:
        variation_offre   = random.randint(-10, 10)
        variation_demande = random.randint(-10, 10)

        # Effet saisonnier (appliqué une fois par jour, atténué)
        mod = saison["modificateurs"].get(cle, {"offre": 0, "demande": 0})
        variation_offre   += mod["offre"]   // 3
        variation_demande += mod["demande"] // 3

        offre_demande[cle]["offre"]   = limiter(offre_demande[cle]["offre"]   + variation_offre)
        offre_demande[cle]["demande"] = limiter(offre_demande[cle]["demande"] + variation_demande)

    # ── Concurrents PNJ : leurs achats/ventes impactent le marché ────────────
    for conc in concurrents:
        if conc["capital"] <= 0:
            continue
        style = conc["style"]
        for cle in PRODUITS:
            prix  = prix_actuels[cle]
            base  = PRODUITS[cle]["prix_base"]
            if style == "prudent":
                # Achète si -15% du prix de base, vend si +15%
                if prix <= base * 0.85 and conc["capital"] >= prix:
                    conc["capital"] -= prix
                    offre_demande[cle]["demande"] = limiter(offre_demande[cle]["demande"] + 3)
                elif prix >= base * 1.15:
                    conc["capital"] += prix
                    offre_demande[cle]["offre"]   = limiter(offre_demande[cle]["offre"]   + 3)
            elif style == "agressif":
                # Achète agressivement, influence plus fort
                if prix <= base * 0.92 and conc["capital"] >= prix:
                    conc["capital"] -= prix
                    offre_demande[cle]["demande"] = limiter(offre_demande[cle]["demande"] + 6)
                elif prix >= base * 1.08:
                    conc["capital"] += prix
                    offre_demande[cle]["offre"]   = limiter(offre_demande[cle]["offre"]   + 6)
            elif style == "speculateur":
                # Mise sur les tendances : achète si demande forte
                od = offre_demande[cle]
                if od["demande"] > od["offre"] + 20 and conc["capital"] >= prix:
                    conc["capital"] -= prix
                    offre_demande[cle]["demande"] = limiter(offre_demande[cle]["demande"] + 5)
                elif od["offre"] > od["demande"] + 20:
                    conc["capital"] += prix
                    offre_demande[cle]["offre"]   = limiter(offre_demande[cle]["offre"]   + 5)

    if evenement is None:
        return

    cible = evenement["cible"]

    if cible is not None:
        if cible in offre_demande:
            if evenement["mult"] > 1:
                offre_demande[cible]["demande"] = limiter(offre_demande[cible]["demande"] + 25)
                offre_demande[cible]["offre"]   = limiter(offre_demande[cible]["offre"]   - 15)
            elif evenement["mult"] < 1:
                offre_demande[cible]["offre"]   = limiter(offre_demande[cible]["offre"]   + 25)
                offre_demande[cible]["demande"] = limiter(offre_demande[cible]["demande"] - 15)

    if evenement["perte_stock"] > 0:
        for cle in PRODUITS:
            offre_demande[cle]["offre"] = limiter(offre_demande[cle]["offre"] - 20)


def modifier_marche_apres_transaction(cle, type_action, quantite):
    """
    Modifie l'offre/demande après une action du joueur.

    Acheter :
    - la demande augmente
    - l'offre baisse

    Vendre :
    - l'offre augmente
    - la demande baisse un peu
    """
    if type_action == "achat":
        offre_demande[cle]["demande"] = limiter(offre_demande[cle]["demande"] + quantite * 2)
        offre_demande[cle]["offre"] = limiter(offre_demande[cle]["offre"] - quantite)

    elif type_action == "vente":
        offre_demande[cle]["offre"] = limiter(offre_demande[cle]["offre"] + quantite * 2)
        offre_demande[cle]["demande"] = limiter(offre_demande[cle]["demande"] - quantite)


def calculer_nouveau_prix(cle, multiplicateur=1.0):
    """
    Calcule un nouveau prix avec :
    - volatilité du produit
    - difficulté progressive
    - événement
    - offre et demande dynamique
    """
    prod = PRODUITS[cle]
    base = prod["prix_base"]
    vol = prod["volatilite"]

    facteur_difficulte = 1 + (jour / JOURS_MAX) * 0.5
    variation = random.uniform(-vol * facteur_difficulte, vol * facteur_difficulte)

    facteur_marche = facteur_offre_demande(cle)

    nouveau = base * (1 + variation) * multiplicateur * facteur_marche

    return max(1, round(nouveau))


def mettre_a_jour_prix(evenement=None):
    """Met à jour les prix de tous les produits."""
    mult_global = evenement["mult"] if evenement else 1.0
    cible_event = evenement["cible"] if evenement else None

    for cle in PRODUITS:
        mult = mult_global if cle == cible_event else 1.0
        prix_actuels[cle] = calculer_nouveau_prix(cle, mult)


def tirer_evenement():
    return random.choice(EVENEMENTS)


def stock_total():
    return sum(stock.values())


def valeur_stock():
    """Valeur des marchandises du marché uniquement (farine exclue)."""
    return sum(stock[cle] * prix_actuels[cle] for cle in stock)


def valeur_farine():
    """Valeur séparée du stock de farine."""
    return stock_farine * prix_farine


def patrimoine_total():
    """Argent + stock marchand uniquement (farine non comptée ici)."""
    return argent + valeur_stock()


def variation_prix(cle):
    base = PRODUITS[cle]["prix_base"]
    prix = prix_actuels[cle]
    pct = ((prix - base) / base) * 100
    return pct


def fleche_variation(pct):
    if pct > 10:
        return f"{C.VERT}▲{C.RESET}"
    elif pct < -10:
        return f"{C.ROUGE}▼{C.RESET}"
    else:
        return f"{C.GRIS}─{C.RESET}"


def config_employe(niveau):
    if niveau == 1:
        return {"cout": 120, "salaire": 6, "fiabilite": 0.55, "nom": "Apprenti négociant"}
    elif niveau == 2:
        return {"cout": 280, "salaire": 15, "fiabilite": 0.72, "nom": "Commerçant expérimenté"}
    elif niveau == 3:
        return {"cout": 600, "salaire": 30, "fiabilite": 0.88, "nom": "Maître du marché"}
    return None


def embaucher_employe():
    global argent, employe

    effacer()
    titre_bloc("  EMBAUCHE D'UN EMPLOYÉ  ", C.MAGENTA)

    # Déjà un employé actif
    if employe["actif"]:
        print(f"\n  {C.JAUNE}⚠  Tu as déjà un employé en poste :{C.RESET}")
        print(f"  {C.BOLD}{employe['nom']}{C.RESET} "
              f"(fiabilité {C.CYAN}{int(employe['fiabilite']*100)}%{C.RESET}, "
              f"salaire {C.ROUGE}{employe['salaire']} €/jour{C.RESET})")
        print(f"\n  {C.GRIS}Licencie-le d'abord avec [L] avant d'en recruter un autre.{C.RESET}")
        input(f"\n  {C.GRIS}[ENTRÉE] pour revenir{C.RESET}")
        return

    # Tableau des profils disponibles
    print(f"\n  {C.BOLD}Profils disponibles :{C.RESET}")
    ligne("─", 64, C.GRIS)

    profils = [
        (1, "🔰", C.VERT),
        (2, "⚔️ ", C.JAUNE),
        (3, "👑", C.MAGENTA),
    ]

    for niveau, icone, couleur in profils:
        cfg = config_employe(niveau)
        fiabilite_barre = barre_progression(int(cfg["fiabilite"] * 100), 100, 12, couleur)
        print(
            f"\n  {couleur}{C.BOLD}[{niveau}] {icone} {cfg['nom']}{C.RESET}\n"
            f"      Coût d'embauche : {C.JAUNE}{cfg['cout']} €{C.RESET}  │  "
            f"Salaire : {C.ROUGE}{cfg['salaire']} €/jour{C.RESET}  │  "
            f"Fiabilité : {fiabilite_barre}"
        )

    ligne("─", 64, C.GRIS)
    print(f"  {C.GRIS}[0]{C.RESET} Annuler")
    print(f"\n  {C.BOLD}Ton choix : {C.RESET}", end="")

    try:
        niveau = int(input())
    except ValueError:
        print(f"\n  {C.ROUGE}Valeur invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    if niveau == 0:
        return

    cfg = config_employe(niveau)
    if cfg is None:
        print(f"\n  {C.ROUGE}Niveau invalide. Choisis 1, 2 ou 3.{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    if argent < cfg["cout"]:
        print(f"\n  {C.ROUGE}✖  Fonds insuffisants !{C.RESET} "
              f"Il te faut {C.JAUNE}{cfg['cout']} €{C.RESET}, "
              f"tu as {C.ROUGE}{argent} €{C.RESET}.")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    # Confirmation
    print(f"\n  Confirmer l'embauche de {C.BOLD}{cfg['nom']}{C.RESET} "
          f"pour {C.JAUNE}{cfg['cout']} €{C.RESET} ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        print(f"  {C.GRIS}Embauche annulée.{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    argent -= cfg["cout"]
    employe["actif"] = True
    employe["niveau"] = niveau
    employe["salaire"] = cfg["salaire"]
    employe["cout_embauche"] = cfg["cout"]
    employe["nom"] = cfg["nom"]
    employe["fiabilite"] = cfg["fiabilite"]

    historique.append((jour, f"Embauche {cfg['nom']}", -cfg["cout"]))

    print(f"\n  {C.VERT}✔  {cfg['nom']} rejoint ton équipe !{C.RESET}")
    print(f"  {C.GRIS}Il agira automatiquement à chaque fin de journée.{C.RESET}")
    input(f"\n  {C.GRIS}[ENTRÉE]{C.RESET}")


def licencier_employe():
    global employe

    effacer()
    titre_bloc("  LICENCIEMENT  ", C.ROUGE)

    if not employe["actif"]:
        print(f"\n  {C.GRIS}Tu n'as aucun employé en poste.{C.RESET}")
        input(f"\n  {C.GRIS}[ENTRÉE] pour revenir{C.RESET}")
        return

    print(f"\n  {C.BOLD}Employé actuel :{C.RESET} {employe['nom']}")
    print(f"  Salaire économisé dès demain : {C.VERT}+{employe['salaire']} €/jour{C.RESET}")
    print(f"\n  {C.ROUGE}Confirmer le licenciement ? (o/n) : {C.RESET}", end="")

    if input().strip().lower() != "o":
        print(f"  {C.GRIS}Licenciement annulé.{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    nom = employe["nom"]
    employe["actif"] = False
    employe["niveau"] = 0
    employe["salaire"] = 0
    employe["cout_embauche"] = 0
    employe["nom"] = None
    employe["fiabilite"] = 0.0

    print(f"\n  {C.JAUNE}✔  {nom} a été licencié.{C.RESET}")
    input(f"\n  {C.GRIS}[ENTRÉE]{C.RESET}")


def payer_employe():
    global argent
    if employe["actif"]:
        argent = max(0, argent - employe["salaire"])
        historique.append((jour, f"Salaire {employe['nom']}", -employe["salaire"]))


def moyenne_prix_historique(cle, n=3):
    prixs = [p for j, action, montant in historique if cle in action]
    if len(prixs) == 0:
        return prix_actuels[cle]
    return sum(prixs[-n:]) / min(n, len(prixs))

# ──────────────────────────────────────────────
# AUTOMATIQUE
# ──────────────────────────────────────────────


def score_opportunite_achat(cle):
    """
    Calcule un score d'opportunité d'achat pour un produit (plus c'est élevé, mieux c'est).
    Prend en compte : rabais vs base, tendance offre/demande, jours restants.
    """
    prix  = prix_actuels[cle]
    base  = PRODUITS[cle]["prix_base"]
    offre = offre_demande[cle]["offre"]
    dem   = offre_demande[cle]["demande"]

    # Rabais par rapport au prix de base (positif = bon marché)
    rabais = (base - prix) / base  # ex: 0.20 si 20% sous le prix de base

    # Signal offre/demande : demande forte = prix va monter → bon moment d'acheter
    signal_od = (dem - offre) / 100  # positif si demande > offre

    # Urgence temporelle : plus on approche de la fin, moins on veut stocker
    jours_restants = JOURS_MAX - jour
    penalite_temps = max(0, (10 - jours_restants) / 10) * 0.3  # pénalise l'achat en fin de partie

    return rabais + signal_od * 0.5 - penalite_temps


def score_opportunite_vente(cle):
    """
    Calcule un score d'opportunité de vente (plus c'est élevé, mieux c'est).
    """
    prix  = prix_actuels[cle]
    base  = PRODUITS[cle]["prix_base"]
    offre = offre_demande[cle]["offre"]
    dem   = offre_demande[cle]["demande"]

    # Prime par rapport au prix de base
    prime = (prix - base) / base

    # Signal offre/demande : offre forte = prix va baisser → bon moment de vendre
    signal_od = (offre - dem) / 100

    # Urgence temporelle : en fin de partie, vendre le stock devient prioritaire
    jours_restants = JOURS_MAX - jour
    bonus_temps = max(0, (10 - jours_restants) / 10) * 0.4

    return prime + signal_od * 0.5 + bonus_temps


def action_employe():
    global argent

    if not employe["actif"]:
        return

    niveau   = employe["niveau"]
    fiab     = employe["fiabilite"]
    nom      = employe["nom"]

    # ── NIVEAU 1 : Apprenti — logique simple + erreurs aléatoires ─────────────
    if niveau == 1:
        for cle in PRODUITS:
            prix = prix_actuels[cle]
            base = PRODUITS[cle]["prix_base"]

            # Chance d'ignorer une opportunité (manque d'expérience)
            if random.random() > fiab:
                continue

            if prix <= base * 0.88:
                if argent >= prix and stock_total() < LIMITE_STOCK:
                    stock[cle] += 1
                    argent -= prix
                    modifier_marche_apres_transaction(cle, "achat", 1)
                    historique.append((jour, f"{nom} achète {PRODUITS[cle]['nom']}", -prix))

            elif prix >= base * 1.15 and stock[cle] > 0:
                stock[cle] -= 1
                argent += prix
                modifier_marche_apres_transaction(cle, "vente", 1)
                historique.append((jour, f"{nom} vend {PRODUITS[cle]['nom']}", prix))

    # ── NIVEAU 2 : Expérimenté — croise prix ET offre/demande ────────────────
    elif niveau == 2:
        # Trie les produits par opportunité décroissante avant d'agir
        candidats_achat = sorted(
            PRODUITS.keys(),
            key=lambda c: score_opportunite_achat(c),
            reverse=True
        )
        candidats_vente = sorted(
            PRODUITS.keys(),
            key=lambda c: score_opportunite_vente(c),
            reverse=True
        )

        # Ventes d'abord (libère de l'argent)
        for cle in candidats_vente:
            if stock[cle] <= 0:
                continue
            score = score_opportunite_vente(cle)
            if score >= 0.10:  # seuil : au moins 10% de prime ou signal positif
                qte = min(stock[cle], 2)  # vend jusqu'à 2 unités par tour
                stock[cle] -= qte
                argent += prix_actuels[cle] * qte
                modifier_marche_apres_transaction(cle, "vente", qte)
                historique.append((jour, f"{nom} vend {PRODUITS[cle]['nom']} x{qte}", prix_actuels[cle] * qte))

        # Achats ensuite
        for cle in candidats_achat:
            score = score_opportunite_achat(cle)
            prix  = prix_actuels[cle]
            if score >= 0.08 and argent >= prix and stock_total() < LIMITE_STOCK:
                stock[cle] += 1
                argent -= prix
                modifier_marche_apres_transaction(cle, "achat", 1)
                historique.append((jour, f"{nom} achète {PRODUITS[cle]['nom']}", -prix))

    # ── NIVEAU 3 : Maître — stratège complet ──────────────────────────────────
    elif niveau == 3:
        jours_restants = JOURS_MAX - jour

        # --- Phase VENTE : priorité aux meilleures opportunités ---
        candidats_vente = sorted(
            [c for c in PRODUITS if stock[c] > 0],
            key=lambda c: score_opportunite_vente(c),
            reverse=True
        )

        for cle in candidats_vente:
            score = score_opportunite_vente(cle)
            prix  = prix_actuels[cle]
            base  = PRODUITS[cle]["prix_base"]

            # En fin de partie : liquider tout le stock même à prix neutre
            if jours_restants <= 5:
                seuil_vente = -0.05
            else:
                seuil_vente = 0.08

            if score >= seuil_vente and stock[cle] > 0:
                # Vend plus agressivement en fin de partie
                qte_max = stock[cle] if jours_restants <= 5 else min(stock[cle], 3)
                qte = qte_max
                stock[cle] -= qte
                gain = prix * qte
                argent += gain
                modifier_marche_apres_transaction(cle, "vente", qte)
                historique.append((jour, f"{nom} vend {PRODUITS[cle]['nom']} x{qte}", gain))

        # --- Phase ACHAT : uniquement si opportunité nette et temps suffisant ---
        if jours_restants > 4:  # n'achète pas en toute fin de partie
            candidats_achat = sorted(
                PRODUITS.keys(),
                key=lambda c: score_opportunite_achat(c),
                reverse=True
            )

            espace_dispo = LIMITE_STOCK - stock_total()
            budget_reserve = max(0, argent - employe["salaire"] * 3)  # garde 3j de salaire

            for cle in candidats_achat:
                if espace_dispo <= 0 or budget_reserve <= 0:
                    break

                score = score_opportunite_achat(cle)
                prix  = prix_actuels[cle]

                if score < 0.12:  # seuil plus sélectif que niveau 2
                    continue

                # Achète jusqu'à 3 unités si l'opportunité est excellente
                qte_possible = min(
                    int(budget_reserve // prix),
                    espace_dispo,
                    3 if score >= 0.25 else 1
                )

                if qte_possible <= 0:
                    continue

                cout = prix * qte_possible
                stock[cle] += qte_possible
                argent -= cout
                budget_reserve -= cout
                espace_dispo -= qte_possible
                modifier_marche_apres_transaction(cle, "achat", qte_possible)
                historique.append((jour, f"{nom} achète {PRODUITS[cle]['nom']} x{qte_possible}", -cout))
            

# ──────────────────────────────────────────────
#  MORAL, ÉVOLUTION EMPLOYÉS ET USURE MACHINES
# ──────────────────────────────────────────────

def _efficacite_avec_moral(efficacite_base, moral):
    """Modifie l'efficacité réelle selon le moral (0-100)."""
    if moral >= 80:
        return min(1.0, efficacite_base * 1.1)
    elif moral >= 50:
        return efficacite_base
    elif moral >= 25:
        return efficacite_base * 0.75
    else:
        return efficacite_base * 0.50


def payer_employe():
    global argent
    if not employe["actif"]:
        return

    if argent >= employe["salaire"]:
        argent -= employe["salaire"]
        historique.append((jour, f"Salaire {employe['nom']}", -employe["salaire"]))
        employe["salaires_impaye"] = 0
        # Prime de moral si payé à l'heure
        employe["moral"] = min(100, employe["moral"] + 2)
    else:
        # Pas assez d'argent : moral baisse
        employe["salaires_impaye"] += 1
        employe["moral"] = max(0, employe["moral"] - 15)
        historique.append((jour, f"Salaire impayé {employe['nom']}", 0))

    employe["jours_travailles"] += 1
    _verifier_evolution_employe()


def _verifier_evolution_employe():
    """Propose l'évolution de carrière si l'employé a assez travaillé."""
    global employe
    niv = employe["niveau"]
    seuil = {1: 8, 2: 12}  # jours nécessaires pour monter de niveau
    if niv < 3 and employe["jours_travailles"] >= seuil.get(niv, 999):
        cfg_actuel  = config_employe(niv)
        cfg_suivant = config_employe(niv + 1)
        cout_reduit = cfg_suivant["cout"] // 2
        print(
            f"\n  {C.JAUNE}⭐ {employe['nom']} est pret a evoluer !{C.RESET}\n"
            f"  Passage a {C.BOLD}{cfg_suivant['nom']}{C.RESET} "
            f"pour seulement {C.VERT}{cout_reduit} €{C.RESET} "
            f"(au lieu de {cfg_suivant['cout']} €).\n"
            f"  Accepter ? (o/n) : ", end=""
        )
        if input().strip().lower() == "o":
            if argent >= cout_reduit:
                argent -= cout_reduit
                employe["niveau"]         = niv + 1
                employe["salaire"]        = cfg_suivant["salaire"]
                employe["nom"]            = cfg_suivant["nom"]
                employe["fiabilite"]      = cfg_suivant["fiabilite"]
                employe["jours_travailles"] = 0
                employe["moral"]          = min(100, employe["moral"] + 20)
                historique.append((jour, f"Evolution {cfg_suivant['nom']}", -cout_reduit))
                print(f"  {C.VERT}✔  Evolution reussie !{C.RESET}")
            else:
                print(f"  {C.ROUGE}Fonds insuffisants.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")


def _verifier_evolution_specialiste(specialiste, config_fn, nom_metier):
    """Vérifie et propose l'évolution pour meunier/tisserand/etc."""
    niv = specialiste["niveau"]
    seuil = {1: 7, 2: 10}
    if niv < 3 and specialiste.get("jours_travailles", 0) >= seuil.get(niv, 999):
        cfg_suivant = config_fn(niv + 1)
        cout_reduit = cfg_suivant["cout"] // 2
        print(
            f"\n  {C.JAUNE}⭐ {specialiste['nom']} est pret a evoluer !{C.RESET}\n"
            f"  Passage a {C.BOLD}{cfg_suivant['nom']}{C.RESET} pour {C.VERT}{cout_reduit} €{C.RESET}.\n"
            f"  Accepter ? (o/n) : ", end=""
        )
        if input().strip().lower() == "o":
            global argent
            if argent >= cout_reduit:
                argent -= cout_reduit
                specialiste["niveau"]          = niv + 1
                specialiste["salaire"]         = cfg_suivant["salaire"]
                specialiste["nom"]             = cfg_suivant["nom"]
                specialiste["efficacite"]      = cfg_suivant.get("efficacite", cfg_suivant.get("talent", 0))
                specialiste["jours_travailles"] = 0
                specialiste["moral"]           = min(100, specialiste.get("moral", 80) + 20)
                historique.append((jour, f"Evolution {cfg_suivant['nom']}", -cout_reduit))
                print(f"  {C.VERT}✔  Evolution reussie !{C.RESET}")
            else:
                print(f"  {C.ROUGE}Fonds insuffisants.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")


def _payer_specialiste(specialiste, label):
    global argent
    if not specialiste["actif"]:
        return
    if argent >= specialiste["salaire"]:
        argent -= specialiste["salaire"]
        historique.append((jour, f"Salaire {specialiste['nom']}", -specialiste["salaire"]))
        specialiste["salaires_impaye"] = 0
        specialiste["moral"] = min(100, specialiste.get("moral", 80) + 2)
    else:
        specialiste["salaires_impaye"] = specialiste.get("salaires_impaye", 0) + 1
        specialiste["moral"] = max(0, specialiste.get("moral", 80) - 15)
        historique.append((jour, f"Salaire impayé {specialiste['nom']}", 0))
    specialiste["jours_travailles"] = specialiste.get("jours_travailles", 0) + 1


def _appliquer_usure(machine_dict, usure_max, label):
    """Applique 1 point d'usure par jour de production. Panne si max atteint."""
    if not machine_dict.get("possede", False) or machine_dict.get("en_panne", False):
        return
    machine_dict["usure"] = machine_dict.get("usure", 0) + 1
    if machine_dict["usure"] >= machine_dict.get("usure_max", usure_max):
        machine_dict["en_panne"] = True
        print(f"\n  {C.ROUGE}⚠  {machine_dict['nom']} est tombé en panne ! Répare-le dans son menu.{C.RESET}")


def action_reparer_machine(machine_dict, constantes_dict):
    """Répare une machine en panne moyennant un coût."""
    global argent
    if not machine_dict.get("en_panne", False):
        print(f"  {C.GRIS}La machine est en bon état.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    cout_reparation = constantes_dict[machine_dict["niveau"]]["cout"] // 4
    print(
        f"\n  {C.ROUGE}Machine en panne !{C.RESET}  Coût de réparation : {C.JAUNE}{cout_reparation} €{C.RESET}\n"
        f"  Confirmer ? (o/n) : ", end=""
    )
    if input().strip().lower() != "o":
        return
    if argent < cout_reparation:
        print(f"  {C.ROUGE}Fonds insuffisants.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    argent -= cout_reparation
    machine_dict["en_panne"] = False
    machine_dict["usure"]    = 0
    historique.append((jour, f"Reparation {machine_dict['nom']}", -cout_reparation))
    print(f"\n  {C.VERT}✔  {machine_dict['nom']} réparée !{C.RESET}")
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


def action_ameliorer_machine(machine_dict, constantes_dict):
    """Upgrade une machine existante vers le niveau supérieur."""
    global argent
    niv = machine_dict.get("niveau", 0)
    if niv >= 3:
        print(f"  {C.GRIS}Déjà au niveau maximum.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    suivant = constantes_dict.get(niv + 1)
    if not suivant:
        return
    cout = suivant["cout"] - constantes_dict[niv]["cout"] // 2
    cout = max(50, cout)
    print(
        f"\n  Améliorer vers {C.BOLD}{suivant['nom']}{C.RESET} "
        f"pour {C.JAUNE}{cout} €{C.RESET} ? (o/n) : ", end=""
    )
    if input().strip().lower() != "o":
        return
    if argent < cout:
        print(f"  {C.ROUGE}Fonds insuffisants.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    argent -= cout
    machine_dict.update({
        "niveau":  niv + 1,
        "nom":     suivant["nom"],
        "emoji":   suivant["emoji"],
        "entretien": suivant["entretien"],
        "usure":   0,
        "en_panne": False,
    })
    # Mise à jour des clés spécifiques à chaque type
    for cle in ("ble_par_farine", "capacite_jour", "soie_par_vetement",
                 "epices_par_tissu", "soie_par_tissu", "poisson_par_boite",
                 "sel_par_boite", "or_par_bijou", "qualite_min", "qualite_max"):
        if cle in suivant:
            machine_dict[cle] = suivant[cle]
    historique.append((jour, f"Amelioration {machine_dict['nom']}", -cout))
    print(f"\n  {C.VERT}✔  Machine améliorée : {suivant['nom']} !{C.RESET}")
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


# ──────────────────────────────────────────────
#  CONSERVES (POISSON + SEL → CONSERVES)
# ──────────────────────────────────────────────

def config_conserveur(niveau):
    if niveau == 1:
        return {"salaire": 7,  "efficacite": 0.60, "nom": "Aide-conserveur",  "cout": 45}
    elif niveau == 2:
        return {"salaire": 16, "efficacite": 0.80, "nom": "Conserveur",       "cout": 140}
    elif niveau == 3:
        return {"salaire": 30, "efficacite": 1.00, "nom": "Maitre conserveur","cout": 320}
    return None


def mettre_a_jour_prix_conserves():
    global prix_conserves, offre_demande_conserves
    offre_demande_conserves["offre"]   = limiter(offre_demande_conserves["offre"]   + random.randint(-7, 7))
    offre_demande_conserves["demande"] = limiter(offre_demande_conserves["demande"] + random.randint(-5, 9))
    offre_poisson = offre_demande.get("poisson", {}).get("offre", 100)
    if offre_poisson < 60:
        offre_demande_conserves["offre"]   = limiter(offre_demande_conserves["offre"]   - 10)
        offre_demande_conserves["demande"] = limiter(offre_demande_conserves["demande"] + 8)
    offre   = offre_demande_conserves["offre"]
    demande = offre_demande_conserves["demande"]
    facteur = max(0.65, min(1.75, 1 + (demande/offre - 1) * 0.45))
    prix_conserves = max(12, round(CONSERVES_PRIX_BASE * facteur))


def produire_conserves(quantite_voulue):
    global stock_conserves, conserves_produites_total
    if not conserverie["possede"] or conserverie["en_panne"]:
        return 0, "Conserverie indisponible."
    poisson_dispo = stock.get("poisson", 0)
    sel_dispo     = stock.get("sel", 0)
    p_par_b = conserverie["poisson_par_boite"]
    s_par_b = conserverie["sel_par_boite"]
    max_prod = min(quantite_voulue, conserverie["capacite_jour"],
                   poisson_dispo // p_par_b, sel_dispo // s_par_b)
    if max_prod <= 0:
        return 0, f"Manque de poisson ({p_par_b}/boite) ou sel ({s_par_b}/boite)."
    stock["poisson"]     -= max_prod * p_par_b
    stock["sel"]         -= max_prod * s_par_b
    stock_conserves      += max_prod
    conserves_produites_total += max_prod
    _appliquer_usure(conserverie, 40, "conserverie")
    return max_prod, f"{max_prod} boite(s) produites ({max_prod*p_par_b} poisson, {max_prod*s_par_b} sel)."


def payer_conserveur_et_conserverie():
    _payer_specialiste(conserveur, "conserveur")
    if conserverie["possede"] and not conserverie["en_panne"]:
        global argent
        argent = max(0, argent - conserverie["entretien"])
        historique.append((jour, f"Entretien {conserverie['nom']}", -conserverie["entretien"]))
    if conserveur["actif"]:
        _verifier_evolution_specialiste(conserveur, config_conserveur, "conserveur")


def action_conserveur_auto():
    if not conserveur["actif"] or not conserverie["possede"] or conserverie["en_panne"]:
        return
    moral = conserveur.get("moral", 80)
    eff   = _efficacite_avec_moral(conserveur["efficacite"], moral)
    cap   = int(conserverie["capacite_jour"] * eff)
    produit, _ = produire_conserves(cap)
    if produit > 0:
        historique.append((jour, f"{conserveur['nom']} conserve x{produit}", 0))


def action_atelier_conserves():
    while True:
        effacer()
        titre_bloc("  CONSERVERIE — POISSON + SEL  ", C.CYAN)

        print(f"\n  {C.BOLD}Conserverie :{C.RESET} ", end="")
        if conserverie["possede"]:
            etat = f"{C.ROUGE}EN PANNE{C.RESET}" if conserverie["en_panne"] else f"{C.VERT}OK{C.RESET}"
            print(
                f"{conserverie['emoji']} {C.BOLD}{conserverie['nom']}{C.RESET}  {etat}  │  "
                f"Usure : {conserverie['usure']}/{conserverie['usure_max']}  │  "
                f"Entretien : {C.ROUGE}{conserverie['entretien']} €/j{C.RESET}"
            )
        else:
            print(f"{C.GRIS}Aucune{C.RESET}")

        print(f"  {C.BOLD}Conserveur :{C.RESET} ", end="")
        if conserveur["actif"]:
            moral_barre = barre_progression(conserveur.get("moral", 80), 100, 10,
                                            C.VERT if conserveur.get("moral",80) >= 50 else C.ROUGE)
            print(
                f"{C.BOLD}{conserveur['nom']}{C.RESET}  │  "
                f"Moral : {moral_barre}  │  "
                f"Salaire : {C.ROUGE}{conserveur['salaire']} €/j{C.RESET}  │  "
                f"Exp : {conserveur.get('jours_travailles',0)}j"
            )
        else:
            print(f"{C.GRIS}Aucun{C.RESET}")

        print(
            f"\n  🐟 Poisson : {C.JAUNE}{stock.get('poisson',0)}{C.RESET}  │  "
            f"🧂 Sel : {C.JAUNE}{stock.get('sel',0)}{C.RESET}  │  "
            f"🥫 Conserves : {C.JAUNE}{stock_conserves}{C.RESET}  │  "
            f"Prix : {C.VERT}{prix_conserves} €{C.RESET}"
        )
        ligne("─", 64, C.GRIS)
        print(f"  {C.CYAN}[1]{C.RESET}  Acheter une conserverie")
        print(f"  {C.JAUNE}[2]{C.RESET}  Améliorer la conserverie")
        print(f"  {C.ROUGE}[3]{C.RESET}  Vendre la conserverie")
        print(f"  {C.ROUGE}[4]{C.RESET}  Réparer la conserverie")
        print(f"  {C.VERT}[5]{C.RESET}  Embaucher un conserveur")
        print(f"  {C.ROUGE}[6]{C.RESET}  Licencier le conserveur")
        print(f"  {C.JAUNE}[7]{C.RESET}  Produire manuellement")
        print(f"  {C.VERT}[8]{C.RESET}  Vendre les conserves")
        print(f"  {C.GRIS}[0]{C.RESET}  Retour")
        ligne("─", 64, C.GRIS)
        print(f"  {C.BOLD}Choix : {C.RESET}", end="")

        choix = input().strip()
        if choix == "1":
            _acheter_equipement_generique(conserverie, CONSERVERIES, "Conserverie", C.CYAN,
                lambda m: {"possede": True, "niveau": m["niveau"], "nom": m["cfg"]["nom"],
                           "emoji": m["cfg"]["emoji"],
                           "poisson_par_boite": m["cfg"]["poisson_par_boite"],
                           "sel_par_boite": m["cfg"]["sel_par_boite"],
                           "capacite_jour": m["cfg"]["capacite_jour"],
                           "entretien": m["cfg"]["entretien"],
                           "usure": 0, "usure_max": 40, "en_panne": False})
        elif choix == "2":
            action_ameliorer_machine(conserverie, CONSERVERIES)
        elif choix == "3":
            _vendre_equipement_generique(conserverie, CONSERVERIES)
        elif choix == "4":
            action_reparer_machine(conserverie, CONSERVERIES)
        elif choix == "5":
            _embaucher_specialiste_generique(conserveur, config_conserveur, conserverie,
                                              "Conserveur", C.CYAN)
        elif choix == "6":
            _licencier_specialiste_generique(conserveur, "Conserveur")
        elif choix == "7":
            _produire_manuellement(conserverie, produire_conserves,
                                   "conserves", "boite(s)")
        elif choix == "8":
            _vendre_produit_generique("conserves", stock_conserves, prix_conserves,
                                      "🥫 Conserves", C.CYAN)
        elif choix == "0":
            return


# ──────────────────────────────────────────────
#  TISSU BRODE (SOIE + ÉPICES → TISSU BRODÉ)
# ──────────────────────────────────────────────

def config_brodeur(niveau):
    if niveau == 1:
        return {"salaire": 11, "efficacite": 0.60, "nom": "Apprenti brodeur",  "cout": 70}
    elif niveau == 2:
        return {"salaire": 22, "efficacite": 0.80, "nom": "Brodeur confirme",  "cout": 190}
    elif niveau == 3:
        return {"salaire": 40, "efficacite": 1.00, "nom": "Maitre brodeur",    "cout": 420}
    return None


def mettre_a_jour_prix_tissu():
    global prix_tissu, offre_demande_tissu
    offre_demande_tissu["offre"]   = limiter(offre_demande_tissu["offre"]   + random.randint(-7, 7))
    offre_demande_tissu["demande"] = limiter(offre_demande_tissu["demande"] + random.randint(-5, 11))
    if evenement_actif and evenement_actif.get("cible") in ("soie", "epices"):
        offre_demande_tissu["demande"] = limiter(offre_demande_tissu["demande"] + 12)
    offre   = offre_demande_tissu["offre"]
    demande = offre_demande_tissu["demande"]
    facteur = max(0.65, min(2.0, 1 + (demande/offre - 1) * 0.50))
    prix_tissu = max(40, round(TISSU_PRIX_BASE * facteur))


def produire_tissu(quantite_voulue):
    global stock_tissu, tissu_produit_total
    if not atelier_tissu["possede"] or atelier_tissu["en_panne"]:
        return 0, "Atelier de broderie indisponible."
    soie_dispo   = stock.get("soie", 0)
    epices_dispo = stock.get("epices", 0)
    s_par_t = atelier_tissu["soie_par_tissu"]
    e_par_t = atelier_tissu["epices_par_tissu"]
    max_prod = min(quantite_voulue, atelier_tissu["capacite_jour"],
                   soie_dispo // s_par_t, epices_dispo // e_par_t)
    if max_prod <= 0:
        return 0, f"Manque de soie ({s_par_t}/tissu) ou epices ({e_par_t}/tissu)."
    stock["soie"]   -= max_prod * s_par_t
    stock["epices"] -= max_prod * e_par_t
    stock_tissu     += max_prod
    tissu_produit_total += max_prod
    _appliquer_usure(atelier_tissu, 35, "atelier tissu")
    return max_prod, f"{max_prod} tissu(s) brode(s) ({max_prod*s_par_t} soie, {max_prod*e_par_t} epices)."


def payer_brodeur_et_atelier_tissu():
    _payer_specialiste(brodeur, "brodeur")
    if atelier_tissu["possede"] and not atelier_tissu["en_panne"]:
        global argent
        argent = max(0, argent - atelier_tissu["entretien"])
        historique.append((jour, f"Entretien {atelier_tissu['nom']}", -atelier_tissu["entretien"]))
    if brodeur["actif"]:
        _verifier_evolution_specialiste(brodeur, config_brodeur, "brodeur")


def action_brodeur_auto():
    if not brodeur["actif"] or not atelier_tissu["possede"] or atelier_tissu["en_panne"]:
        return
    eff = _efficacite_avec_moral(brodeur["efficacite"], brodeur.get("moral", 80))
    cap = int(atelier_tissu["capacite_jour"] * eff)
    produit, _ = produire_tissu(cap)
    if produit > 0:
        historique.append((jour, f"{brodeur['nom']} brode x{produit} tissu(s)", 0))


def action_atelier_tissu_brode():
    while True:
        effacer()
        titre_bloc("  BRODERIE — SOIE + ÉPICES  ", C.MAGENTA)

        print(f"\n  {C.BOLD}Atelier :{C.RESET} ", end="")
        if atelier_tissu["possede"]:
            etat = f"{C.ROUGE}EN PANNE{C.RESET}" if atelier_tissu["en_panne"] else f"{C.VERT}OK{C.RESET}"
            print(
                f"{atelier_tissu['emoji']} {C.BOLD}{atelier_tissu['nom']}{C.RESET}  {etat}  │  "
                f"Usure : {atelier_tissu['usure']}/{atelier_tissu['usure_max']}  │  "
                f"Entretien : {C.ROUGE}{atelier_tissu['entretien']} €/j{C.RESET}"
            )
        else:
            print(f"{C.GRIS}Aucun{C.RESET}")

        print(f"  {C.BOLD}Brodeur :{C.RESET} ", end="")
        if brodeur["actif"]:
            moral_barre = barre_progression(brodeur.get("moral", 80), 100, 10,
                                            C.VERT if brodeur.get("moral",80) >= 50 else C.ROUGE)
            print(
                f"{C.BOLD}{brodeur['nom']}{C.RESET}  │  "
                f"Moral : {moral_barre}  │  "
                f"Salaire : {C.ROUGE}{brodeur['salaire']} €/j{C.RESET}  │  "
                f"Exp : {brodeur.get('jours_travailles',0)}j"
            )
        else:
            print(f"{C.GRIS}Aucun{C.RESET}")

        print(
            f"\n  🧵 Soie : {C.JAUNE}{stock.get('soie',0)}{C.RESET}  │  "
            f"🌶 Epices : {C.JAUNE}{stock.get('epices',0)}{C.RESET}  │  "
            f"🎀 Tissu brode : {C.JAUNE}{stock_tissu}{C.RESET}  │  "
            f"Prix : {C.VERT}{prix_tissu} €{C.RESET}"
        )
        ligne("─", 64, C.GRIS)
        print(f"  {C.MAGENTA}[1]{C.RESET}  Acheter un atelier de broderie")
        print(f"  {C.JAUNE}[2]{C.RESET}  Améliorer l'atelier")
        print(f"  {C.ROUGE}[3]{C.RESET}  Vendre l'atelier")
        print(f"  {C.ROUGE}[4]{C.RESET}  Réparer l'atelier")
        print(f"  {C.VERT}[5]{C.RESET}  Embaucher un brodeur")
        print(f"  {C.ROUGE}[6]{C.RESET}  Licencier le brodeur")
        print(f"  {C.JAUNE}[7]{C.RESET}  Produire manuellement")
        print(f"  {C.VERT}[8]{C.RESET}  Vendre le tissu brodé")
        print(f"  {C.GRIS}[0]{C.RESET}  Retour")
        ligne("─", 64, C.GRIS)
        print(f"  {C.BOLD}Choix : {C.RESET}", end="")

        choix = input().strip()
        if choix == "1":
            _acheter_equipement_generique(atelier_tissu, ATELIERS_TISSU, "Atelier broderie", C.MAGENTA,
                lambda m: {"possede": True, "niveau": m["niveau"], "nom": m["cfg"]["nom"],
                           "emoji": m["cfg"]["emoji"],
                           "soie_par_tissu": m["cfg"]["soie_par_tissu"],
                           "epices_par_tissu": m["cfg"]["epices_par_tissu"],
                           "capacite_jour": m["cfg"]["capacite_jour"],
                           "entretien": m["cfg"]["entretien"],
                           "usure": 0, "usure_max": 35, "en_panne": False})
        elif choix == "2":
            action_ameliorer_machine(atelier_tissu, ATELIERS_TISSU)
        elif choix == "3":
            _vendre_equipement_generique(atelier_tissu, ATELIERS_TISSU)
        elif choix == "4":
            action_reparer_machine(atelier_tissu, ATELIERS_TISSU)
        elif choix == "5":
            _embaucher_specialiste_generique(brodeur, config_brodeur, atelier_tissu,
                                             "Brodeur", C.MAGENTA)
        elif choix == "6":
            _licencier_specialiste_generique(brodeur, "Brodeur")
        elif choix == "7":
            _produire_manuellement(atelier_tissu, produire_tissu, "tissu brode", "piece(s)")
        elif choix == "8":
            _vendre_produit_generique("tissu", stock_tissu, prix_tissu,
                                      "🎀 Tissu brode", C.MAGENTA)
        elif choix == "0":
            return


# ── Helpers génériques pour les menus d'atelier ──────────────────────────────

def _acheter_equipement_generique(machine_dict, constantes, titre, couleur, builder):
    global argent
    if machine_dict["possede"]:
        print(f"\n  {C.JAUNE}Tu possedes deja cet equipement.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    effacer()
    titre_bloc(f"  ACHAT — {titre.upper()}  ", couleur)
    print(f"\n  {C.BOLD}Niveaux disponibles :{C.RESET}")
    ligne("─", 64, C.GRIS)
    couleurs = {1: C.VERT, 2: C.JAUNE, 3: C.MAGENTA}
    for niv, cfg in constantes.items():
        coul = couleurs[niv]
        print(f"\n  {coul}{C.BOLD}[{niv}] {cfg['emoji']} {cfg['nom']}{C.RESET}")
        print(f"      Prix : {C.JAUNE}{cfg['cout']} €{C.RESET}  │  Entretien : {C.ROUGE}{cfg['entretien']} €/j{C.RESET}")
        print(f"      {C.GRIS}{cfg['desc']}{C.RESET}")
    ligne("─", 64, C.GRIS)
    print(f"  [0] Annuler\n  Choix : ", end="")
    try:
        choix = int(input())
    except ValueError:
        return
    if choix == 0 or choix not in constantes:
        return
    cfg = constantes[choix]
    if argent < cfg["cout"]:
        print(f"  {C.ROUGE}Fonds insuffisants.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    print(f"\n  Confirmer l'achat de {cfg['nom']} pour {C.JAUNE}{cfg['cout']} €{C.RESET} ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        return
    argent -= cfg["cout"]
    machine_dict.update(builder({"niveau": choix, "cfg": cfg}))
    historique.append((jour, f"Achat {cfg['nom']}", -cfg["cout"]))
    print(f"\n  {C.VERT}✔  {cfg['emoji']} {cfg['nom']} installe !{C.RESET}")
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


def _vendre_equipement_generique(machine_dict, constantes):
    global argent
    if not machine_dict["possede"]:
        print(f"  {C.GRIS}Aucun equipement a vendre.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    valeur = constantes[machine_dict["niveau"]]["cout"] // 2
    print(f"\n  Vendre {machine_dict['nom']} pour {C.JAUNE}{valeur} €{C.RESET} (50%) ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        return
    argent += valeur
    historique.append((jour, f"Vente {machine_dict['nom']}", valeur))
    for k in list(machine_dict.keys()):
        if isinstance(machine_dict[k], bool):
            machine_dict[k] = False
        elif isinstance(machine_dict[k], int):
            machine_dict[k] = 0
        elif isinstance(machine_dict[k], str):
            machine_dict[k] = None if k != "emoji" else ""
    machine_dict["possede"] = False
    print(f"\n  {C.JAUNE}✔  Vendu pour {valeur} €.{C.RESET}")
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


def _embaucher_specialiste_generique(specialiste, config_fn, machine_dict, titre, couleur):
    global argent
    effacer()
    titre_bloc(f"  EMBAUCHE — {titre.upper()}  ", couleur)
    if specialiste["actif"]:
        print(f"\n  {C.JAUNE}Tu as deja un {titre.lower()} : {specialiste['nom']}{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    if not machine_dict["possede"]:
        print(f"\n  {C.ROUGE}Aucun equipement installe !{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    print(f"\n  {C.BOLD}Profils :{C.RESET}")
    ligne("─", 64, C.GRIS)
    couleurs = {1: C.VERT, 2: C.JAUNE, 3: C.MAGENTA}
    for niv in range(1, 4):
        cfg = config_fn(niv)
        coul = couleurs[niv]
        eff_pct = int(cfg.get("efficacite", cfg.get("talent", 0)) * 100)
        print(
            f"\n  {coul}{C.BOLD}[{niv}] {cfg['nom']}{C.RESET}\n"
            f"      Embauche : {C.JAUNE}{cfg['cout']} €{C.RESET}  │  "
            f"Salaire : {C.ROUGE}{cfg['salaire']} €/j{C.RESET}  │  "
            f"Efficacite : {C.CYAN}{eff_pct}%{C.RESET}"
        )
    ligne("─", 64, C.GRIS)
    print(f"  [0] Annuler\n  Choix : ", end="")
    try:
        niv = int(input())
    except ValueError:
        return
    if niv == 0:
        return
    cfg = config_fn(niv)
    if cfg is None or argent < cfg["cout"]:
        print(f"  {C.ROUGE}Impossible.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    print(f"\n  Confirmer l'embauche de {cfg['nom']} pour {C.JAUNE}{cfg['cout']} €{C.RESET} ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        return
    argent -= cfg["cout"]
    specialiste["actif"]      = True
    specialiste["niveau"]     = niv
    specialiste["salaire"]    = cfg["salaire"]
    specialiste["nom"]        = cfg["nom"]
    specialiste["efficacite"] = cfg.get("efficacite", cfg.get("talent", 0))
    specialiste["moral"]      = 80
    specialiste["jours_travailles"] = 0
    specialiste["salaires_impaye"]  = 0
    historique.append((jour, f"Embauche {cfg['nom']}", -cfg["cout"]))
    print(f"\n  {C.VERT}✔  {cfg['nom']} recrute !{C.RESET}")
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


def _licencier_specialiste_generique(specialiste, titre):
    effacer()
    titre_bloc(f"  LICENCIEMENT — {titre.upper()}  ", C.ROUGE)
    if not specialiste["actif"]:
        print(f"\n  {C.GRIS}Aucun {titre.lower()} en poste.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    print(f"\n  Licencier {C.BOLD}{specialiste['nom']}{C.RESET} ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        return
    nom_tmp = specialiste["nom"]
    specialiste.update({"actif": False, "niveau": 0, "salaire": 0, "nom": None,
                        "efficacite": 0.0, "moral": 80, "jours_travailles": 0,
                        "salaires_impaye": 0})
    print(f"\n  {C.JAUNE}✔  {nom_tmp} licencie.{C.RESET}")
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


def _produire_manuellement(machine_dict, fn_produire, nom_produit, unite):
    effacer()
    titre_bloc(f"  PRODUCTION MANUELLE — {nom_produit.upper()}  ", C.JAUNE)
    if not machine_dict["possede"]:
        print(f"\n  {C.ROUGE}Aucun equipement installe.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    if machine_dict.get("en_panne"):
        print(f"\n  {C.ROUGE}Machine en panne ! Repare-la d'abord.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    print(f"\n  Quantite a produire : ", end="")
    try:
        qte = int(input())
    except ValueError:
        return
    if qte <= 0:
        return
    produit, msg = fn_produire(qte)
    if produit > 0:
        print(f"\n  {C.VERT}✔  {msg}{C.RESET}")
    else:
        print(f"\n  {C.ROUGE}✖  {msg}{C.RESET}")
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


def _vendre_produit_generique(cle_produit, stock_actuel, prix_actuel, label, couleur):
    global argent, stock_conserves, stock_tissu
    effacer()
    titre_bloc(f"  VENTE — {label.upper()}  ", couleur)
    if stock_actuel <= 0:
        print(f"\n  {C.ROUGE}Aucun stock a vendre.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    print(f"\n  {label} — {C.JAUNE}{prix_actuel} €{C.RESET}")
    print(f"  En stock : {C.CYAN}{stock_actuel}{C.RESET}  (valeur : {stock_actuel * prix_actuel} €)")
    print(f"  Quantite a vendre : ", end="")
    try:
        qte = int(input())
    except ValueError:
        return
    if qte <= 0 or qte > stock_actuel:
        print(f"  {C.ROUGE}Quantite invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    gain = qte * prix_actuel
    argent += gain
    if cle_produit == "conserves":
        stock_conserves -= qte
    elif cle_produit == "tissu":
        stock_tissu -= qte
    historique.append((jour, f"Vente {label} x{qte}", gain))
    print(f"\n  {C.VERT}✔  {qte} vendu(s) pour +{gain} €{C.RESET}")
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


# ──────────────────────────────────────────────
#  SYSTEME MOULIN / FARINE
# ──────────────────────────────────────────────

def config_meunier(niveau):
    if niveau == 1:
        return {"salaire": 8,  "efficacite": 0.60, "nom": "Apprenti meunier",   "cout": 50}
    elif niveau == 2:
        return {"salaire": 18, "efficacite": 0.80, "nom": "Meunier confirme",   "cout": 150}
    elif niveau == 3:
        return {"salaire": 35, "efficacite": 1.00, "nom": "Maitre meunier",     "cout": 350}
    return None


def mettre_a_jour_prix_farine():
    """
    Prix farine calculé via offre/demande propre à la farine.
    - Fluctuation aléatoire quotidienne de l'offre/demande
    - Si le blé est rare (offre faible), la farine devient plus rare aussi
    - Vendre de la farine augmente l'offre, produire de la farine augmente la demande
    """
    global prix_farine, offre_demande_farine

    # Fluctuation aléatoire quotidienne
    offre_demande_farine["offre"]   = limiter(offre_demande_farine["offre"]   + random.randint(-8, 8))
    offre_demande_farine["demande"] = limiter(offre_demande_farine["demande"] + random.randint(-6, 10))

    # Lien avec le blé : si blé rare sur le marché → farine plus rare
    offre_ble = offre_demande.get("ble", {}).get("offre", 100)
    if offre_ble < 60:
        offre_demande_farine["offre"]   = limiter(offre_demande_farine["offre"]   - 12)
        offre_demande_farine["demande"] = limiter(offre_demande_farine["demande"] + 8)

    # Événement blé (incendie / bonne récolte) se répercute sur la farine
    if evenement_actif and evenement_actif.get("cible") == "ble":
        if evenement_actif["mult"] > 1:   # blé plus cher → farine plus chère
            offre_demande_farine["demande"] = limiter(offre_demande_farine["demande"] + 15)
        elif evenement_actif["mult"] < 1: # blé bradé → farine moins chère
            offre_demande_farine["offre"]   = limiter(offre_demande_farine["offre"]   + 15)

    # Calcul du prix via facteur offre/demande
    offre   = offre_demande_farine["offre"]
    demande = offre_demande_farine["demande"]
    ratio   = demande / offre
    facteur = max(0.65, min(1.75, 1 + (ratio - 1) * 0.45))

    prix_farine = max(10, round(FARINE_PRIX_BASE * facteur))


def tendance_farine():
    offre   = offre_demande_farine["offre"]
    demande = offre_demande_farine["demande"]
    if demande >= offre + 35:
        return f"{C.VERT}Demande +{C.RESET}"
    elif offre >= demande + 35:
        return f"{C.ROUGE}Offre +{C.RESET}"
    else:
        return f"{C.GRIS}Stable{C.RESET}"


def modifier_marche_farine(type_action, quantite):
    """
    Vendre de la farine → offre augmente, demande baisse.
    Produire de la farine → demande augmente (signal de rareté).
    """
    if type_action == "vente":
        offre_demande_farine["offre"]   = limiter(offre_demande_farine["offre"]   + quantite * 3)
        offre_demande_farine["demande"] = limiter(offre_demande_farine["demande"] - quantite)
    elif type_action == "production":
        offre_demande_farine["demande"] = limiter(offre_demande_farine["demande"] + quantite * 2)


def produire_farine(quantite_voulue):
    """
    Tente de produire `quantite_voulue` sacs de farine.
    Consomme du blé, retourne (produit, message).
    """
    global stock_farine, farine_produite_total

    if not machine["possede"]:
        return 0, "Aucune machine installée."

    ble_dispo  = stock.get("ble", 0)
    ble_needed = machine["ble_par_farine"]
    max_par_ble = ble_dispo // ble_needed

    produit = min(quantite_voulue, machine["capacite_jour"], max_par_ble)

    if produit <= 0:
        return 0, f"Pas assez de ble (besoin : {ble_needed} par sac)."

    consomme = produit * ble_needed
    stock["ble"] -= consomme
    stock_farine += produit
    farine_produite_total += produit

    return produit, f"{produit} sac(s) de farine produit(s) ({consomme} ble consomme)."


def payer_meunier_et_entretien():
    """Déduit salaire meunier + entretien machine chaque jour."""
    global argent
    if meunier["actif"]:
        argent = max(0, argent - meunier["salaire"])
        historique.append((jour, f"Salaire {meunier['nom']}", -meunier["salaire"]))
    if machine["possede"]:
        argent = max(0, argent - machine["entretien"])
        historique.append((jour, f"Entretien {machine['nom']}", -machine["entretien"]))


def action_meunier_auto():
    """Le meunier produit automatiquement de la farine à chaque fin de jour."""
    if not meunier["actif"] or not machine["possede"]:
        return
    cap = int(machine["capacite_jour"] * meunier["efficacite"])
    produit, _ = produire_farine(cap)
    if produit > 0:
        historique.append((jour, f"{meunier['nom']} produit farine x{produit}", 0))


def acheter_machine():
    global argent, machine

    effacer()
    titre_bloc("  ATELIER — ACHAT MACHINE  ", C.BLEU)

    if machine["possede"]:
        print(f"\n  {C.JAUNE}Tu possedes deja : {machine['emoji']} {machine['nom']}{C.RESET}")
        print(f"  {C.GRIS}Vends ou demolis ta machine avant d'en acheter une nouvelle.{C.RESET}")
        input(f"\n  {C.GRIS}[ENTREE] pour revenir{C.RESET}")
        return

    print(f"\n  {C.BOLD}Machines disponibles :{C.RESET}")
    ligne("─", 72, C.GRIS)

    couleurs = {1: C.VERT, 2: C.JAUNE, 3: C.MAGENTA}
    for niv, m in MACHINES.items():
        coul = couleurs[niv]
        print(
            f"\n  {coul}{C.BOLD}[{niv}] {m['emoji']} {m['nom']}{C.RESET}\n"
            f"      Prix : {C.JAUNE}{m['cout']} €{C.RESET}  │  "
            f"Entretien : {C.ROUGE}{m['entretien']} €/jour{C.RESET}  │  "
            f"Rendement : {C.CYAN}{m['ble_par_farine']} ble → 1 farine{C.RESET}  │  "
            f"Capacite : {C.VERT}{m['capacite_jour']} sacs/jour{C.RESET}\n"
            f"      {C.GRIS}{m['desc']}{C.RESET}"
        )

    ligne("─", 72, C.GRIS)
    print(f"  {C.GRIS}[0]{C.RESET} Annuler")
    print(f"\n  {C.BOLD}Ton choix : {C.RESET}", end="")

    try:
        choix = int(input())
    except ValueError:
        print(f"\n  {C.ROUGE}Valeur invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    if choix == 0:
        return

    if choix not in MACHINES:
        print(f"\n  {C.ROUGE}Niveau invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    m = MACHINES[choix]
    if argent < m["cout"]:
        print(f"\n  {C.ROUGE}Fonds insuffisants !{C.RESET} Il te faut {m['cout']} €, tu as {argent} €.")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  Confirmer l'achat de {C.BOLD}{m['nom']}{C.RESET} pour {C.JAUNE}{m['cout']} €{C.RESET} ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        print(f"  {C.GRIS}Achat annule.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    argent -= m["cout"]
    machine["possede"]        = True
    machine["niveau"]         = choix
    machine["nom"]            = m["nom"]
    machine["emoji"]          = m["emoji"]
    machine["ble_par_farine"] = m["ble_par_farine"]
    machine["capacite_jour"]  = m["capacite_jour"]
    machine["entretien"]      = m["entretien"]

    historique.append((jour, f"Achat machine {m['nom']}", -m["cout"]))
    print(f"\n  {C.VERT}✔  {m['emoji']} {m['nom']} installee !{C.RESET}")
    print(f"  {C.GRIS}Tu peux maintenant moudre du ble en farine avec [M].{C.RESET}")
    input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")


def vendre_machine():
    global argent, machine

    if not machine["possede"]:
        print(f"\n  {C.GRIS}Aucune machine a vendre.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    valeur = MACHINES[machine["niveau"]]["cout"] // 2
    print(f"\n  Vendre {machine['emoji']} {machine['nom']} pour {C.JAUNE}{valeur} €{C.RESET} (50% du prix) ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        return

    argent += valeur
    historique.append((jour, f"Vente machine {machine['nom']}", valeur))
    nom_tmp = machine["nom"]
    machine["possede"]        = False
    machine["niveau"]         = 0
    machine["nom"]            = None
    machine["emoji"]          = ""
    machine["ble_par_farine"] = 0
    machine["capacite_jour"]  = 0
    machine["entretien"]      = 0
    print(f"\n  {C.JAUNE}✔  {nom_tmp} revendue pour {valeur} €.{C.RESET}")
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


def embaucher_meunier():
    global argent, meunier

    effacer()
    titre_bloc("  EMBAUCHE — MEUNIER  ", C.BLEU)

    if meunier["actif"]:
        print(f"\n  {C.JAUNE}Tu as deja un meunier : {C.BOLD}{meunier['nom']}{C.RESET}")
        print(f"  {C.GRIS}Licencie-le d'abord avant d'en recruter un autre.{C.RESET}")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    if not machine["possede"]:
        print(f"\n  {C.ROUGE}Aucune machine installee !{C.RESET} Achete d'abord une machine avec [M].")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  {C.BOLD}Profils disponibles :{C.RESET}")
    ligne("─", 64, C.GRIS)
    couleurs = {1: C.VERT, 2: C.JAUNE, 3: C.MAGENTA}
    icones   = {1: "🔰", 2: "⚒ ", 3: "🏆"}

    for niv in range(1, 4):
        cfg  = config_meunier(niv)
        coul = couleurs[niv]
        barre = barre_progression(int(cfg["efficacite"] * 100), 100, 12, coul)
        print(
            f"\n  {coul}{C.BOLD}[{niv}] {icones[niv]} {cfg['nom']}{C.RESET}\n"
            f"      Embauche : {C.JAUNE}{cfg['cout']} €{C.RESET}  │  "
            f"Salaire : {C.ROUGE}{cfg['salaire']} €/jour{C.RESET}  │  "
            f"Efficacite : {barre}"
        )

    ligne("─", 64, C.GRIS)
    print(f"  {C.GRIS}[0]{C.RESET} Annuler")
    print(f"\n  {C.BOLD}Ton choix : {C.RESET}", end="")

    try:
        niv = int(input())
    except ValueError:
        print(f"\n  {C.ROUGE}Valeur invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    if niv == 0:
        return
    cfg = config_meunier(niv)
    if cfg is None:
        print(f"\n  {C.ROUGE}Niveau invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    if argent < cfg["cout"]:
        print(f"\n  {C.ROUGE}Fonds insuffisants !{C.RESET} Il te faut {cfg['cout']} €.")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  Confirmer l'embauche de {C.BOLD}{cfg['nom']}{C.RESET} pour {C.JAUNE}{cfg['cout']} €{C.RESET} ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        print(f"  {C.GRIS}Annule.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    argent -= cfg["cout"]
    meunier["actif"]      = True
    meunier["niveau"]     = niv
    meunier["salaire"]    = cfg["salaire"]
    meunier["nom"]        = cfg["nom"]
    meunier["efficacite"] = cfg["efficacite"]

    historique.append((jour, f"Embauche {cfg['nom']}", -cfg["cout"]))
    print(f"\n  {C.VERT}✔  {cfg['nom']} recrute !{C.RESET}")
    print(f"  {C.GRIS}Il moudra automatiquement a chaque fin de journee.{C.RESET}")
    input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")


def licencier_meunier():
    global meunier

    effacer()
    titre_bloc("  LICENCIEMENT — MEUNIER  ", C.ROUGE)

    if not meunier["actif"]:
        print(f"\n  {C.GRIS}Aucun meunier en poste.{C.RESET}")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  Licencier {C.BOLD}{meunier['nom']}{C.RESET} ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        print(f"  {C.GRIS}Annule.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    nom_tmp = meunier["nom"]
    meunier["actif"]      = False
    meunier["niveau"]     = 0
    meunier["salaire"]    = 0
    meunier["nom"]        = None
    meunier["efficacite"] = 0.0

    print(f"\n  {C.JAUNE}✔  {nom_tmp} licencie.{C.RESET}")
    input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")


def action_moudre():
    """Action manuelle : le joueur moud lui-même du blé."""
    global argent

    effacer()
    titre_bloc("  ATELIER — MOUDRE DU BLE  ", C.BLEU)

    if not machine["possede"]:
        print(f"\n  {C.ROUGE}Aucune machine installee.{C.RESET} Achete-en une avec [M].")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    ble_dispo = stock.get("ble", 0)
    ble_par_f = machine["ble_par_farine"]
    max_prod  = min(machine["capacite_jour"], ble_dispo // ble_par_f)

    print(f"\n  Machine    : {machine['emoji']} {C.BOLD}{machine['nom']}{C.RESET}")
    print(f"  Conversion : {C.CYAN}{ble_par_f} ble → 1 sac de farine{C.RESET}")
    print(f"  Capacite   : {C.CYAN}{machine['capacite_jour']} sacs/jour{C.RESET}")
    print(f"  Ble en stock    : {C.JAUNE}{ble_dispo} unites{C.RESET}")
    print(f"  Farine en stock : {C.JAUNE}{stock_farine} sacs{C.RESET}")
    print(f"  Prix farine     : {C.VERT}{prix_farine} €/sac{C.RESET}")

    if max_prod <= 0:
        print(f"\n  {C.ROUGE}Impossible : pas assez de ble (besoin {ble_par_f} par sac).{C.RESET}")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  Tu peux produire jusqu'a {C.CYAN}{max_prod}{C.RESET} sac(s).")
    print(f"  Quantite a produire : ", end="")

    try:
        qte = int(input())
    except ValueError:
        print(f"  {C.ROUGE}Valeur invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    if qte <= 0:
        print(f"  {C.ROUGE}Quantite doit etre positive.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    produit, msg = produire_farine(qte)
    if produit > 0:
        historique.append((jour, f"Mouture manuelle farine x{produit}", 0))
        print(f"\n  {C.VERT}✔  {msg}{C.RESET}")
        print(f"  Stock farine : {C.JAUNE}{stock_farine} sacs{C.RESET}")
    else:
        print(f"\n  {C.ROUGE}✖  {msg}{C.RESET}")

    input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")


def action_vendre_farine():
    global argent, stock_farine

    effacer()
    titre_bloc("  VENDRE DE LA FARINE  ", C.VERT)

    if stock_farine <= 0:
        print(f"\n  {C.ROUGE}Aucun sac de farine en stock.{C.RESET}")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  🌾→🌫  {C.BOLD}Farine{C.RESET} — {C.JAUNE}{prix_farine} €/sac{C.RESET}")
    print(f"  En stock : {C.CYAN}{stock_farine} sac(s){C.RESET}  (valeur totale : {C.VERT}{stock_farine * prix_farine} €{C.RESET})")
    print(f"\n  Quantite a vendre (0 = annuler) : ", end="")

    try:
        qte = int(input())
    except ValueError:
        print(f"  {C.ROUGE}Valeur invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    if qte <= 0:
        return
    if qte > stock_farine:
        print(f"  {C.ROUGE}Tu n'as que {stock_farine} sac(s).{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    gain = qte * prix_farine
    argent += gain
    stock_farine -= qte

    historique.append((jour, f"Vente Farine x{qte}", gain))
    print(f"\n  {C.VERT}✔  Vente reussie !{C.RESET} {qte} sac(s) pour {C.VERT}+{gain} €{C.RESET}")
    input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")


def action_atelier():
    """Menu de gestion de l'atelier (machine + meunier)."""
    while True:
        effacer()
        titre_bloc("  ATELIER DE MOUTURE  ", C.BLEU)

        # Etat machine
        print(f"\n  {C.BOLD}Machine :{C.RESET} ", end="")
        if machine["possede"]:
            print(
                f"{machine['emoji']} {C.BOLD}{machine['nom']}{C.RESET}  │  "
                f"Rendement : {C.CYAN}{machine['ble_par_farine']} ble → 1 farine{C.RESET}  │  "
                f"Capacite : {C.CYAN}{machine['capacite_jour']} sacs/j{C.RESET}  │  "
                f"Entretien : {C.ROUGE}{machine['entretien']} €/j{C.RESET}"
            )
        else:
            print(f"{C.GRIS}Aucune{C.RESET}")

        # Etat meunier
        print(f"  {C.BOLD}Meunier :{C.RESET} ", end="")
        if meunier["actif"]:
            print(
                f"{C.BOLD}{meunier['nom']}{C.RESET}  │  "
                f"Efficacite : {C.CYAN}{int(meunier['efficacite']*100)}%{C.RESET}  │  "
                f"Salaire : {C.ROUGE}{meunier['salaire']} €/j{C.RESET}"
            )
        else:
            print(f"{C.GRIS}Aucun{C.RESET}")

        # Stocks
        print(
            f"\n  🌾 Ble en stock   : {C.JAUNE}{stock.get('ble', 0)}{C.RESET}  │  "
            f"🌫  Farine en stock : {C.JAUNE}{stock_farine} sacs{C.RESET}  │  "
            f"Prix farine : {C.VERT}{prix_farine} €/sac{C.RESET}"
        )

        ligne("─", 64, C.GRIS)
        print(f"  {C.BLEU}[1]{C.RESET}  Acheter une machine")
        print(f"  {C.ROUGE}[2]{C.RESET}  Vendre la machine")
        print(f"  {C.VERT}[3]{C.RESET}  Embaucher un meunier")
        print(f"  {C.ROUGE}[4]{C.RESET}  Licencier le meunier")
        print(f"  {C.JAUNE}[5]{C.RESET}  Moudre manuellement")
        print(f"  {C.VERT}[6]{C.RESET}  Vendre de la farine")
        print(f"  {C.GRIS}[0]{C.RESET}  Retour au jeu")
        ligne("─", 64, C.GRIS)
        print(f"  {C.BOLD}Choix : {C.RESET}", end="")

        choix = input().strip()

        if choix == "1":
            acheter_machine()
        elif choix == "2":
            vendre_machine()
        elif choix == "3":
            embaucher_meunier()
        elif choix == "4":
            licencier_meunier()
        elif choix == "5":
            action_moudre()
        elif choix == "6":
            action_vendre_farine()
        elif choix == "0":
            return
        else:
            print(f"  {C.ROUGE}Choix invalide.{C.RESET}")
            input(f"  {C.GRIS}[ENTREE]{C.RESET}")


# ──────────────────────────────────────────────
#  SYSTEME TISSAGE — SOIE → VÊTEMENTS
# ──────────────────────────────────────────────

def config_tisserand(niveau):
    if niveau == 1:
        return {"salaire": 9,  "efficacite": 0.60, "nom": "Apprenti tisserand", "cout": 60}
    elif niveau == 2:
        return {"salaire": 20, "efficacite": 0.80, "nom": "Tisserand confirme", "cout": 180}
    elif niveau == 3:
        return {"salaire": 38, "efficacite": 1.00, "nom": "Maitre tisserand",   "cout": 400}
    return None


def mettre_a_jour_prix_vetements():
    global prix_vetements, offre_demande_vetements

    offre_demande_vetements["offre"]   = limiter(offre_demande_vetements["offre"]   + random.randint(-8, 8))
    offre_demande_vetements["demande"] = limiter(offre_demande_vetements["demande"] + random.randint(-5, 11))

    # Lien avec la soie : si soie rare → vêtements rares
    offre_soie = offre_demande.get("soie", {}).get("offre", 100)
    if offre_soie < 60:
        offre_demande_vetements["offre"]   = limiter(offre_demande_vetements["offre"]   - 14)
        offre_demande_vetements["demande"] = limiter(offre_demande_vetements["demande"] + 10)

    # Événement soie se répercute sur les vêtements
    if evenement_actif and evenement_actif.get("cible") == "soie":
        if evenement_actif["mult"] > 1:
            offre_demande_vetements["demande"] = limiter(offre_demande_vetements["demande"] + 18)
        elif evenement_actif["mult"] < 1:
            offre_demande_vetements["offre"]   = limiter(offre_demande_vetements["offre"]   + 18)

    # Festival des tissus → forte demande
    if evenement_actif and "tissu" in evenement_actif.get("msg", "").lower():
        offre_demande_vetements["demande"] = limiter(offre_demande_vetements["demande"] + 25)

    offre   = offre_demande_vetements["offre"]
    demande = offre_demande_vetements["demande"]
    ratio   = demande / offre
    facteur = max(0.65, min(2.0, 1 + (ratio - 1) * 0.50))

    prix_vetements = max(20, round(VETEMENTS_PRIX_BASE * facteur))


def tendance_vetements():
    offre   = offre_demande_vetements["offre"]
    demande = offre_demande_vetements["demande"]
    if demande >= offre + 35:
        return f"{C.VERT}Demande +{C.RESET}"
    elif offre >= demande + 35:
        return f"{C.ROUGE}Offre +{C.RESET}"
    else:
        return f"{C.GRIS}Stable{C.RESET}"


def modifier_marche_vetements(type_action, quantite):
    if type_action == "vente":
        offre_demande_vetements["offre"]   = limiter(offre_demande_vetements["offre"]   + quantite * 3)
        offre_demande_vetements["demande"] = limiter(offre_demande_vetements["demande"] - quantite)
    elif type_action == "production":
        offre_demande_vetements["demande"] = limiter(offre_demande_vetements["demande"] + quantite * 2)


def produire_vetements(quantite_voulue):
    global stock_vetements, vetements_produits_total

    if not metier_a_tisser["possede"]:
        return 0, "Aucun metier a tisser installe."

    soie_dispo  = stock.get("soie", 0)
    soie_needed = metier_a_tisser["soie_par_vetement"]
    max_par_soie = soie_dispo // soie_needed

    produit = min(quantite_voulue, metier_a_tisser["capacite_jour"], max_par_soie)

    if produit <= 0:
        return 0, f"Pas assez de soie (besoin : {soie_needed} par vetement)."

    consomme = produit * soie_needed
    stock["soie"] -= consomme
    stock_vetements += produit
    vetements_produits_total += produit
    modifier_marche_vetements("production", produit)

    return produit, f"{produit} vetement(s) produit(s) ({consomme} soie consommee)."


def payer_tisserand_et_metier():
    global argent
    if tisserand["actif"]:
        argent = max(0, argent - tisserand["salaire"])
        historique.append((jour, f"Salaire {tisserand['nom']}", -tisserand["salaire"]))
    if metier_a_tisser["possede"]:
        argent = max(0, argent - metier_a_tisser["entretien"])
        historique.append((jour, f"Entretien {metier_a_tisser['nom']}", -metier_a_tisser["entretien"]))


def action_tisserand_auto():
    if not tisserand["actif"] or not metier_a_tisser["possede"]:
        return
    cap = int(metier_a_tisser["capacite_jour"] * tisserand["efficacite"])
    produit, _ = produire_vetements(cap)
    if produit > 0:
        historique.append((jour, f"{tisserand['nom']} tisse vetements x{produit}", 0))


def acheter_metier():
    global argent, metier_a_tisser

    effacer()
    titre_bloc("  MANUFACTURE — ACHAT METIER  ", C.MAGENTA)

    if metier_a_tisser["possede"]:
        print(f"\n  {C.JAUNE}Tu possedes deja : {metier_a_tisser['emoji']} {metier_a_tisser['nom']}{C.RESET}")
        print(f"  {C.GRIS}Vends-le avant d'en acheter un nouveau.{C.RESET}")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  {C.BOLD}Metiers disponibles :{C.RESET}")
    ligne("─", 72, C.GRIS)
    couleurs = {1: C.VERT, 2: C.JAUNE, 3: C.MAGENTA}

    for niv, m in METIERS.items():
        coul = couleurs[niv]
        print(
            f"\n  {coul}{C.BOLD}[{niv}] {m['emoji']} {m['nom']}{C.RESET}\n"
            f"      Prix : {C.JAUNE}{m['cout']} €{C.RESET}  │  "
            f"Entretien : {C.ROUGE}{m['entretien']} €/jour{C.RESET}  │  "
            f"Rendement : {C.CYAN}{m['soie_par_vetement']} soie → 1 vetement{C.RESET}  │  "
            f"Capacite : {C.VERT}{m['capacite_jour']} vetements/jour{C.RESET}\n"
            f"      {C.GRIS}{m['desc']}{C.RESET}"
        )

    ligne("─", 72, C.GRIS)
    print(f"  {C.GRIS}[0]{C.RESET} Annuler")
    print(f"\n  {C.BOLD}Ton choix : {C.RESET}", end="")

    try:
        choix = int(input())
    except ValueError:
        print(f"\n  {C.ROUGE}Valeur invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    if choix == 0:
        return
    if choix not in METIERS:
        print(f"\n  {C.ROUGE}Niveau invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    m = METIERS[choix]
    if argent < m["cout"]:
        print(f"\n  {C.ROUGE}Fonds insuffisants !{C.RESET} Il te faut {m['cout']} €, tu as {argent} €.")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  Confirmer l'achat de {C.BOLD}{m['nom']}{C.RESET} pour {C.JAUNE}{m['cout']} €{C.RESET} ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        print(f"  {C.GRIS}Annule.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    argent -= m["cout"]
    metier_a_tisser["possede"]           = True
    metier_a_tisser["niveau"]            = choix
    metier_a_tisser["nom"]               = m["nom"]
    metier_a_tisser["emoji"]             = m["emoji"]
    metier_a_tisser["soie_par_vetement"] = m["soie_par_vetement"]
    metier_a_tisser["capacite_jour"]     = m["capacite_jour"]
    metier_a_tisser["entretien"]         = m["entretien"]

    historique.append((jour, f"Achat {m['nom']}", -m["cout"]))
    print(f"\n  {C.VERT}✔  {m['emoji']} {m['nom']} installe !{C.RESET}")
    input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")


def vendre_metier():
    global argent, metier_a_tisser

    if not metier_a_tisser["possede"]:
        print(f"\n  {C.GRIS}Aucun metier a vendre.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    valeur = METIERS[metier_a_tisser["niveau"]]["cout"] // 2
    print(f"\n  Vendre {metier_a_tisser['emoji']} {metier_a_tisser['nom']} pour {C.JAUNE}{valeur} €{C.RESET} (50%) ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        return

    argent += valeur
    historique.append((jour, f"Vente {metier_a_tisser['nom']}", valeur))
    metier_a_tisser.update({"possede": False, "niveau": 0, "nom": None,
                             "emoji": "", "soie_par_vetement": 0,
                             "capacite_jour": 0, "entretien": 0})
    print(f"\n  {C.JAUNE}✔  Metier revendu pour {valeur} €.{C.RESET}")
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


def embaucher_tisserand():
    global argent, tisserand

    effacer()
    titre_bloc("  EMBAUCHE — TISSERAND  ", C.MAGENTA)

    if tisserand["actif"]:
        print(f"\n  {C.JAUNE}Tu as deja un tisserand : {C.BOLD}{tisserand['nom']}{C.RESET}")
        print(f"  {C.GRIS}Licencie-le d'abord.{C.RESET}")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    if not metier_a_tisser["possede"]:
        print(f"\n  {C.ROUGE}Aucun metier a tisser installe !{C.RESET} Achete-en un d'abord.")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  {C.BOLD}Profils disponibles :{C.RESET}")
    ligne("─", 64, C.GRIS)
    couleurs = {1: C.VERT, 2: C.JAUNE, 3: C.MAGENTA}
    icones   = {1: "🔰", 2: "🧵", 3: "🏆"}

    for niv in range(1, 4):
        cfg  = config_tisserand(niv)
        coul = couleurs[niv]
        barre = barre_progression(int(cfg["efficacite"] * 100), 100, 12, coul)
        print(
            f"\n  {coul}{C.BOLD}[{niv}] {icones[niv]} {cfg['nom']}{C.RESET}\n"
            f"      Embauche : {C.JAUNE}{cfg['cout']} €{C.RESET}  │  "
            f"Salaire : {C.ROUGE}{cfg['salaire']} €/jour{C.RESET}  │  "
            f"Efficacite : {barre}"
        )

    ligne("─", 64, C.GRIS)
    print(f"  {C.GRIS}[0]{C.RESET} Annuler")
    print(f"\n  {C.BOLD}Ton choix : {C.RESET}", end="")

    try:
        niv = int(input())
    except ValueError:
        print(f"\n  {C.ROUGE}Valeur invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    if niv == 0:
        return
    cfg = config_tisserand(niv)
    if cfg is None:
        print(f"\n  {C.ROUGE}Niveau invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    if argent < cfg["cout"]:
        print(f"\n  {C.ROUGE}Fonds insuffisants !{C.RESET} Il te faut {cfg['cout']} €.")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  Confirmer l'embauche de {C.BOLD}{cfg['nom']}{C.RESET} pour {C.JAUNE}{cfg['cout']} €{C.RESET} ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        print(f"  {C.GRIS}Annule.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    argent -= cfg["cout"]
    tisserand["actif"]      = True
    tisserand["niveau"]     = niv
    tisserand["salaire"]    = cfg["salaire"]
    tisserand["nom"]        = cfg["nom"]
    tisserand["efficacite"] = cfg["efficacite"]

    historique.append((jour, f"Embauche {cfg['nom']}", -cfg["cout"]))
    print(f"\n  {C.VERT}✔  {cfg['nom']} recrute !{C.RESET}")
    print(f"  {C.GRIS}Il tissera automatiquement chaque fin de journee.{C.RESET}")
    input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")


def licencier_tisserand():
    global tisserand

    effacer()
    titre_bloc("  LICENCIEMENT — TISSERAND  ", C.ROUGE)

    if not tisserand["actif"]:
        print(f"\n  {C.GRIS}Aucun tisserand en poste.{C.RESET}")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  Licencier {C.BOLD}{tisserand['nom']}{C.RESET} ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        print(f"  {C.GRIS}Annule.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    nom_tmp = tisserand["nom"]
    tisserand.update({"actif": False, "niveau": 0, "salaire": 0, "nom": None, "efficacite": 0.0})
    print(f"\n  {C.JAUNE}✔  {nom_tmp} licencie.{C.RESET}")
    input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")


def action_tisser():
    global argent

    effacer()
    titre_bloc("  MANUFACTURE — TISSER DE LA SOIE  ", C.MAGENTA)

    if not metier_a_tisser["possede"]:
        print(f"\n  {C.ROUGE}Aucun metier a tisser installe.{C.RESET}")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    soie_dispo  = stock.get("soie", 0)
    soie_par_v  = metier_a_tisser["soie_par_vetement"]
    max_prod    = min(metier_a_tisser["capacite_jour"], soie_dispo // soie_par_v)

    print(f"\n  Metier     : {metier_a_tisser['emoji']} {C.BOLD}{metier_a_tisser['nom']}{C.RESET}")
    print(f"  Conversion : {C.CYAN}{soie_par_v} soie → 1 vetement{C.RESET}")
    print(f"  Capacite   : {C.CYAN}{metier_a_tisser['capacite_jour']} vetements/jour{C.RESET}")
    print(f"  Soie en stock      : {C.JAUNE}{soie_dispo} unites{C.RESET}")
    print(f"  Vetements en stock : {C.JAUNE}{stock_vetements}{C.RESET}")
    print(f"  Prix vetement      : {C.VERT}{prix_vetements} €{C.RESET}")

    if max_prod <= 0:
        print(f"\n  {C.ROUGE}Impossible : pas assez de soie (besoin {soie_par_v} par vetement).{C.RESET}")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  Tu peux produire jusqu'a {C.CYAN}{max_prod}{C.RESET} vetement(s).")
    print(f"  Quantite a produire : ", end="")

    try:
        qte = int(input())
    except ValueError:
        print(f"  {C.ROUGE}Valeur invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    if qte <= 0:
        return

    produit, msg = produire_vetements(qte)
    if produit > 0:
        historique.append((jour, f"Tissage manuel vetements x{produit}", 0))
        print(f"\n  {C.VERT}✔  {msg}{C.RESET}")
        print(f"  Stock vetements : {C.JAUNE}{stock_vetements}{C.RESET}")
    else:
        print(f"\n  {C.ROUGE}✖  {msg}{C.RESET}")

    input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")


def action_atelier_vetements():
    while True:
        effacer()
        titre_bloc("  MANUFACTURE DE TISSAGE  ", C.MAGENTA)

        print(f"\n  {C.BOLD}Metier :{C.RESET} ", end="")
        if metier_a_tisser["possede"]:
            print(
                f"{metier_a_tisser['emoji']} {C.BOLD}{metier_a_tisser['nom']}{C.RESET}  │  "
                f"Rendement : {C.CYAN}{metier_a_tisser['soie_par_vetement']} soie → 1 vetement{C.RESET}  │  "
                f"Capacite : {C.CYAN}{metier_a_tisser['capacite_jour']} vet./j{C.RESET}  │  "
                f"Entretien : {C.ROUGE}{metier_a_tisser['entretien']} €/j{C.RESET}"
            )
        else:
            print(f"{C.GRIS}Aucun{C.RESET}")

        print(f"  {C.BOLD}Tisserand :{C.RESET} ", end="")
        if tisserand["actif"]:
            print(
                f"{C.BOLD}{tisserand['nom']}{C.RESET}  │  "
                f"Efficacite : {C.CYAN}{int(tisserand['efficacite']*100)}%{C.RESET}  │  "
                f"Salaire : {C.ROUGE}{tisserand['salaire']} €/j{C.RESET}"
            )
        else:
            print(f"{C.GRIS}Aucun{C.RESET}")

        print(
            f"\n  🧵 Soie en stock      : {C.JAUNE}{stock.get('soie', 0)}{C.RESET}  │  "
            f"👘 Vetements en stock : {C.JAUNE}{stock_vetements}{C.RESET}  │  "
            f"Prix : {C.VERT}{prix_vetements} €{C.RESET}"
        )

        ligne("─", 64, C.GRIS)
        print(f"  {C.MAGENTA}[1]{C.RESET}  Acheter un metier a tisser")
        print(f"  {C.ROUGE}[2]{C.RESET}  Vendre le metier")
        print(f"  {C.VERT}[3]{C.RESET}  Embaucher un tisserand")
        print(f"  {C.ROUGE}[4]{C.RESET}  Licencier le tisserand")
        print(f"  {C.JAUNE}[5]{C.RESET}  Tisser manuellement")
        print(f"  {C.GRIS}[0]{C.RESET}  Retour au jeu")
        ligne("─", 64, C.GRIS)
        print(f"  {C.BOLD}Choix : {C.RESET}", end="")

        choix = input().strip()

        if choix == "1":
            acheter_metier()
        elif choix == "2":
            vendre_metier()
        elif choix == "3":
            embaucher_tisserand()
        elif choix == "4":
            licencier_tisserand()
        elif choix == "5":
            action_tisser()
        elif choix == "0":
            return
        else:
            print(f"  {C.ROUGE}Choix invalide.{C.RESET}")
            input(f"  {C.GRIS}[ENTREE]{C.RESET}")


# ──────────────────────────────────────────────
#  SYSTEME ORFEVRERIE — OR → BIJOUX → ENCHERES
# ──────────────────────────────────────────────

def config_orfevre(niveau):
    if niveau == 1:
        return {"salaire": 12, "talent": 0.0,  "nom": "Apprenti orfèvre",  "cout": 80}
    elif niveau == 2:
        return {"salaire": 25, "talent": 0.15, "nom": "Joaillier confirme", "cout": 220}
    elif niveau == 3:
        return {"salaire": 50, "talent": 0.30, "nom": "Maitre orfèvre",     "cout": 500}
    return None


def tirer_qualite_bijou():
    """Tire une qualité selon les bornes de l'atelier + talent de l'orfèvre."""
    qmin = atelier_or["qualite_min"]
    qmax = atelier_or["qualite_max"]
    # Le talent de l'orfèvre peut faire monter la qualite max de 1
    if orfèvre["actif"] and orfèvre["talent"] > 0 and random.random() < orfèvre["talent"]:
        qmax = min(5, qmax + 1)
    return random.randint(qmin, qmax)


def produire_bijou(quantite_voulue):
    global stock_bijoux, bijoux_produits_total

    if not atelier_or["possede"]:
        return 0, "Aucun atelier installe."

    or_dispo   = stock.get("or", 0)
    or_needed  = atelier_or["or_par_bijou"]
    max_par_or = or_dispo // or_needed
    produit    = min(quantite_voulue, atelier_or["capacite_jour"], max_par_or)

    if produit <= 0:
        return 0, f"Pas assez d'or (besoin : {or_needed} par bijou)."

    consomme = produit * or_needed
    stock["or"] -= consomme
    noms_tires = random.choices(NOMS_BIJOUX, k=produit)

    for nom in noms_tires:
        qualite = tirer_qualite_bijou()
        stock_bijoux.append({"qualite": qualite, "nom": nom})
        bijoux_produits_total += 1
        historique.append((jour, f"Bijou cree : {nom} ({QUALITE_NOMS[qualite]})", 0))

    return produit, f"{produit} bijou(x) cree(s) ({consomme} or consomme)."


def valeur_bijoux():
    return sum(BIJOU_PRIX_BASE[b["qualite"]] for b in stock_bijoux)


def payer_orfevre_et_atelier():
    global argent
    if orfèvre["actif"]:
        argent = max(0, argent - orfèvre["salaire"])
        historique.append((jour, f"Salaire {orfèvre['nom']}", -orfèvre["salaire"]))
    if atelier_or["possede"]:
        argent = max(0, argent - atelier_or["entretien"])
        historique.append((jour, f"Entretien {atelier_or['nom']}", -atelier_or["entretien"]))


def action_orfevre_auto():
    if not orfèvre["actif"] or not atelier_or["possede"]:
        return
    cap = atelier_or["capacite_jour"]
    produit, _ = produire_bijou(cap)
    if produit > 0:
        historique.append((jour, f"{orfèvre['nom']} fabrique {produit} bijou(x)", 0))


def acheter_atelier_or():
    global argent, atelier_or

    effacer()
    titre_bloc("  ORFEVRERIE — ACHAT ATELIER  ", C.JAUNE)

    if atelier_or["possede"]:
        print(f"\n  {C.JAUNE}Tu possedes deja : {atelier_or['emoji']} {atelier_or['nom']}{C.RESET}")
        print(f"  {C.GRIS}Vends-le avant d'en acheter un nouveau.{C.RESET}")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  {C.BOLD}Ateliers disponibles :{C.RESET}")
    ligne("─", 72, C.GRIS)
    couleurs = {1: C.VERT, 2: C.JAUNE, 3: C.MAGENTA}

    for niv, a in ATELIERS_OR.items():
        coul = couleurs[niv]
        print(
            f"\n  {coul}{C.BOLD}[{niv}] {a['emoji']} {a['nom']}{C.RESET}\n"
            f"      Prix : {C.JAUNE}{a['cout']} €{C.RESET}  │  "
            f"Entretien : {C.ROUGE}{a['entretien']} €/jour{C.RESET}  │  "
            f"Rendement : {C.CYAN}{a['or_par_bijou']} or → 1 bijou{C.RESET}  │  "
            f"Capacite : {C.VERT}{a['capacite_jour']} bijou(x)/jour{C.RESET}\n"
            f"      Qualite : {QUALITE_NOMS[a['qualite_min']]} → {QUALITE_NOMS[a['qualite_max']]}  │  "
            f"{C.GRIS}{a['desc']}{C.RESET}"
        )

    ligne("─", 72, C.GRIS)
    print(f"  {C.GRIS}[0]{C.RESET} Annuler")
    print(f"\n  {C.BOLD}Ton choix : {C.RESET}", end="")

    try:
        choix = int(input())
    except ValueError:
        return

    if choix == 0:
        return
    if choix not in ATELIERS_OR:
        print(f"\n  {C.ROUGE}Niveau invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    a = ATELIERS_OR[choix]
    if argent < a["cout"]:
        print(f"\n  {C.ROUGE}Fonds insuffisants !{C.RESET} Il te faut {a['cout']} €.")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  Confirmer l'achat de {C.BOLD}{a['nom']}{C.RESET} pour {C.JAUNE}{a['cout']} €{C.RESET} ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        return

    argent -= a["cout"]
    atelier_or.update({
        "possede": True, "niveau": choix, "nom": a["nom"], "emoji": a["emoji"],
        "or_par_bijou": a["or_par_bijou"], "capacite_jour": a["capacite_jour"],
        "entretien": a["entretien"], "qualite_min": a["qualite_min"], "qualite_max": a["qualite_max"],
    })
    historique.append((jour, f"Achat {a['nom']}", -a["cout"]))
    print(f"\n  {C.VERT}✔  {a['emoji']} {a['nom']} installe !{C.RESET}")
    input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")


def vendre_atelier_or():
    global argent, atelier_or

    if not atelier_or["possede"]:
        print(f"\n  {C.GRIS}Aucun atelier a vendre.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    valeur = ATELIERS_OR[atelier_or["niveau"]]["cout"] // 2
    print(f"\n  Vendre {atelier_or['emoji']} {atelier_or['nom']} pour {C.JAUNE}{valeur} €{C.RESET} (50%) ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        return

    argent += valeur
    historique.append((jour, f"Vente {atelier_or['nom']}", valeur))
    atelier_or.update({"possede": False, "niveau": 0, "nom": None, "emoji": "",
                       "or_par_bijou": 0, "capacite_jour": 0, "entretien": 0,
                       "qualite_min": 0, "qualite_max": 0})
    print(f"\n  {C.JAUNE}✔  Atelier revendu pour {valeur} €.{C.RESET}")
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


def embaucher_orfevre():
    global argent, orfèvre

    effacer()
    titre_bloc("  EMBAUCHE — ORFÈVRE  ", C.JAUNE)

    if orfèvre["actif"]:
        print(f"\n  {C.JAUNE}Tu as deja un orfèvre : {C.BOLD}{orfèvre['nom']}{C.RESET}")
        print(f"  {C.GRIS}Licencie-le d'abord.{C.RESET}")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    if not atelier_or["possede"]:
        print(f"\n  {C.ROUGE}Aucun atelier installe !{C.RESET} Achete-en un d'abord.")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  {C.BOLD}Profils disponibles :{C.RESET}")
    ligne("─", 64, C.GRIS)
    couleurs = {1: C.VERT, 2: C.JAUNE, 3: C.MAGENTA}
    icones   = {1: "🔰", 2: "⚒ ", 3: "💎"}

    for niv in range(1, 4):
        cfg  = config_orfevre(niv)
        coul = couleurs[niv]
        talent_pct = int(cfg["talent"] * 100)
        print(
            f"\n  {coul}{C.BOLD}[{niv}] {icones[niv]} {cfg['nom']}{C.RESET}\n"
            f"      Embauche : {C.JAUNE}{cfg['cout']} €{C.RESET}  │  "
            f"Salaire : {C.ROUGE}{cfg['salaire']} €/jour{C.RESET}  │  "
            f"Talent : {C.CYAN}+{talent_pct}% chance qualite sup.{C.RESET}"
        )

    ligne("─", 64, C.GRIS)
    print(f"  {C.GRIS}[0]{C.RESET} Annuler")
    print(f"\n  {C.BOLD}Ton choix : {C.RESET}", end="")

    try:
        niv = int(input())
    except ValueError:
        return

    if niv == 0:
        return
    cfg = config_orfevre(niv)
    if cfg is None or argent < cfg["cout"]:
        print(f"\n  {C.ROUGE}Impossible.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  Confirmer l'embauche de {C.BOLD}{cfg['nom']}{C.RESET} pour {C.JAUNE}{cfg['cout']} €{C.RESET} ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        return

    argent -= cfg["cout"]
    orfèvre.update({"actif": True, "niveau": niv, "salaire": cfg["salaire"],
                    "nom": cfg["nom"], "talent": cfg["talent"]})
    historique.append((jour, f"Embauche {cfg['nom']}", -cfg["cout"]))
    print(f"\n  {C.VERT}✔  {cfg['nom']} recrute !{C.RESET}")
    input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")


def licencier_orfevre():
    global orfèvre

    effacer()
    titre_bloc("  LICENCIEMENT — ORFÈVRE  ", C.ROUGE)

    if not orfèvre["actif"]:
        print(f"\n  {C.GRIS}Aucun orfèvre en poste.{C.RESET}")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  Licencier {C.BOLD}{orfèvre['nom']}{C.RESET} ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        return

    nom_tmp = orfèvre["nom"]
    orfèvre.update({"actif": False, "niveau": 0, "salaire": 0, "nom": None, "talent": 0.0})
    print(f"\n  {C.JAUNE}✔  {nom_tmp} licencie.{C.RESET}")
    input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")


def action_forger():
    effacer()
    titre_bloc("  ORFEVRERIE — FORGER UN BIJOU  ", C.JAUNE)

    if not atelier_or["possede"]:
        print(f"\n  {C.ROUGE}Aucun atelier installe.{C.RESET}")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    or_dispo  = stock.get("or", 0)
    or_par_b  = atelier_or["or_par_bijou"]
    max_prod  = min(atelier_or["capacite_jour"], or_dispo // or_par_b)

    print(f"\n  Atelier    : {atelier_or['emoji']} {C.BOLD}{atelier_or['nom']}{C.RESET}")
    print(f"  Conversion : {C.CYAN}{or_par_b} or → 1 bijou{C.RESET}")
    print(f"  Qualite    : {QUALITE_NOMS[atelier_or['qualite_min']]} → {QUALITE_NOMS[atelier_or['qualite_max']]}", end="")
    if orfèvre["actif"] and orfèvre["talent"] > 0:
        print(f"  {C.CYAN}(+{int(orfèvre['talent']*100)}% chance de qualite sup.){C.RESET}")
    else:
        print()
    print(f"  Or en stock    : {C.JAUNE}{or_dispo}{C.RESET}")
    print(f"  Bijoux en stock : {C.JAUNE}{len(stock_bijoux)}{C.RESET}")

    if max_prod <= 0:
        print(f"\n  {C.ROUGE}Pas assez d'or (besoin {or_par_b} par bijou).{C.RESET}")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    print(f"\n  Tu peux forger jusqu'a {C.CYAN}{max_prod}{C.RESET} bijou(x).")
    print(f"  Quantite a forger : ", end="")

    try:
        qte = int(input())
    except ValueError:
        return

    if qte <= 0:
        return

    produit, msg = produire_bijou(qte)
    if produit > 0:
        print(f"\n  {C.VERT}✔  {msg}{C.RESET}")
        print(f"\n  {C.BOLD}Bijoux crees :{C.RESET}")
        for b in stock_bijoux[-produit:]:
            prix_est = BIJOU_PRIX_BASE[b["qualite"]]
            print(f"    {QUALITE_NOMS[b['qualite']]}  {C.BOLD}{b['nom']}{C.RESET}  — valeur estimee {C.JAUNE}~{prix_est} €{C.RESET}")
    else:
        print(f"\n  {C.ROUGE}✖  {msg}{C.RESET}")

    input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")


def action_enchere():
    """Salle des enchères : vendre un bijou à des acheteurs PNJ."""
    global argent, stock_bijoux

    effacer()
    titre_bloc("  SALLE DES ENCHERES  ", C.JAUNE)

    if not stock_bijoux:
        print(f"\n  {C.ROUGE}Tu n'as aucun bijou a mettre aux encheres.{C.RESET}")
        print(f"  {C.GRIS}Forge des bijoux dans ton atelier [X] → Forger.{C.RESET}")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    # Afficher les bijoux disponibles
    print(f"\n  {C.BOLD}Tes bijoux :{C.RESET}")
    ligne("─", 60, C.GRIS)
    for i, b in enumerate(stock_bijoux, 1):
        prix_base = BIJOU_PRIX_BASE[b["qualite"]]
        print(f"  {C.JAUNE}[{i}]{C.RESET}  {QUALITE_NOMS[b['qualite']]}  {C.BOLD}{b['nom']}{C.RESET}  — valeur estimee {C.CYAN}~{prix_base} €{C.RESET}")
    print(f"  {C.GRIS}[0]{C.RESET}  Annuler")
    ligne("─", 60, C.GRIS)
    print(f"\n  Quel bijou mettre en vente ? : ", end="")

    try:
        choix = int(input())
    except ValueError:
        return
    if choix == 0:
        return
    if not (1 <= choix <= len(stock_bijoux)):
        print(f"  {C.ROUGE}Choix invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return

    bijou = stock_bijoux[choix - 1]
    prix_base = BIJOU_PRIX_BASE[bijou["qualite"]]

    print(f"\n  Tu mets aux encheres : {QUALITE_NOMS[bijou['qualite']]} {C.BOLD}{bijou['nom']}{C.RESET}")
    print(f"  Valeur estimee : {C.CYAN}~{prix_base} €{C.RESET}")
    print(f"  Prix de reserve (mise minimum, 0 = sans reserve) : ", end="")

    try:
        reserve = int(input())
    except ValueError:
        reserve = 0
    reserve = max(0, reserve)

    # ── Génération des acheteurs PNJ ──────────────────────────────────────────
    effacer()
    titre_bloc("  ENCHERES EN COURS  ", C.JAUNE)
    print(f"\n  Lot : {QUALITE_NOMS[bijou['qualite']]} {C.BOLD}{bijou['nom']}{C.RESET}")
    if reserve > 0:
        print(f"  Prix de reserve : {C.ROUGE}{reserve} €{C.RESET}")
    print()

    # Bonus si commande royale active
    bonus_noble = evenement_actif and "or" in evenement_actif.get("msg", "").lower()

    # 3 acheteurs de base + 1 noble possible
    noms_acheteurs = ["Marchand Borino", "Dame Elvira", "Negociant Fust"]
    if bonus_noble:
        noms_acheteurs.append("Comte de Valverde")
        print(f"  {C.JAUNE}★ Un noble est present ! Il encheries generalement haut.{C.RESET}\n")

    acheteurs = []
    for nom in noms_acheteurs:
        est_noble = "Comte" in nom
        budget_min = int(prix_base * (1.5 if est_noble else 0.7))
        budget_max = int(prix_base * (2.8 if est_noble else 1.8))
        interet   = random.uniform(0.4, 1.0)  # probabilite de surencherir
        budget    = random.randint(budget_min, budget_max)
        acheteurs.append({"nom": nom, "budget": budget, "interet": interet,
                           "mise": 0, "actif": True, "est_noble": est_noble})

    # ── Simulation de l'enchère ───────────────────────────────────────────────
    mise_actuelle = max(reserve, int(prix_base * 0.5))
    gagnant       = None
    increment_min = max(5, int(prix_base * 0.05))
    increment_max = max(20, int(prix_base * 0.20))

    ligne("─", 60, C.GRIS)
    print(f"  {C.BOLD}Mise de depart : {C.JAUNE}{mise_actuelle} €{C.RESET}\n")
    pause(0.3)

    for tour in range(1, 8):
        print(f"  {C.GRIS}— Tour {tour} —{C.RESET}")
        encheres_ce_tour = False

        for ach in acheteurs:
            if not ach["actif"]:
                continue
            # L'acheteur surencherit selon son intérêt et son budget
            if random.random() < ach["interet"] and ach["budget"] > mise_actuelle:
                increment = random.randint(increment_min, increment_max)
                nouvelle_mise = min(ach["budget"], mise_actuelle + increment)
                if nouvelle_mise > mise_actuelle:
                    mise_actuelle = nouvelle_mise
                    gagnant       = ach
                    ach["mise"]   = nouvelle_mise
                    coul = C.JAUNE if ach["est_noble"] else C.BLANC
                    print(f"  {coul}{C.BOLD}{ach['nom']}{C.RESET} : {C.VERT}{mise_actuelle} €{C.RESET}  !", end="")
                    if tour <= 2:
                        print(f"  {C.GRIS}(ouverture){C.RESET}")
                    elif mise_actuelle > prix_base * 1.5:
                        print(f"  {C.JAUNE} ⬆ Surenchere !!{C.RESET}")
                    else:
                        print()
                    encheres_ce_tour = True
                    pause(0.2)
            else:
                ach["interet"] *= 0.85  # se decourage un peu

        if not encheres_ce_tour:
            print(f"  {C.GRIS}Plus d'encherisseurs actifs.{C.RESET}")
            break
        pause(0.1)

    # ── Résultat ──────────────────────────────────────────────────────────────
    print()
    ligne("─", 60, C.GRIS)

    if gagnant is None or mise_actuelle < reserve:
        print(f"\n  {C.ROUGE}✖  Personne n'a atteint le prix de reserve ({reserve} €).{C.RESET}")
        print(f"  {C.GRIS}Le bijou vous est retourne.{C.RESET}")
        input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")
        return

    # Vente réussie
    stock_bijoux.pop(choix - 1)
    argent += mise_actuelle
    historique.append((jour, f"Enchere {bijou['nom']} ({QUALITE_NOMS[bijou['qualite']]})", mise_actuelle))

    print(f"\n  {C.VERT}🏆 ADJUGE !{C.RESET}")
    print(f"  {C.BOLD}{gagnant['nom']}{C.RESET} remporte {C.BOLD}{bijou['nom']}{C.RESET} pour {C.JAUNE}{C.BOLD}{mise_actuelle} €{C.RESET} !")
    bénéfice = mise_actuelle - prix_base
    if bénéfice > 0:
        print(f"  {C.VERT}Benefice vs estimation : +{bénéfice} €{C.RESET}")
    elif bénéfice < 0:
        print(f"  {C.ROUGE}En dessous de l'estimation : {bénéfice} €{C.RESET}")

    input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")


def action_atelier_or():
    while True:
        effacer()
        titre_bloc("  ORFEVRERIE  ", C.JAUNE)

        print(f"\n  {C.BOLD}Atelier :{C.RESET} ", end="")
        if atelier_or["possede"]:
            print(
                f"{atelier_or['emoji']} {C.BOLD}{atelier_or['nom']}{C.RESET}  │  "
                f"Rendement : {C.CYAN}{atelier_or['or_par_bijou']} or → 1 bijou{C.RESET}  │  "
                f"Capacite : {C.CYAN}{atelier_or['capacite_jour']}/j{C.RESET}  │  "
                f"Entretien : {C.ROUGE}{atelier_or['entretien']} €/j{C.RESET}"
            )
            print(f"            Qualite : {QUALITE_NOMS[atelier_or['qualite_min']]} → {QUALITE_NOMS[atelier_or['qualite_max']]}")
        else:
            print(f"{C.GRIS}Aucun{C.RESET}")

        print(f"  {C.BOLD}Orfèvre :{C.RESET} ", end="")
        if orfèvre["actif"]:
            print(
                f"{C.BOLD}{orfèvre['nom']}{C.RESET}  │  "
                f"Talent : {C.CYAN}+{int(orfèvre['talent']*100)}% qualite{C.RESET}  │  "
                f"Salaire : {C.ROUGE}{orfèvre['salaire']} €/j{C.RESET}"
            )
        else:
            print(f"{C.GRIS}Aucun{C.RESET}")

        print(
            f"\n  ✨ Or en stock    : {C.JAUNE}{stock.get('or', 0)}{C.RESET}  │  "
            f"💍 Bijoux en stock : {C.JAUNE}{len(stock_bijoux)}{C.RESET}  │  "
            f"Valeur estimee : {C.VERT}{valeur_bijoux()} €{C.RESET}"
        )

        if stock_bijoux:
            print(f"\n  {C.BOLD}Tes bijoux :{C.RESET}")
            for b in stock_bijoux:
                print(f"    {QUALITE_NOMS[b['qualite']]}  {b['nom']}  — {C.CYAN}~{BIJOU_PRIX_BASE[b['qualite']]} €{C.RESET}")

        ligne("─", 64, C.GRIS)
        print(f"  {C.JAUNE}[1]{C.RESET}  Acheter un atelier")
        print(f"  {C.ROUGE}[2]{C.RESET}  Vendre l'atelier")
        print(f"  {C.VERT}[3]{C.RESET}  Embaucher un orfèvre")
        print(f"  {C.ROUGE}[4]{C.RESET}  Licencier l'orfèvre")
        print(f"  {C.JAUNE}[5]{C.RESET}  Forger manuellement")
        print(f"  {C.MAGENTA}[6]{C.RESET}  Salle des encheres")
        print(f"  {C.GRIS}[0]{C.RESET}  Retour")
        ligne("─", 64, C.GRIS)
        print(f"  {C.BOLD}Choix : {C.RESET}", end="")

        choix = input().strip()
        if choix == "1":
            acheter_atelier_or()
        elif choix == "2":
            vendre_atelier_or()
        elif choix == "3":
            embaucher_orfevre()
        elif choix == "4":
            licencier_orfevre()
        elif choix == "5":
            action_forger()
        elif choix == "6":
            action_enchere()
        elif choix == "0":
            return
        else:
            print(f"  {C.ROUGE}Choix invalide.{C.RESET}")
            input(f"  {C.GRIS}[ENTREE]{C.RESET}")


# ══════════════════════════════════════════════
#  SAISONS
# ══════════════════════════════════════════════

def appliquer_modificateurs_saison():
    """Applique les bonus/malus d'offre/demande de la saison courante."""
    saison = get_saison()
    for cle, mod in saison["modificateurs"].items():
        if cle in offre_demande:
            offre_demande[cle]["offre"]   = limiter(offre_demande[cle]["offre"]   + mod["offre"])
            offre_demande[cle]["demande"] = limiter(offre_demande[cle]["demande"] + mod["demande"])


# ══════════════════════════════════════════════
#  CONCURRENTS PNJ
# ══════════════════════════════════════════════

def initialiser_concurrents():
    global concurrents
    concurrents = []
    for base in CONCURRENTS_BASE:
        c = dict(base)
        c["stock"] = {cle: 0 for cle in PRODUITS}
        c["transactions_jour"] = []
        concurrents.append(c)


def action_concurrent(c):
    """Un concurrent achète ou vend selon son style."""
    style = c["style"]

    for cle in random.sample(list(PRODUITS.keys()), len(PRODUITS)):
        prix  = prix_actuels[cle]
        base  = PRODUITS[cle]["prix_base"]
        score_a = score_opportunite_achat(cle)
        score_v = score_opportunite_vente(cle)

        if style == "prudent":
            seuil_a, seuil_v = 0.15, 0.15
        elif style == "agressif":
            seuil_a, seuil_v = 0.05, 0.05
        else:  # speculateur
            seuil_a, seuil_v = 0.20, 0.08

        # Vente
        if c["stock"][cle] > 0 and score_v >= seuil_v:
            qte = 1
            c["stock"][cle] -= qte
            c["capital"] += prix * qte
            modifier_marche_apres_transaction(cle, "vente", qte)
            c["transactions_jour"].append(f"vend {PRODUITS[cle]['nom']}")

        # Achat
        elif score_a >= seuil_a and c["capital"] >= prix:
            c["stock"][cle] += 1
            c["capital"] -= prix
            modifier_marche_apres_transaction(cle, "achat", 1)
            c["transactions_jour"].append(f"achete {PRODUITS[cle]['nom']}")


def action_tous_concurrents():
    for c in concurrents:
        c["transactions_jour"] = []
        action_concurrent(c)


def afficher_concurrents():
    effacer()
    titre_bloc("  CONCURRENTS DU MARCHÉ  ", C.ROUGE)
    print()
    for c in concurrents:
        capital_str = f"{C.JAUNE}{c['capital']} €{C.RESET}"
        print(f"  {c['emoji']} {C.BOLD}{c['nom']}{C.RESET}  │  Capital : {capital_str}  │  Style : {C.CYAN}{c['style']}{C.RESET}")
        stocks_actifs = [(cle, qte) for cle, qte in c["stock"].items() if qte > 0]
        if stocks_actifs:
            s = ", ".join(f"{PRODUITS[cle]['emoji']} {PRODUITS[cle]['nom']} x{qte}" for cle, qte in stocks_actifs)
            print(f"     Stock : {C.GRIS}{s}{C.RESET}")
        if c["transactions_jour"]:
            print(f"     Aujourd'hui : {C.GRIS}{', '.join(c['transactions_jour'][:3])}{C.RESET}")
        print()
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


# ══════════════════════════════════════════════
#  MORAL & ÉVOLUTION DES EMPLOYÉS
# ══════════════════════════════════════════════

def _moral_couleur(m):
    if m >= 75:
        return C.VERT
    elif m >= 40:
        return C.JAUNE
    else:
        return C.ROUGE


def _efficacite_reelle(employe_dict):
    """Retourne l'efficacité effective en tenant compte du moral."""
    base = employe_dict.get("efficacite", 1.0)
    moral = employe_dict.get("moral", 100)
    # En dessous de 50 moral : efficacité réduite jusqu'à -40%
    facteur_moral = 1.0 if moral >= 50 else 0.6 + (moral / 50) * 0.4
    return base * facteur_moral


def mettre_a_jour_moral(emp, a_travaille=True, salaire_paye=True, machine_ok=True):
    """Calcule l'évolution du moral d'un employé."""
    if not emp["actif"]:
        return

    variation = 0

    if salaire_paye:
        variation += 5          # paiement régulier = moral stable
        emp["salaires_impaye"] = 0
    else:
        emp["salaires_impaye"] += 1
        variation -= 15 * emp["salaires_impaye"]  # chaque jour impayé pèse plus

    if not machine_ok:
        variation -= 8          # machine en panne = frustration

    if a_travaille:
        emp["jours_travailles"] = emp.get("jours_travailles", 0) + 1
        variation += 2          # travailler = progression naturelle

    emp["moral"] = max(0, min(100, emp["moral"] + variation))


def verifier_evolution_employe():
    """Propose de faire évoluer l'employé commercial s'il a assez d'expérience."""
    global argent
    if not employe["actif"]:
        return
    niv = employe["niveau"]
    seuils = {1: 5, 2: 8}
    if niv in seuils and employe["jours_travailles"] >= seuils[niv]:
        cout_upgrade = {1: 100, 2: 250}[niv]
        print(f"\n  {C.JAUNE}★ {employe['nom']} a assez d'experience pour evoluer !{C.RESET}")
        print(f"  Cout de promotion : {C.JAUNE}{cout_upgrade} €{C.RESET}")
        print(f"  Promouvoir ? (o/n) : ", end="")
        if input().strip().lower() == "o" and argent >= cout_upgrade:
            argent -= cout_upgrade
            nouveau_niv = niv + 1
            cfg = config_employe(nouveau_niv)
            employe["niveau"]           = nouveau_niv
            employe["salaire"]          = cfg["salaire"]
            employe["fiabilite"]        = cfg["fiabilite"]
            employe["nom"]              = cfg["nom"]
            employe["jours_travailles"] = 0
            employe["moral"]            = min(100, employe["moral"] + 20)
            historique.append((jour, f"Promotion → {cfg['nom']}", -cout_upgrade))
            print(f"\n  {C.VERT}✔  Promu ! Nouvel employe : {cfg['nom']}{C.RESET}")
            input(f"  {C.GRIS}[ENTREE]{C.RESET}")


def verifier_evolution_ouvrier(emp, config_fn, label):
    """Propose l'évolution pour meunier/tisserand/conserveur/brodeur/orfèvre."""
    if not emp["actif"]:
        return
    niv = emp["niveau"]
    seuils = {1: 5, 2: 8}
    if niv in seuils and emp.get("jours_travailles", 0) >= seuils[niv]:
        cout_upgrade = {1: 80, 2: 200}[niv]
        print(f"\n  {C.JAUNE}★ {emp['nom']} ({label}) peut evoluer !{C.RESET}")
        print(f"  Cout de promotion : {C.JAUNE}{cout_upgrade} €{C.RESET}")
        print(f"  Promouvoir ? (o/n) : ", end="")
        global argent
        if input().strip().lower() == "o" and argent >= cout_upgrade:
            argent -= cout_upgrade
            nouveau_niv = niv + 1
            cfg = config_fn(nouveau_niv)
            emp["niveau"]           = nouveau_niv
            emp["salaire"]          = cfg["salaire"]
            emp["efficacite"]       = cfg["efficacite"]
            emp["nom"]              = cfg["nom"]
            emp["jours_travailles"] = 0
            emp["moral"]            = min(100, emp["moral"] + 20)
            historique.append((jour, f"Promotion {label} → {cfg['nom']}", -cout_upgrade))
            print(f"\n  {C.VERT}✔  {cfg['nom']} promu !{C.RESET}")
            input(f"  {C.GRIS}[ENTREE]{C.RESET}")


# ══════════════════════════════════════════════
#  USURE DES MACHINES
# ══════════════════════════════════════════════

def _incrementer_usure(machine_dict, nb_produit=1):
    """Incrémente l'usure et retourne True si la machine tombe en panne."""
    if not machine_dict["possede"] or machine_dict["en_panne"]:
        return False
    machine_dict["usure"] += nb_produit
    if machine_dict["usure"] >= machine_dict["usure_max"]:
        machine_dict["en_panne"] = True
        return True
    return False


def cout_reparation(machine_dict, constantes_dict):
    """Coût de réparation = 30% du prix d'achat de la machine."""
    niv = machine_dict["niveau"]
    if niv in constantes_dict:
        return int(constantes_dict[niv]["cout"] * 0.30)
    return 50


def reparer_machine(machine_dict, constantes_dict, label):
    global argent
    cout = cout_reparation(machine_dict, constantes_dict)
    print(f"\n  {C.ROUGE}⚠ {machine_dict['nom']} est en panne !{C.RESET}")
    print(f"  Cout de reparation : {C.JAUNE}{cout} €{C.RESET}")
    print(f"  Reparer ? (o/n) : ", end="")
    if input().strip().lower() == "o":
        if argent < cout:
            print(f"  {C.ROUGE}Fonds insuffisants.{C.RESET}")
            input(f"  {C.GRIS}[ENTREE]{C.RESET}")
            return
        argent -= cout
        machine_dict["en_panne"] = False
        machine_dict["usure"]    = 0
        historique.append((jour, f"Reparation {machine_dict['nom']}", -cout))
        print(f"\n  {C.VERT}✔  Machine reparee !{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")


def ameliorer_machine(machine_dict, constantes_dict, champs_a_copier, label):
    """Upgrade une machine en place (niveau +1) pour 50% du prix d'achat suivant."""
    global argent
    niv = machine_dict["niveau"]
    if niv >= 3:
        print(f"\n  {C.GRIS}Cette machine est deja au niveau maximum.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    prochaine = constantes_dict[niv + 1]
    cout = int(prochaine["cout"] * 0.50)
    print(f"\n  Ameliorer vers {C.BOLD}{prochaine['nom']}{C.RESET} pour {C.JAUNE}{cout} €{C.RESET} (50% du prix neuf) ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        return
    if argent < cout:
        print(f"  {C.ROUGE}Fonds insuffisants.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    argent -= cout
    machine_dict["niveau"] = niv + 1
    for champ in champs_a_copier:
        machine_dict[champ] = prochaine[champ]
    machine_dict["nom"]      = prochaine["nom"]
    machine_dict["emoji"]    = prochaine.get("emoji", machine_dict["emoji"])
    machine_dict["usure"]    = 0
    machine_dict["en_panne"] = False
    historique.append((jour, f"Upgrade {label} → {prochaine['nom']}", -cout))
    print(f"\n  {C.VERT}✔  Machine amelioree : {prochaine['nom']}{C.RESET}")
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


# ══════════════════════════════════════════════
#  CONSERVES (poisson + sel → conserves)
# ══════════════════════════════════════════════

def config_conserveur(niveau):
    if niveau == 1:
        return {"salaire": 7,  "efficacite": 0.60, "nom": "Apprenti conserveur",  "cout": 50}
    elif niveau == 2:
        return {"salaire": 16, "efficacite": 0.80, "nom": "Conserveur confirme",  "cout": 140}
    elif niveau == 3:
        return {"salaire": 30, "efficacite": 1.00, "nom": "Maitre conserveur",    "cout": 300}
    return None


def mettre_a_jour_prix_conserves():
    global prix_conserves, offre_demande_conserves
    offre_demande_conserves["offre"]   = limiter(offre_demande_conserves["offre"]   + random.randint(-7, 7))
    offre_demande_conserves["demande"] = limiter(offre_demande_conserves["demande"] + random.randint(-5, 10))
    if offre_demande.get("poisson", {}).get("offre", 100) < 60:
        offre_demande_conserves["offre"]   = limiter(offre_demande_conserves["offre"]   - 12)
        offre_demande_conserves["demande"] = limiter(offre_demande_conserves["demande"] + 8)
    ratio   = offre_demande_conserves["demande"] / offre_demande_conserves["offre"]
    facteur = max(0.65, min(1.80, 1 + (ratio - 1) * 0.45))
    prix_conserves = max(14, round(CONSERVES_PRIX_BASE * facteur))


def produire_conserves(qte_voulue):
    global stock_conserves, conserves_produites_total
    if not conserverie["possede"] or conserverie["en_panne"]:
        return 0, "Conserverie indisponible."
    poisson_dispo = stock.get("poisson", 0)
    sel_dispo     = stock.get("sel", 0)
    p_par_b = conserverie["poisson_par_boite"]
    s_par_b = conserverie["sel_par_boite"]
    max_prod = min(qte_voulue, conserverie["capacite_jour"],
                  poisson_dispo // p_par_b, sel_dispo // s_par_b)
    if max_prod <= 0:
        return 0, f"Besoin {p_par_b} poisson + {s_par_b} sel par boite."
    stock["poisson"]     -= max_prod * p_par_b
    stock["sel"]         -= max_prod * s_par_b
    stock_conserves      += max_prod
    conserves_produites_total += max_prod
    panne = _incrementer_usure(conserverie, max_prod)
    return max_prod, f"{max_prod} boite(s) produites.{' ⚠ PANNE !' if panne else ''}"


def payer_conserveur_et_conserverie():
    global argent
    if conserveur["actif"]:
        if argent >= conserveur["salaire"]:
            argent -= conserveur["salaire"]
            historique.append((jour, f"Salaire {conserveur['nom']}", -conserveur["salaire"]))
            mettre_a_jour_moral(conserveur, salaire_paye=True, machine_ok=not conserverie["en_panne"])
        else:
            mettre_a_jour_moral(conserveur, salaire_paye=False, machine_ok=not conserverie["en_panne"])
    if conserverie["possede"]:
        argent = max(0, argent - conserverie["entretien"])
        historique.append((jour, f"Entretien {conserverie['nom']}", -conserverie["entretien"]))


def action_conserveur_auto():
    if not conserveur["actif"] or not conserverie["possede"] or conserverie["en_panne"]:
        return
    cap = int(conserverie["capacite_jour"] * _efficacite_reelle(conserveur))
    produit, _ = produire_conserves(cap)
    if produit > 0:
        conserveur["jours_travailles"] = conserveur.get("jours_travailles", 0) + 1
        historique.append((jour, f"{conserveur['nom']} produit conserves x{produit}", 0))


def action_atelier_conserves():
    global argent, stock_conserves
    while True:
        effacer()
        titre_bloc("  CONSERVERIE — POISSON + SEL → CONSERVES  ", C.CYAN)

        panne_txt = f"  {C.ROUGE}⚠ EN PANNE{C.RESET}" if conserverie["en_panne"] else ""
        print(f"\n  {C.BOLD}Conserverie :{C.RESET} ", end="")
        if conserverie["possede"]:
            usure_pct = int(conserverie["usure"] / conserverie["usure_max"] * 100)
            print(
                f"{conserverie['emoji']} {C.BOLD}{conserverie['nom']}{C.RESET}{panne_txt}\n"
                f"    Rendement : {C.CYAN}{conserverie['poisson_par_boite']} poisson + {conserverie['sel_par_boite']} sel → 1 boite{C.RESET}  │  "
                f"Cap. : {conserverie['capacite_jour']}/j  │  Usure : {barre_progression(usure_pct, 100, 10, C.ROUGE)}"
            )
        else:
            print(f"{C.GRIS}Aucune{C.RESET}")

        print(f"  {C.BOLD}Conserveur :{C.RESET} ", end="")
        if conserveur["actif"]:
            mc = _moral_couleur(conserveur["moral"])
            print(f"{C.BOLD}{conserveur['nom']}{C.RESET}  │  Moral : {mc}{conserveur['moral']}%{C.RESET}  │  Exp : {conserveur['jours_travailles']}j  │  Salaire : {C.ROUGE}{conserveur['salaire']} €/j{C.RESET}")
        else:
            print(f"{C.GRIS}Aucun{C.RESET}")

        print(f"\n  🐟 Poisson : {C.JAUNE}{stock.get('poisson',0)}{C.RESET}  │  🧂 Sel : {C.JAUNE}{stock.get('sel',0)}{C.RESET}  │  🥫 Conserves : {C.JAUNE}{stock_conserves}{C.RESET} ({C.VERT}{prix_conserves} €{C.RESET})")

        ligne("─", 64, C.GRIS)
        print(f"  {C.CYAN}[1]{C.RESET}  Acheter une conserverie")
        print(f"  {C.ROUGE}[2]{C.RESET}  Vendre la conserverie")
        print(f"  {C.JAUNE}[3]{C.RESET}  Ameliorer la conserverie")
        print(f"  {C.ROUGE}[4]{C.RESET}  Reparer la conserverie")
        print(f"  {C.VERT}[5]{C.RESET}  Embaucher un conserveur")
        print(f"  {C.ROUGE}[6]{C.RESET}  Licencier le conserveur")
        print(f"  {C.JAUNE}[7]{C.RESET}  Produire manuellement")
        print(f"  {C.VERT}[8]{C.RESET}  Vendre les conserves")
        print(f"  {C.GRIS}[0]{C.RESET}  Retour")
        ligne("─", 64, C.GRIS)
        print(f"  {C.BOLD}Choix : {C.RESET}", end="")

        choix = input().strip()

        if choix == "1":
            _acheter_outil(conserverie, CONSERVERIES, ["poisson_par_boite", "sel_par_boite", "capacite_jour", "entretien"], "Conserverie", C.CYAN)
        elif choix == "2":
            _vendre_outil(conserverie, CONSERVERIES, "Conserverie")
        elif choix == "3":
            ameliorer_machine(conserverie, CONSERVERIES, ["poisson_par_boite", "sel_par_boite", "capacite_jour", "entretien"], "Conserverie")
        elif choix == "4":
            reparer_machine(conserverie, CONSERVERIES, "Conserverie")
        elif choix == "5":
            _embaucher_ouvrier(conserveur, config_conserveur, conserverie, "Conserveur", C.CYAN)
        elif choix == "6":
            _licencier_ouvrier(conserveur, "Conserveur")
        elif choix == "7":
            _produire_manuel(produire_conserves, conserverie, "conserves",
                             f"{conserverie['poisson_par_boite']} poisson + {conserverie['sel_par_boite']} sel → 1 boite",
                             stock_conserves, prix_conserves)
        elif choix == "8":
            _vendre_transforme("conserves", stock_conserves, prix_conserves,
                               offre_demande_conserves, "stock_conserves", "Conserves")
        elif choix == "0":
            return
        else:
            print(f"  {C.ROUGE}Choix invalide.{C.RESET}")
            input(f"  {C.GRIS}[ENTREE]{C.RESET}")


# ══════════════════════════════════════════════
#  TISSU BRODÉ (épices + soie → tissu brodé)
# ══════════════════════════════════════════════

def config_brodeur(niveau):
    if niveau == 1:
        return {"salaire": 11, "efficacite": 0.60, "nom": "Apprenti brodeur",  "cout": 70}
    elif niveau == 2:
        return {"salaire": 22, "efficacite": 0.80, "nom": "Brodeur confirme",  "cout": 190}
    elif niveau == 3:
        return {"salaire": 40, "efficacite": 1.00, "nom": "Maitre brodeur",    "cout": 420}
    return None


def mettre_a_jour_prix_tissu():
    global prix_tissu, offre_demande_tissu
    offre_demande_tissu["offre"]   = limiter(offre_demande_tissu["offre"]   + random.randint(-8, 7))
    offre_demande_tissu["demande"] = limiter(offre_demande_tissu["demande"] + random.randint(-5, 12))
    if evenement_actif and evenement_actif.get("cible") in ("soie", "epices"):
        offre_demande_tissu["demande"] = limiter(offre_demande_tissu["demande"] + 15)
    saison = get_saison()
    if saison["nom"] in ("Automne", "Hiver"):
        offre_demande_tissu["demande"] = limiter(offre_demande_tissu["demande"] + 8)
    ratio   = offre_demande_tissu["demande"] / offre_demande_tissu["offre"]
    facteur = max(0.65, min(2.0, 1 + (ratio - 1) * 0.50))
    prix_tissu = max(40, round(TISSU_PRIX_BASE * facteur))


def produire_tissu(qte_voulue):
    global stock_tissu, tissu_produit_total
    if not atelier_tissu["possede"] or atelier_tissu["en_panne"]:
        return 0, "Atelier de broderie indisponible."
    soie_dispo   = stock.get("soie", 0)
    epices_dispo = stock.get("epices", 0)
    s_par_t = atelier_tissu["soie_par_tissu"]
    e_par_t = atelier_tissu["epices_par_tissu"]
    max_prod = min(qte_voulue, atelier_tissu["capacite_jour"],
                  soie_dispo // s_par_t, epices_dispo // e_par_t)
    if max_prod <= 0:
        return 0, f"Besoin {s_par_t} soie + {e_par_t} epices par tissu."
    stock["soie"]   -= max_prod * s_par_t
    stock["epices"] -= max_prod * e_par_t
    stock_tissu     += max_prod
    tissu_produit_total += max_prod
    panne = _incrementer_usure(atelier_tissu, max_prod)
    return max_prod, f"{max_prod} tissu(s) brode(s).{' ⚠ PANNE !' if panne else ''}"


def payer_brodeur_et_atelier():
    global argent
    if brodeur["actif"]:
        if argent >= brodeur["salaire"]:
            argent -= brodeur["salaire"]
            historique.append((jour, f"Salaire {brodeur['nom']}", -brodeur["salaire"]))
            mettre_a_jour_moral(brodeur, salaire_paye=True, machine_ok=not atelier_tissu["en_panne"])
        else:
            mettre_a_jour_moral(brodeur, salaire_paye=False, machine_ok=not atelier_tissu["en_panne"])
    if atelier_tissu["possede"]:
        argent = max(0, argent - atelier_tissu["entretien"])
        historique.append((jour, f"Entretien {atelier_tissu['nom']}", -atelier_tissu["entretien"]))


def action_brodeur_auto():
    if not brodeur["actif"] or not atelier_tissu["possede"] or atelier_tissu["en_panne"]:
        return
    cap = int(atelier_tissu["capacite_jour"] * _efficacite_reelle(brodeur))
    produit, _ = produire_tissu(cap)
    if produit > 0:
        brodeur["jours_travailles"] = brodeur.get("jours_travailles", 0) + 1
        historique.append((jour, f"{brodeur['nom']} brode tissu x{produit}", 0))


def action_atelier_tissu_brode():
    global argent, stock_tissu
    while True:
        effacer()
        titre_bloc("  BRODERIE — SOIE + ÉPICES → TISSU BRODÉ  ", C.MAGENTA)

        panne_txt = f"  {C.ROUGE}⚠ EN PANNE{C.RESET}" if atelier_tissu["en_panne"] else ""
        print(f"\n  {C.BOLD}Atelier :{C.RESET} ", end="")
        if atelier_tissu["possede"]:
            usure_pct = int(atelier_tissu["usure"] / atelier_tissu["usure_max"] * 100)
            print(
                f"{atelier_tissu['emoji']} {C.BOLD}{atelier_tissu['nom']}{C.RESET}{panne_txt}\n"
                f"    Rendement : {C.CYAN}{atelier_tissu['soie_par_tissu']} soie + {atelier_tissu['epices_par_tissu']} epices → 1 tissu{C.RESET}  │  "
                f"Usure : {barre_progression(usure_pct, 100, 10, C.ROUGE)}"
            )
        else:
            print(f"{C.GRIS}Aucun{C.RESET}")

        print(f"  {C.BOLD}Brodeur :{C.RESET} ", end="")
        if brodeur["actif"]:
            mc = _moral_couleur(brodeur["moral"])
            print(f"{C.BOLD}{brodeur['nom']}{C.RESET}  │  Moral : {mc}{brodeur['moral']}%{C.RESET}  │  Exp : {brodeur['jours_travailles']}j  │  Salaire : {C.ROUGE}{brodeur['salaire']} €/j{C.RESET}")
        else:
            print(f"{C.GRIS}Aucun{C.RESET}")

        print(f"\n  🧵 Soie : {C.JAUNE}{stock.get('soie',0)}{C.RESET}  │  🌶 Epices : {C.JAUNE}{stock.get('epices',0)}{C.RESET}  │  🪢 Tissu brode : {C.JAUNE}{stock_tissu}{C.RESET} ({C.VERT}{prix_tissu} €{C.RESET})")
        print(f"  Saison actuelle : {get_saison()['emoji']} {C.BOLD}{get_saison()['nom']}{C.RESET} — {C.GRIS}{get_saison()['desc']}{C.RESET}")

        ligne("─", 64, C.GRIS)
        print(f"  {C.MAGENTA}[1]{C.RESET}  Acheter un atelier de broderie")
        print(f"  {C.ROUGE}[2]{C.RESET}  Vendre l'atelier")
        print(f"  {C.JAUNE}[3]{C.RESET}  Ameliorer l'atelier")
        print(f"  {C.ROUGE}[4]{C.RESET}  Reparer l'atelier")
        print(f"  {C.VERT}[5]{C.RESET}  Embaucher un brodeur")
        print(f"  {C.ROUGE}[6]{C.RESET}  Licencier le brodeur")
        print(f"  {C.JAUNE}[7]{C.RESET}  Broder manuellement")
        print(f"  {C.VERT}[8]{C.RESET}  Vendre le tissu brode")
        print(f"  {C.GRIS}[0]{C.RESET}  Retour")
        ligne("─", 64, C.GRIS)
        print(f"  {C.BOLD}Choix : {C.RESET}", end="")

        choix = input().strip()

        if choix == "1":
            _acheter_outil(atelier_tissu, ATELIERS_TISSU, ["soie_par_tissu", "epices_par_tissu", "capacite_jour", "entretien"], "Atelier de broderie", C.MAGENTA)
        elif choix == "2":
            _vendre_outil(atelier_tissu, ATELIERS_TISSU, "Atelier de broderie")
        elif choix == "3":
            ameliorer_machine(atelier_tissu, ATELIERS_TISSU, ["soie_par_tissu", "epices_par_tissu", "capacite_jour", "entretien"], "Broderie")
        elif choix == "4":
            reparer_machine(atelier_tissu, ATELIERS_TISSU, "Broderie")
        elif choix == "5":
            _embaucher_ouvrier(brodeur, config_brodeur, atelier_tissu, "Brodeur", C.MAGENTA)
        elif choix == "6":
            _licencier_ouvrier(brodeur, "Brodeur")
        elif choix == "7":
            _produire_manuel(produire_tissu, atelier_tissu, "tissus brodes",
                             f"{atelier_tissu['soie_par_tissu']} soie + {atelier_tissu['epices_par_tissu']} epices → 1 tissu",
                             stock_tissu, prix_tissu)
        elif choix == "8":
            _vendre_transforme("tissu", stock_tissu, prix_tissu,
                               offre_demande_tissu, "stock_tissu", "Tissu brode")
        elif choix == "0":
            return
        else:
            print(f"  {C.ROUGE}Choix invalide.{C.RESET}")
            input(f"  {C.GRIS}[ENTREE]{C.RESET}")


# ══════════════════════════════════════════════
#  HELPERS GÉNÉRIQUES (ateliers partagés)
# ══════════════════════════════════════════════

def _acheter_outil(outil_dict, constantes, champs, label, couleur=C.CYAN):
    global argent
    effacer()
    titre_bloc(f"  ACHETER — {label.upper()}  ", couleur)
    if outil_dict["possede"]:
        print(f"\n  {C.JAUNE}Tu en possedes deja un.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    print(f"\n  {C.BOLD}Niveaux disponibles :{C.RESET}")
    ligne("─", 60, C.GRIS)
    coul = {1: C.VERT, 2: C.JAUNE, 3: C.MAGENTA}
    for niv, cfg in constantes.items():
        print(
            f"\n  {coul[niv]}{C.BOLD}[{niv}]{C.RESET} {cfg.get('emoji','')} {C.BOLD}{cfg['nom']}{C.RESET}\n"
            f"      Prix : {C.JAUNE}{cfg['cout']} €{C.RESET}  │  "
            f"Entretien : {C.ROUGE}{cfg['entretien']} €/j{C.RESET}  │  "
            f"Capacite : {C.VERT}{cfg['capacite_jour']}/j{C.RESET}\n"
            f"      {C.GRIS}{cfg['desc']}{C.RESET}"
        )
    ligne("─", 60, C.GRIS)
    print(f"  {C.GRIS}[0]{C.RESET} Annuler\n  → ", end="")
    try:
        choix = int(input())
    except ValueError:
        return
    if choix == 0 or choix not in constantes:
        return
    cfg = constantes[choix]
    if argent < cfg["cout"]:
        print(f"\n  {C.ROUGE}Fonds insuffisants.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    print(f"  Confirmer {C.BOLD}{cfg['nom']}{C.RESET} pour {C.JAUNE}{cfg['cout']} €{C.RESET} ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        return
    argent -= cfg["cout"]
    outil_dict["possede"] = True
    outil_dict["niveau"]  = choix
    outil_dict["nom"]     = cfg["nom"]
    outil_dict["emoji"]   = cfg.get("emoji", "")
    outil_dict["capacite_jour"] = cfg["capacite_jour"]
    outil_dict["entretien"]     = cfg["entretien"]
    outil_dict["usure"]    = 0
    outil_dict["en_panne"] = False
    for champ in champs:
        outil_dict[champ] = cfg[champ]
    historique.append((jour, f"Achat {cfg['nom']}", -cfg["cout"]))
    print(f"\n  {C.VERT}✔  {cfg['nom']} installe !{C.RESET}")
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


def _vendre_outil(outil_dict, constantes, label):
    global argent
    if not outil_dict["possede"]:
        print(f"\n  {C.GRIS}Aucun {label} a vendre.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    valeur = constantes[outil_dict["niveau"]]["cout"] // 2
    print(f"\n  Vendre {outil_dict['nom']} pour {C.JAUNE}{valeur} €{C.RESET} (50%) ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        return
    argent += valeur
    historique.append((jour, f"Vente {outil_dict['nom']}", valeur))
    for k in list(outil_dict.keys()):
        if isinstance(outil_dict[k], bool):
            outil_dict[k] = False
        elif isinstance(outil_dict[k], int):
            outil_dict[k] = 0
        elif isinstance(outil_dict[k], str):
            outil_dict[k] = "" if k not in ("nom",) else None
    outil_dict["possede"] = False
    outil_dict["nom"]     = None
    print(f"\n  {C.JAUNE}✔  Vendu pour {valeur} €.{C.RESET}")
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


def _embaucher_ouvrier(emp_dict, config_fn, outil_dict, label, couleur=C.CYAN):
    global argent
    effacer()
    titre_bloc(f"  EMBAUCHE — {label.upper()}  ", couleur)
    if emp_dict["actif"]:
        print(f"\n  {C.JAUNE}Tu as deja un {label} : {emp_dict['nom']}{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    if not outil_dict["possede"]:
        print(f"\n  {C.ROUGE}Aucun atelier installe.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    print(f"\n  {C.BOLD}Profils :{C.RESET}")
    ligne("─", 60, C.GRIS)
    coul = {1: C.VERT, 2: C.JAUNE, 3: C.MAGENTA}
    for niv in range(1, 4):
        cfg = config_fn(niv)
        print(f"  {coul[niv]}{C.BOLD}[{niv}]{C.RESET} {cfg['nom']}  │  Embauche {C.JAUNE}{cfg['cout']} €{C.RESET}  │  Salaire {C.ROUGE}{cfg['salaire']} €/j{C.RESET}  │  Efficacite {C.CYAN}{int(cfg['efficacite']*100)}%{C.RESET}")
    ligne("─", 60, C.GRIS)
    print(f"  {C.GRIS}[0]{C.RESET} Annuler\n  → ", end="")
    try:
        niv = int(input())
    except ValueError:
        return
    if niv == 0:
        return
    cfg = config_fn(niv)
    if cfg is None or argent < cfg["cout"]:
        print(f"\n  {C.ROUGE}Impossible.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    print(f"  Confirmer {C.BOLD}{cfg['nom']}{C.RESET} pour {C.JAUNE}{cfg['cout']} €{C.RESET} ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        return
    argent -= cfg["cout"]
    emp_dict.update({"actif": True, "niveau": niv, "salaire": cfg["salaire"],
                     "nom": cfg["nom"], "efficacite": cfg["efficacite"],
                     "moral": 100, "jours_travailles": 0, "salaires_impaye": 0})
    historique.append((jour, f"Embauche {cfg['nom']}", -cfg["cout"]))
    print(f"\n  {C.VERT}✔  {cfg['nom']} recrute !{C.RESET}")
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


def _licencier_ouvrier(emp_dict, label):
    effacer()
    titre_bloc(f"  LICENCIEMENT — {label.upper()}  ", C.ROUGE)
    if not emp_dict["actif"]:
        print(f"\n  {C.GRIS}Aucun {label} en poste.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    print(f"\n  Licencier {C.BOLD}{emp_dict['nom']}{C.RESET} ? (o/n) : ", end="")
    if input().strip().lower() != "o":
        return
    nom_tmp = emp_dict["nom"]
    emp_dict.update({"actif": False, "niveau": 0, "salaire": 0,
                     "nom": None, "moral": 100, "jours_travailles": 0, "salaires_impaye": 0})
    print(f"\n  {C.JAUNE}✔  {nom_tmp} licencie.{C.RESET}")
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


def _produire_manuel(fn_produire, outil_dict, label_prod, recette, stock_actuel, prix_actuel):
    effacer()
    if not outil_dict["possede"]:
        print(f"\n  {C.ROUGE}Aucun atelier installe.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    if outil_dict["en_panne"]:
        print(f"\n  {C.ROUGE}⚠ Atelier en panne ! Repare-le d'abord.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    print(f"\n  Recette : {C.CYAN}{recette}{C.RESET}")
    print(f"  En stock : {C.JAUNE}{stock_actuel}{C.RESET}  │  Prix actuel : {C.VERT}{prix_actuel} €{C.RESET}")
    print(f"  Quantite a produire : ", end="")
    try:
        qte = int(input())
    except ValueError:
        return
    if qte <= 0:
        return
    produit, msg = fn_produire(qte)
    if produit > 0:
        print(f"\n  {C.VERT}✔  {msg}{C.RESET}")
    else:
        print(f"\n  {C.ROUGE}✖  {msg}{C.RESET}")
    input(f"\n  {C.GRIS}[ENTREE]{C.RESET}")


def _vendre_transforme(cle_stock, stock_actuel, prix_actuel, od, nom_global_stock, label):
    """Vente générique d'un produit transformé depuis un menu atelier."""
    global argent, stock_conserves, stock_tissu
    if stock_actuel <= 0:
        print(f"\n  {C.ROUGE}Aucun {label} en stock.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    print(f"\n  {label} : {C.JAUNE}{prix_actuel} €{C.RESET}  │  En stock : {C.CYAN}{stock_actuel}{C.RESET}")
    print(f"  O/D : Offre {C.CYAN}{od['offre']}{C.RESET} / Demande {C.MAGENTA}{od['demande']}{C.RESET}")
    print(f"  Quantite a vendre : ", end="")
    try:
        qte = int(input())
    except ValueError:
        return
    if qte <= 0 or qte > stock_actuel:
        print(f"  {C.ROUGE}Quantite invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTREE]{C.RESET}")
        return
    gain = qte * prix_actuel
    argent += gain
    if nom_global_stock == "stock_conserves":
        stock_conserves -= qte
    elif nom_global_stock == "stock_tissu":
        stock_tissu -= qte
    historique.append((jour, f"Vente {label} x{qte}", gain))
    print(f"\n  {C.VERT}✔  {qte} {label}(s) vendu(s) pour +{gain} €{C.RESET}")
    input(f"  {C.GRIS}[ENTREE]{C.RESET}")


# ══════════════════════════════════════════════
#  ÉCRANS
# ══════════════════════════════════════════════

def ecran_titre():
    effacer()
    print()
    time.sleep(0.2)

    logo = [
        f"{C.JAUNE}{C.BOLD}  ███╗   ███╗███████╗██████╗  ██████╗ █████╗ ████████╗ ██████╗ ██████╗ {C.RESET}",
        f"{C.JAUNE}{C.BOLD}  ████╗ ████║██╔════╝██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗{C.RESET}",
        f"{C.JAUNE}{C.BOLD}  ██╔████╔██║█████╗  ██████╔╝██║     ███████║   ██║   ██║   ██║██████╔╝{C.RESET}",
        f"{C.JAUNE}{C.BOLD}  ██║╚██╔╝██║██╔══╝  ██╔══██╗██║     ██╔══██║   ██║   ██║   ██║██╔══██╗{C.RESET}",
        f"{C.JAUNE}{C.BOLD}  ██║ ╚═╝ ██║███████╗██║  ██║╚██████╗██║  ██║   ██║   ╚██████╔╝██║  ██║{C.RESET}",
        f"{C.JAUNE}{C.BOLD}  ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝{C.RESET}",
    ]

    for l in logo:
        print(l)
        pause(0.06)

    print()
    ligne("═")
    centre = "Jeu de commerce stratégique au tour par tour".center(64)
    print(f"{C.CYAN}{C.BOLD}{centre}{C.RESET}")
    centre2 = "Niveau NSI — Python pur".center(64)
    print(f"{C.GRIS}{centre2}{C.RESET}")
    ligne("═")
    print()

    infos = [
        f"  {C.VERT}●{C.RESET} Objectif  : accumuler {C.JAUNE}{C.BOLD}{OBJECTIF} €{C.RESET} en {JOURS_MAX} jours",
        f"  {C.CYAN}●{C.RESET} Capital   : {C.BOLD}{ARGENT_DEPART} €{C.RESET} de départ",
        f"  {C.MAGENTA}●{C.RESET} Produits  : {len(PRODUITS)} marchandises à trader",
        f"  {C.ROUGE}●{C.RESET} Danger    : événements aléatoires et marchés volatils",
        f"  {C.JAUNE}●{C.RESET} Nouveau   : système dynamique d'offre et de demande",
    ]

    for info in infos:
        taper(info, delai=0.008)
        pause(0.05)

    print()
    ligne()
    print(f"\n  {C.GRIS}Appuie sur{C.RESET} {C.BOLD}{C.BLANC}ENTRÉE{C.RESET} {C.GRIS}pour commencer…{C.RESET}")
    input()


def afficher_hud():
    largeur = 64
    patrimoine = patrimoine_total()
    patrimoine_avec_farine = patrimoine + valeur_farine() + stock_vetements * prix_vetements + valeur_bijoux()
    progression_obj = min(patrimoine_avec_farine, OBJECTIF)

    print()
    print(f"{C.CYAN}╔{'═'*62}╗{C.RESET}")

    jour_texte = f"JOUR {jour}/{JOURS_MAX}"
    titre_texte = "✦  MERCATOR  ✦"
    jours_restants = JOURS_MAX - jour
    alerte = f"{C.ROUGE}⚠ {jours_restants}j restants{C.RESET}" if jours_restants <= 5 else f"{C.GRIS}{jours_restants} jours restants{C.RESET}"

    print(f"{C.CYAN}║{C.RESET} {C.JAUNE}{C.BOLD}{jour_texte:<15}{C.RESET}{C.BLANC}{C.BOLD}{titre_texte:^30}{C.RESET}{alerte:>20} {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}╠{'═'*62}╣{C.RESET}")

    argent_couleur = C.VERT if argent > 50 else C.ROUGE
    stock_utilise = stock_total()
    stock_couleur = C.ROUGE if stock_utilise >= LIMITE_STOCK else C.CYAN

    arg_txt = f"{argent_couleur}{C.BOLD}  💰 Argent : {argent:>6} €{C.RESET}"
    stk_txt = f"{stock_couleur}  📦 Stock  : {stock_utilise}/{LIMITE_STOCK}{C.RESET}"
    val_txt = f"{C.GRIS}  💎 Stock marchand : {valeur_stock()} €{C.RESET}"
    if stock_farine > 0:
        val_txt += f"  {C.BLEU}🌫 Farine : {valeur_farine()} €{C.RESET}"

    saison = get_saison()
    print(f"  {saison['emoji']} {C.BOLD}{saison['nom']}{C.RESET}  {C.GRIS}{saison['desc']}{C.RESET}")

    print(f"{C.CYAN}║{C.RESET}{arg_txt:<40}{stk_txt:<30}{C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}{val_txt:<60} {C.CYAN}║{C.RESET}")

    barre = barre_progression(progression_obj, OBJECTIF, 30)
    obj_txt = f"  🎯 Objectif : {barre}  {C.JAUNE}{patrimoine_avec_farine}/{OBJECTIF} €{C.RESET}"
    print(f"{C.CYAN}║{C.RESET}{obj_txt}")

    print(f"{C.CYAN}╚{'═'*62}╝{C.RESET}")

    # Bandeau employe commercial
    if employe["actif"]:
        fiabilite_pct = int(employe["fiabilite"] * 100)
        print(
            f"  {C.MAGENTA}👤 Employe :{C.RESET} {C.BOLD}{employe['nom']}{C.RESET}  │  "
            f"Fiabilite : {C.CYAN}{fiabilite_pct}%{C.RESET}  │  "
            f"Salaire : {C.ROUGE}{employe['salaire']} €/jour{C.RESET}"
        )

    # Bandeau atelier farine
    if machine["possede"]:
        farine_info = (
            f"  {C.BLEU}🏭 Moulin :{C.RESET} {machine['emoji']} {C.BOLD}{machine['nom']}{C.RESET}  │  "
            f"🌫  Farine : {C.JAUNE}{stock_farine} sacs{C.RESET} ({C.VERT}{prix_farine} €/sac{C.RESET})"
        )
        if meunier["actif"]:
            farine_info += f"  │  {C.BLEU}Meunier : {meunier['nom']}{C.RESET}"
        print(farine_info)

    # Bandeau manufacture vêtements
    if metier_a_tisser["possede"]:
        vet_info = (
            f"  {C.MAGENTA}🏭 Manufacture :{C.RESET} {metier_a_tisser['emoji']} {C.BOLD}{metier_a_tisser['nom']}{C.RESET}  │  "
            f"👘 Vetements : {C.JAUNE}{stock_vetements}{C.RESET} ({C.VERT}{prix_vetements} €{C.RESET})"
        )
        if tisserand["actif"]:
            vet_info += f"  │  {C.MAGENTA}Tisserand : {tisserand['nom']}{C.RESET}"
        print(vet_info)

    # Bandeau orfévrerie
    if atelier_or["possede"]:
        bijou_info = (
            f"  {C.JAUNE}💍 Orfevrerie :{C.RESET} {atelier_or['emoji']} {C.BOLD}{atelier_or['nom']}{C.RESET}  │  "
            f"Bijoux : {C.JAUNE}{len(stock_bijoux)}{C.RESET} ({C.VERT}~{valeur_bijoux()} €{C.RESET})"
        )
        if orfèvre["actif"]:
            bijou_info += f"  │  {C.JAUNE}Orfèvre : {orfèvre['nom']}{C.RESET}"
        print(bijou_info)

    # Bandeau conserverie
    if conserverie["possede"]:
        etat_c = f"{C.ROUGE}⚠ PANNE{C.RESET}" if conserverie["en_panne"] else f"{C.VERT}OK{C.RESET}"
        c_info = (f"  {C.CYAN}🥫 Conserverie :{C.RESET} {conserverie['emoji']} {C.BOLD}{conserverie['nom']}{C.RESET} "
                  f"{etat_c}  │  Conserves : {C.JAUNE}{stock_conserves}{C.RESET} ({C.VERT}{prix_conserves} €{C.RESET})")
        print(c_info)

    # Bandeau broderie
    if atelier_tissu["possede"]:
        etat_b = f"{C.ROUGE}⚠ PANNE{C.RESET}" if atelier_tissu["en_panne"] else f"{C.VERT}OK{C.RESET}"
        b_info = (f"  {C.MAGENTA}🎀 Broderie :{C.RESET} {atelier_tissu['emoji']} {C.BOLD}{atelier_tissu['nom']}{C.RESET} "
                  f"{etat_b}  │  Tissu brode : {C.JAUNE}{stock_tissu}{C.RESET} ({C.VERT}{prix_tissu} €{C.RESET})")
        print(b_info)


def afficher_marche():
    saison = get_saison()
    print(f"\n  {C.BOLD}{C.BLANC}MARCHÉ DU JOUR{C.RESET}  {saison['emoji']} {C.BOLD}{saison['nom']}{C.RESET}  {C.GRIS}{saison['desc']}{C.RESET}")
    ligne("─", 88, C.GRIS)

    print(
        f"  {C.GRIS}"
        f"{'#':<4}"
        f"{'Produit':<14}"
        f"{'Prix':<10}"
        f"{'Var.':>8}"
        f"{'Offre':>8}"
        f"{'Demande':>10}"
        f"{'Tendance':>14}"
        f"{'Stock':>8}"
        f"{'Valeur':>10}"
        f"{C.RESET}"
    )

    ligne("─", 88, C.GRIS)

    for i, (cle, prod) in enumerate(PRODUITS.items(), 1):
        prix = prix_actuels[cle]
        qte = stock[cle]
        valeur = qte * prix
        pct = variation_prix(cle)
        fleche = fleche_variation(pct)

        offre = offre_demande[cle]["offre"]
        demande = offre_demande[cle]["demande"]
        tendance = tendance_marche(cle)

        if pct > 15:
            coul_prix = C.VERT + C.BOLD
        elif pct < -15:
            coul_prix = C.ROUGE + C.BOLD
        else:
            coul_prix = C.BLANC

        pct_str = f"{'+' if pct >= 0 else ''}{pct:.0f}%"

        print(
            f"  {C.JAUNE}{i}{C.RESET}   "
            f"{prod['emoji']} {prod['nom']:<11}"
            f"{coul_prix}{prix:>6} €{C.RESET}  "
            f"{fleche} {pct_str:>5}   "
            f"{C.CYAN}{offre:>5}{C.RESET}   "
            f"{C.MAGENTA}{demande:>7}{C.RESET}   "
            f"{tendance:>20}   "
            f"{C.CYAN}{qte:>4}{C.RESET}   "
            f"{C.GRIS}{valeur:>7} €{C.RESET}"
        )

    ligne("─", 88, C.GRIS)

    # Ligne farine séparée (produit transformé, non achetable sur le marché)
    if machine["possede"] or stock_farine > 0:
        pct_farine = ((prix_farine - FARINE_PRIX_BASE) / FARINE_PRIX_BASE) * 100
        fleche_f   = fleche_variation(pct_farine)
        pct_str_f  = f"{'+' if pct_farine >= 0 else ''}{pct_farine:.0f}%"
        coul_f     = C.VERT + C.BOLD if pct_farine > 10 else (C.ROUGE + C.BOLD if pct_farine < -10 else C.BLANC)
        valeur_f   = stock_farine * prix_farine

    ligne("─", 88, C.GRIS)

    # Ligne farine
    if machine["possede"] or stock_farine > 0:
        pct_farine = ((prix_farine - FARINE_PRIX_BASE) / FARINE_PRIX_BASE) * 100
        fleche_f   = fleche_variation(pct_farine)
        pct_str_f  = f"{'+' if pct_farine >= 0 else ''}{pct_farine:.0f}%"
        coul_f     = C.VERT + C.BOLD if pct_farine > 10 else (C.ROUGE + C.BOLD if pct_farine < -10 else C.BLANC)
        valeur_f   = stock_farine * prix_farine
        od_f       = offre_demande_farine
        tend_f     = tendance_farine()

        print(
            f"  {C.BLEU}🌫 {C.RESET}   "
            f"{'Farine':<13}"
            f"{coul_f}{prix_farine:>6} €{C.RESET}  "
            f"{fleche_f} {pct_str_f:>5}   "
            f"{C.CYAN}{od_f['offre']:>5}{C.RESET}   "
            f"{C.MAGENTA}{od_f['demande']:>7}{C.RESET}   "
            f"{tend_f:>20}   "
            f"{C.JAUNE}{stock_farine:>4}{C.RESET}   "
            f"{C.GRIS}{valeur_f:>7} €{C.RESET}"
        )

    # Ligne vêtements
    if metier_a_tisser["possede"] or stock_vetements > 0:
        pct_vet   = ((prix_vetements - VETEMENTS_PRIX_BASE) / VETEMENTS_PRIX_BASE) * 100
        fleche_v  = fleche_variation(pct_vet)
        pct_str_v = f"{'+' if pct_vet >= 0 else ''}{pct_vet:.0f}%"
        coul_v    = C.VERT + C.BOLD if pct_vet > 10 else (C.ROUGE + C.BOLD if pct_vet < -10 else C.BLANC)
        valeur_v  = stock_vetements * prix_vetements
        od_v      = offre_demande_vetements
        tend_v    = tendance_vetements()

        print(
            f"  {C.MAGENTA}👘{C.RESET}   "
            f"{'Vetements':<13}"
            f"{coul_v}{prix_vetements:>6} €{C.RESET}  "
            f"{fleche_v} {pct_str_v:>5}   "
            f"{C.CYAN}{od_v['offre']:>5}{C.RESET}   "
            f"{C.MAGENTA}{od_v['demande']:>7}{C.RESET}   "
            f"{tend_v:>20}   "
            f"{C.JAUNE}{stock_vetements:>4}{C.RESET}   "
            f"{C.GRIS}{valeur_v:>7} €{C.RESET}"
        )

    ligne("─", 88, C.GRIS)


def afficher_evenement():
    if evenement_actif is None:
        return

    ev = evenement_actif

    if ev["argent"] > 0:
        couleur = C.FOND_VERT
    elif ev["argent"] < 0 or ev["perte_stock"] > 0:
        couleur = C.FOND_ROUGE
    elif ev["mult"] > 1.1:
        couleur = C.FOND_JAUNE
    else:
        couleur = C.FOND_BLEU

    print()
    print(f"  {couleur}{C.BLANC}{C.BOLD}  EVENEMENT DU JOUR  {C.RESET}")
    print(f"  {C.BOLD}{ev['msg']}{C.RESET}")

    if ev["argent"] != 0:
        signe = "+" if ev["argent"] > 0 else ""
        print(f"  → Effet : {C.JAUNE}{signe}{ev['argent']} €{C.RESET}")

    if ev["perte_stock"] > 0:
        print(f"  → {C.ROUGE}Perte de {int(ev['perte_stock'] * 100)}% de chaque stock{C.RESET}")

    if ev["cible"] is not None:
        nom = PRODUITS[ev["cible"]]["nom"]
        print(f"  → Marche touche : {C.CYAN}{nom}{C.RESET}")


def afficher_menu():
    print(f"\n  {C.BOLD}{C.BLANC}ACTIONS{C.RESET}")
    ligne("─", 64, C.GRIS)

    options = [
        (f"{C.VERT}[A]{C.RESET}", "Acheter une marchandise"),
        (f"{C.ROUGE}[V]{C.RESET}", "Vendre une marchandise"),
        (f"{C.JAUNE}[S]{C.RESET}", "Voir les statistiques"),
        (f"{C.CYAN}[J]{C.RESET}", "Passer au jour suivant"),
        (f"{C.GRIS}[Q]{C.RESET}", "Abandonner la partie"),
    ]

    for touche, desc in options:
        print(f"  {touche}  {desc}")

    # Options employe commercial
    if employe["actif"]:
        fiabilite_pct = int(employe["fiabilite"] * 100)
        print(
            f"  {C.ROUGE}[L]{C.RESET}  Licencier l'employe  "
            f"{C.GRIS}({employe['nom']} — {fiabilite_pct}% — {employe['salaire']} €/j){C.RESET}"
        )
    else:
        print(f"  {C.MAGENTA}[E]{C.RESET}  Embaucher un employe commercial")

    # Atelier farine
    if machine["possede"]:
        print(
            f"  {C.BLEU}[T]{C.RESET}  Moulin  "
            f"{C.GRIS}({machine['emoji']} {machine['nom']} — {stock_farine} sac(s) farine){C.RESET}"
        )
    else:
        print(f"  {C.BLEU}[T]{C.RESET}  Moulin  {C.GRIS}(aucune machine — ble → farine){C.RESET}")

    # Manufacture vêtements
    if metier_a_tisser["possede"]:
        print(
            f"  {C.MAGENTA}[U]{C.RESET}  Manufacture  "
            f"{C.GRIS}({metier_a_tisser['emoji']} {metier_a_tisser['nom']} — {stock_vetements} vetement(s)){C.RESET}"
        )
    else:
        print(f"  {C.MAGENTA}[U]{C.RESET}  Manufacture  {C.GRIS}(aucun metier — soie → vetements){C.RESET}")

    # Orfévrerie
    if atelier_or["possede"]:
        print(
            f"  {C.JAUNE}[X]{C.RESET}  Orfevrerie  "
            f"{C.GRIS}({atelier_or['emoji']} {atelier_or['nom']} — {len(stock_bijoux)} bijou(x) ~{valeur_bijoux()} €){C.RESET}"
        )
    else:
        print(f"  {C.JAUNE}[X]{C.RESET}  Orfevrerie  {C.GRIS}(aucun atelier — or → bijoux → encheres){C.RESET}")

    # Conserverie
    if conserverie["possede"]:
        etat = "⚠PANNE" if conserverie["en_panne"] else "OK"
        print(f"  {C.CYAN}[C]{C.RESET}  Conserverie  {C.GRIS}({conserverie['nom']} {etat} — {stock_conserves} boite(s)){C.RESET}")
    else:
        print(f"  {C.CYAN}[C]{C.RESET}  Conserverie  {C.GRIS}(poisson + sel → conserves){C.RESET}")

    # Broderie
    if atelier_tissu["possede"]:
        etat = "⚠PANNE" if atelier_tissu["en_panne"] else "OK"
        print(f"  {C.MAGENTA}[B]{C.RESET}  Broderie  {C.GRIS}({atelier_tissu['nom']} {etat} — {stock_tissu} tissu(s)){C.RESET}")
    else:
        print(f"  {C.MAGENTA}[B]{C.RESET}  Broderie  {C.GRIS}(soie + epices → tissu brode){C.RESET}")

    # Concurrents
    print(f"\n  {C.GRIS}Concurrents actifs : ", end="")
    for conc in concurrents:
        print(f"{conc['emoji']} {conc['nom']} ({conc['capital']} €)  ", end="")
    print(C.RESET)

    ligne("─", 64, C.GRIS)
    print(f"  {C.BOLD}Choix : {C.RESET}", end="")


# ──────────────────────────────────────────────
#  ACTIONS DU JOUEUR
# ──────────────────────────────────────────────

def choisir_produit(action="acheter"):
    noms = list(PRODUITS.keys())

    print(f"\n  Quel produit veux-tu {action} ?")

    for i, cle in enumerate(noms, 1):
        prod = PRODUITS[cle]
        offre = offre_demande[cle]["offre"]
        demande = offre_demande[cle]["demande"]

        print(
            f"  {C.JAUNE}{i}{C.RESET} - "
            f"{prod['emoji']} {prod['nom']} "
            f"({prix_actuels[cle]} €) "
            f"{C.GRIS}| Offre {offre} / Demande {demande}{C.RESET}"
        )

    print(f"  {C.GRIS}0{C.RESET} - Annuler")
    print(f"  → ", end="")

    try:
        choix = int(input())
    except ValueError:
        return None

    if choix == 0:
        return None

    if 1 <= choix <= len(noms):
        return noms[choix - 1]

    print(f"  {C.ROUGE}Choix invalide.{C.RESET}")
    return None


def action_acheter():
    global argent

    cle = choisir_produit("acheter")

    if cle is None:
        return

    prod = PRODUITS[cle]
    prix = prix_actuels[cle]
    espace_dispo = LIMITE_STOCK - stock_total()
    max_achetable = min(argent // prix, espace_dispo)

    if max_achetable <= 0:
        print(f"  {C.ROUGE}Impossible d'acheter : stock plein ou argent insuffisant.{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    print(f"\n  {prod['emoji']} {C.BOLD}{prod['nom']}{C.RESET} — {C.JAUNE}{prix} € l'unité{C.RESET}")
    print(f"  Marché : Offre {C.CYAN}{offre_demande[cle]['offre']}{C.RESET} / Demande {C.MAGENTA}{offre_demande[cle]['demande']}{C.RESET}")
    print(f"  Tu peux acheter jusqu'à {C.CYAN}{max_achetable}{C.RESET} unité(s).")
    print(f"  Quantité : ", end="")

    try:
        quantite = int(input())
    except ValueError:
        print(f"  {C.ROUGE}Valeur invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    if quantite <= 0:
        print(f"  {C.ROUGE}Quantité doit être positive.{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    cout = quantite * prix

    if cout > argent:
        print(f"  {C.ROUGE}Pas assez d'argent ! Il te faut {cout} €, tu as {argent} €.{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    if stock_total() + quantite > LIMITE_STOCK:
        print(f"  {C.ROUGE}Stock insuffisant ! Espace disponible : {espace_dispo} unité(s).{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    argent -= cout
    stock[cle] += quantite

    modifier_marche_apres_transaction(cle, "achat", quantite)

    historique.append((jour, f"Achat {prod['nom']} x{quantite}", -cout))

    print(f"\n  {C.VERT}✔  Achat réussi !{C.RESET} {quantite}x {prod['emoji']} pour {C.ROUGE}-{cout} €{C.RESET}")
    print(f"  {C.GRIS}Le marché réagit : la demande augmente, l'offre baisse.{C.RESET}")

    input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")


def action_vendre():
    global argent, stock_farine, stock_vetements, stock_bijoux

    possedes    = {cle: qte for cle, qte in stock.items() if qte > 0}
    a_farine    = stock_farine > 0
    a_vetements = stock_vetements > 0
    a_bijoux    = len(stock_bijoux) > 0
    a_conserves = stock_conserves > 0
    a_tissu     = stock_tissu > 0

    if not possedes and not a_farine and not a_vetements and not a_bijoux and not a_conserves and not a_tissu:
        print(f"  {C.ROUGE}Tu n'as aucune marchandise à vendre !{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    noms = list(PRODUITS.keys())
    print(f"\n  Que veux-tu vendre ?")

    for i, cle in enumerate(noms, 1):
        prod = PRODUITS[cle]
        qte  = stock[cle]
        if qte == 0:
            print(f"  {C.GRIS}{i} - {prod['emoji']} {prod['nom']} (0 en stock){C.RESET}")
        else:
            print(
                f"  {C.JAUNE}{i}{C.RESET} - "
                f"{prod['emoji']} {prod['nom']} "
                f"({prix_actuels[cle]} €) "
                f"{C.GRIS}| stock : {qte}{C.RESET}"
            )

    idx_farine    = len(noms) + 1
    idx_vetements = len(noms) + 2
    idx_bijoux    = len(noms) + 3
    idx_conserves = len(noms) + 4
    idx_tissu     = len(noms) + 5

    if a_farine:
        print(f"  {C.BLEU}{idx_farine}{C.RESET} - 🌫  Farine ({prix_farine} €/sac) {C.GRIS}| stock : {stock_farine} sac(s){C.RESET}")
    if a_vetements:
        print(f"  {C.MAGENTA}{idx_vetements}{C.RESET} - 👘 Vetements ({prix_vetements} €) {C.GRIS}| stock : {stock_vetements}{C.RESET}")
    if a_bijoux:
        print(f"  {C.JAUNE}{idx_bijoux}{C.RESET} - 💍 Bijoux {C.GRIS}| {len(stock_bijoux)} bijou(x) — encheres recommandees{C.RESET}")
        for j, b in enumerate(stock_bijoux):
            print(f"       {C.GRIS}{j+1}) {QUALITE_NOMS[b['qualite']]} {b['nom']} ~{BIJOU_PRIX_BASE[b['qualite']]} €{C.RESET}")
    if a_conserves:
        print(f"  {C.CYAN}{idx_conserves}{C.RESET} - 🥫 Conserves ({prix_conserves} €/boite) {C.GRIS}| stock : {stock_conserves}{C.RESET}")
    if a_tissu:
        print(f"  {C.MAGENTA}{idx_tissu}{C.RESET} - 🎀 Tissu brode ({prix_tissu} €) {C.GRIS}| stock : {stock_tissu}{C.RESET}")

    print(f"  {C.GRIS}0{C.RESET} - Annuler")
    print(f"  → ", end="")

    try:
        choix = int(input())
    except ValueError:
        return
    if choix == 0:
        return

    # ── Vente farine ──────────────────────────────────────────────────────────
    if a_farine and choix == idx_farine:
        print(f"\n  🌫  {C.BOLD}Farine{C.RESET} — {C.JAUNE}{prix_farine} €/sac{C.RESET}")
        print(f"  En stock : {C.CYAN}{stock_farine}{C.RESET} sac(s)  (valeur : {stock_farine * prix_farine} €)")
        print(f"  Quantité à vendre : ", end="")
        try:
            quantite = int(input())
        except ValueError:
            return
        if quantite <= 0 or quantite > stock_farine:
            print(f"  {C.ROUGE}Quantite invalide.{C.RESET}")
            input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
            return
        gain = quantite * prix_farine
        argent += gain
        stock_farine -= quantite
        modifier_marche_farine("vente", quantite)
        historique.append((jour, f"Vente Farine x{quantite}", gain))
        print(f"\n  {C.VERT}✔  {quantite} sac(s) vendu(s) pour {C.VERT}+{gain} €{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    # ── Vente vêtements ───────────────────────────────────────────────────────
    if a_vetements and choix == idx_vetements:
        print(f"\n  👘 {C.BOLD}Vetements{C.RESET} — {C.JAUNE}{prix_vetements} €{C.RESET}")
        print(f"  En stock : {C.CYAN}{stock_vetements}{C.RESET}  (valeur : {stock_vetements * prix_vetements} €)")
        print(f"  Quantite a vendre : ", end="")
        try:
            quantite = int(input())
        except ValueError:
            return
        if quantite <= 0 or quantite > stock_vetements:
            print(f"  {C.ROUGE}Quantite invalide.{C.RESET}")
            input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
            return
        gain = quantite * prix_vetements
        argent += gain
        stock_vetements -= quantite
        modifier_marche_vetements("vente", quantite)
        historique.append((jour, f"Vente Vetements x{quantite}", gain))
        print(f"\n  {C.VERT}✔  {quantite} vetement(s) vendu(s) pour {C.VERT}+{gain} €{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    # ── Vente bijou de gré à gré (alternative aux enchères) ──────────────────
    if a_bijoux and choix == idx_bijoux:
        print(f"\n  💍 {C.BOLD}Vente directe de bijou{C.RESET}  {C.GRIS}(ou utilise [X] → Encheres pour un meilleur prix){C.RESET}")
        print(f"  Quel bijou vendre ? (numéro) : ", end="")
        try:
            idx = int(input()) - 1
        except ValueError:
            return
        if not (0 <= idx < len(stock_bijoux)):
            print(f"  {C.ROUGE}Choix invalide.{C.RESET}")
            input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
            return
        bijou     = stock_bijoux[idx]
        prix_base = BIJOU_PRIX_BASE[bijou["qualite"]]
        # Vente directe : 70% du prix de base (le marché rogne la marge)
        prix_direct = int(prix_base * 0.70)
        print(
            f"\n  {QUALITE_NOMS[bijou['qualite']]} {C.BOLD}{bijou['nom']}{C.RESET}\n"
            f"  Prix de vente directe : {C.ROUGE}{prix_direct} €{C.RESET}  "
            f"{C.GRIS}(valeur estimee : {prix_base} € — vente aux encheres recommandee){C.RESET}"
        )
        print(f"  Confirmer ? (o/n) : ", end="")
        if input().strip().lower() != "o":
            return
        stock_bijoux.pop(idx)
        argent += prix_direct
        historique.append((jour, f"Vente directe {bijou['nom']}", prix_direct))
        print(f"\n  {C.VERT}✔  Bijou vendu pour {prix_direct} €.{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    # ── Vente conserves ───────────────────────────────────────────────────────
    if a_conserves and choix == idx_conserves:
        print(f"\n  🥫 {C.BOLD}Conserves{C.RESET} — {C.JAUNE}{prix_conserves} €/boite{C.RESET}")
        print(f"  En stock : {C.CYAN}{stock_conserves}{C.RESET}  (valeur : {stock_conserves * prix_conserves} €)")
        print(f"  Quantite a vendre : ", end="")
        try:
            quantite = int(input())
        except ValueError:
            return
        if quantite <= 0 or quantite > stock_conserves:
            print(f"  {C.ROUGE}Quantite invalide.{C.RESET}")
            input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
            return
        gain = quantite * prix_conserves
        argent += gain
        stock_conserves -= quantite
        historique.append((jour, f"Vente Conserves x{quantite}", gain))
        print(f"\n  {C.VERT}✔  {quantite} boite(s) vendues pour +{gain} €{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    # ── Vente tissu brodé ─────────────────────────────────────────────────────
    if a_tissu and choix == idx_tissu:
        print(f"\n  🎀 {C.BOLD}Tissu brode{C.RESET} — {C.JAUNE}{prix_tissu} €{C.RESET}")
        print(f"  En stock : {C.CYAN}{stock_tissu}{C.RESET}  (valeur : {stock_tissu * prix_tissu} €)")
        print(f"  Quantite a vendre : ", end="")
        try:
            quantite = int(input())
        except ValueError:
            return
        if quantite <= 0 or quantite > stock_tissu:
            print(f"  {C.ROUGE}Quantite invalide.{C.RESET}")
            input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
            return
        gain = quantite * prix_tissu
        argent += gain
        stock_tissu -= quantite
        historique.append((jour, f"Vente Tissu brode x{quantite}", gain))
        print(f"\n  {C.VERT}✔  {quantite} tissu(s) vendu(s) pour +{gain} €{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    # Vente marchandise normale
    if not (1 <= choix <= len(noms)):
        print(f"  {C.ROUGE}Choix invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    cle  = noms[choix - 1]
    prod = PRODUITS[cle]
    prix = prix_actuels[cle]
    en_stock = stock[cle]

    if en_stock == 0:
        print(f"  {C.ROUGE}Tu n'as pas de {prod['nom']} en stock.{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    print(f"\n  {prod['emoji']} {C.BOLD}{prod['nom']}{C.RESET} — {C.JAUNE}{prix} € l'unité{C.RESET}")
    print(f"  Marché : Offre {C.CYAN}{offre_demande[cle]['offre']}{C.RESET} / Demande {C.MAGENTA}{offre_demande[cle]['demande']}{C.RESET}")
    print(f"  En stock : {C.CYAN}{en_stock}{C.RESET} unité(s) (valeur : {en_stock * prix} €)")
    print(f"  Quantité à vendre : ", end="")

    try:
        quantite = int(input())
    except ValueError:
        print(f"  {C.ROUGE}Valeur invalide.{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    if quantite <= 0:
        print(f"  {C.ROUGE}Quantité doit être positive.{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    if quantite > en_stock:
        print(f"  {C.ROUGE}Tu n'as que {en_stock} unité(s) de {prod['nom']}.{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    gain = quantite * prix
    argent += gain
    stock[cle] -= quantite

    modifier_marche_apres_transaction(cle, "vente", quantite)

    historique.append((jour, f"Vente {prod['nom']} x{quantite}", gain))

    print(f"\n  {C.VERT}✔  Vente réussie !{C.RESET} {quantite}x {prod['emoji']} pour {C.VERT}+{gain} €{C.RESET}")
    print(f"  {C.GRIS}Le marché réagit : l'offre augmente, la demande baisse légèrement.{C.RESET}")

    input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")


def action_statistiques():
    effacer()
    titre_bloc("  STATISTIQUES  ")

    val_farine_v  = valeur_farine()
    val_vetements = stock_vetements * prix_vetements
    patrimoine_complet = patrimoine_total() + val_farine_v + val_vetements
    print(f"\n  {C.BOLD}Patrimoine total   {C.RESET}: {C.JAUNE}{C.BOLD}{patrimoine_complet} €{C.RESET}  {C.GRIS}(marche + farine + vetements){C.RESET}")
    print(f"  {C.BOLD}Argent disponible  {C.RESET}: {C.VERT}{argent} €{C.RESET}")
    print(f"  {C.BOLD}Stock marchand     {C.RESET}: {C.CYAN}{valeur_stock()} €{C.RESET}  {C.GRIS}(farine/vetements exclus){C.RESET}")
    print(f"  {C.BOLD}Farine en stock    {C.RESET}: {C.BLEU}{stock_farine} sac(s){C.RESET} → {C.VERT}{val_farine_v} €{C.RESET} a {prix_farine} €/sac")
    print(f"  {C.BOLD}Vetements en stock {C.RESET}: {C.MAGENTA}{stock_vetements}{C.RESET} → {C.VERT}{val_vetements} €{C.RESET} a {prix_vetements} €")
    print(f"  {C.BOLD}Jours ecoules      {C.RESET}: {jour}/{JOURS_MAX}")
    print(f"  {C.BOLD}Objectif           {C.RESET}: {OBJECTIF} € {barre_progression(patrimoine_complet, OBJECTIF, 30)}")

    print(f"\n  {C.BOLD}Etat economique des ressources :{C.RESET}")
    ligne("─", 64, C.GRIS)

    for cle, prod in PRODUITS.items():
        offre   = offre_demande[cle]["offre"]
        demande = offre_demande[cle]["demande"]
        facteur = facteur_offre_demande(cle)
        tendance = tendance_marche(cle)

        print(
            f"  {prod['emoji']} {prod['nom']:<10} │ "
            f"Offre : {C.CYAN}{offre:>3}{C.RESET} │ "
            f"Demande : {C.MAGENTA}{demande:>3}{C.RESET} │ "
            f"Facteur prix : {C.JAUNE}x{facteur:.2f}{C.RESET} │ "
            f"{tendance}"
        )

    # ── Section Atelier farine ──
    print(f"\n  {C.BOLD}Moulin (ble → farine) :{C.RESET}")
    ligne("─", 64, C.GRIS)

    if machine["possede"]:
        print(f"  Machine        : {machine['emoji']} {C.BOLD}{machine['nom']}{C.RESET}")
        print(f"  Rendement      : {C.CYAN}{machine['ble_par_farine']} ble → 1 farine{C.RESET}  │  Capacite : {C.CYAN}{machine['capacite_jour']} sacs/jour{C.RESET}")
        print(f"  Entretien      : {C.ROUGE}{machine['entretien']} €/jour{C.RESET}")
        print(f"  O/D farine     : Offre {C.CYAN}{offre_demande_farine['offre']}{C.RESET} / Demande {C.MAGENTA}{offre_demande_farine['demande']}{C.RESET}  │  {tendance_farine()}")
        print(f"  Farine produite (total) : {C.JAUNE}{farine_produite_total} sac(s){C.RESET}")
    else:
        print(f"  {C.GRIS}Aucune machine. Accede au Moulin [T] pour en acheter une.{C.RESET}")

    if meunier["actif"]:
        print(f"  Meunier        : {C.BOLD}{meunier['nom']}{C.RESET}  │  Efficacite : {C.CYAN}{int(meunier['efficacite']*100)}%{C.RESET}  │  Salaire : {C.ROUGE}{meunier['salaire']} €/j{C.RESET}")
    else:
        print(f"  {C.GRIS}Aucun meunier recrute.{C.RESET}")

    # ── Section Manufacture vêtements ──
    print(f"\n  {C.BOLD}Manufacture (soie → vetements) :{C.RESET}")
    ligne("─", 64, C.GRIS)

    if metier_a_tisser["possede"]:
        print(f"  Metier         : {metier_a_tisser['emoji']} {C.BOLD}{metier_a_tisser['nom']}{C.RESET}")
        print(f"  Rendement      : {C.CYAN}{metier_a_tisser['soie_par_vetement']} soie → 1 vetement{C.RESET}  │  Capacite : {C.CYAN}{metier_a_tisser['capacite_jour']}/jour{C.RESET}")
        print(f"  Entretien      : {C.ROUGE}{metier_a_tisser['entretien']} €/jour{C.RESET}")
        print(f"  O/D vetements  : Offre {C.CYAN}{offre_demande_vetements['offre']}{C.RESET} / Demande {C.MAGENTA}{offre_demande_vetements['demande']}{C.RESET}  │  {tendance_vetements()}")
        print(f"  Vetements produits (total) : {C.JAUNE}{vetements_produits_total}{C.RESET}")
    else:
        print(f"  {C.GRIS}Aucun metier. Accede a la Manufacture [U] pour en acheter un.{C.RESET}")

    if tisserand["actif"]:
        print(f"  Tisserand      : {C.BOLD}{tisserand['nom']}{C.RESET}  │  Efficacite : {C.CYAN}{int(tisserand['efficacite']*100)}%{C.RESET}  │  Salaire : {C.ROUGE}{tisserand['salaire']} €/j{C.RESET}")
    else:
        print(f"  {C.GRIS}Aucun tisserand recrute.{C.RESET}")

    print(f"\n  {C.BOLD}Dernieres transactions :{C.RESET}")
    ligne("─", 64, C.GRIS)

    dernieres = historique[-10:] if len(historique) >= 10 else historique

    if not dernieres:
        print(f"  {C.GRIS}Aucune transaction.{C.RESET}")

    for j, action, montant in reversed(dernieres):
        if montant == 0:
            couleur, signe = C.GRIS, " "
        elif montant > 0:
            couleur, signe = C.VERT, "+"
        else:
            couleur, signe = C.ROUGE, ""
        print(f"  Jour {j:>2} │ {action:<35} │ {couleur}{signe}{montant} €{C.RESET}")

    ligne("─", 64, C.GRIS)

    input(f"\n  {C.GRIS}[ENTREE] pour revenir{C.RESET}")


def appliquer_evenement(ev):
    global argent

    argent = max(0, argent + ev["argent"])

    if ev["perte_stock"] > 0:
        for cle in stock:
            perte = int(stock[cle] * ev["perte_stock"])
            stock[cle] = max(0, stock[cle] - perte)


# ──────────────────────────────────────────────
#  ÉCRAN FIN DE PARTIE
# ──────────────────────────────────────────────

def ecran_fin(victoire):
    effacer()
    print()

    if victoire:
        couleur = C.VERT
        texte = "VICTOIRE !"
        sous = f"Tu as atteint {patrimoine_total()} € — objectif dépassé !"
        art = [
            f"  {C.JAUNE}★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★{C.RESET}",
            f"  {C.VERT}{C.BOLD}       Félicitations, marchand !{C.RESET}",
            f"  {C.JAUNE}★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★{C.RESET}",
        ]
    else:
        couleur = C.ROUGE
        texte = "DÉFAITE"
        sous = f"Patrimoine final : {patrimoine_total()} € / {OBJECTIF} €"
        art = [
            f"  {C.ROUGE}✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖{C.RESET}",
            f"  {C.ROUGE}{C.BOLD}    Le commerce ne pardonne pas…{C.RESET}",
            f"  {C.ROUGE}✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖ ✖{C.RESET}",
        ]

    titre_bloc(f"  ✦  {texte}  ✦  ", couleur)
    print()

    for l in art:
        taper(l, delai=0.005)

    print()
    ligne()
    print(f"  {C.BOLD}{sous}{C.RESET}")
    print(f"  Jours joués    : {jour}")
    print(f"  Transactions   : {len(historique)}")
    print(f"  Argent liquide : {argent} €")
    print(f"  Valeur stock   : {valeur_stock()} €")
    ligne()

    print(f"\n  {C.GRIS}Rejouer ? (o/n) : {C.RESET}", end="")
    rep = input().strip().lower()

    return rep == "o"


# ──────────────────────────────────────────────
#  BOUCLE PRINCIPALE
# ──────────────────────────────────────────────

def reinitialiser():
    global argent, stock, prix_actuels, offre_demande, jour, historique, evenement_actif
    global employe, meunier, machine, stock_farine, prix_farine, farine_produite_total
    global tisserand, metier_a_tisser, stock_vetements, prix_vetements, vetements_produits_total
    global offre_demande_farine, offre_demande_vetements
    global stock_bijoux, bijoux_produits_total

    argent = ARGENT_DEPART
    stock = {}
    prix_actuels = {}
    offre_demande = {}
    jour = 1
    historique = []
    evenement_actif = None

    employe.update({"actif": False, "niveau": 0, "salaire": 0,
                    "cout_embauche": 0, "nom": None, "fiabilite": 0.0})
    meunier.update({"actif": False, "niveau": 0, "salaire": 0,
                    "nom": None, "efficacite": 0.0})
    machine.update({"possede": False, "niveau": 0, "nom": None,
                    "emoji": "", "ble_par_farine": 0,
                    "capacite_jour": 0, "entretien": 0})

    stock_farine           = 0
    prix_farine            = FARINE_PRIX_BASE
    farine_produite_total  = 0
    offre_demande_farine   = {"offre": 100, "demande": 100}

    tisserand.update({"actif": False, "niveau": 0, "salaire": 0,
                      "nom": None, "efficacite": 0.0})
    metier_a_tisser.update({"possede": False, "niveau": 0, "nom": None,
                             "emoji": "", "soie_par_vetement": 0,
                             "capacite_jour": 0, "entretien": 0})

    stock_vetements           = 0
    prix_vetements            = VETEMENTS_PRIX_BASE
    vetements_produits_total  = 0
    offre_demande_vetements   = {"offre": 100, "demande": 100}

    orfèvre.update({"actif": False, "niveau": 0, "salaire": 0, "nom": None, "talent": 0.0})
    atelier_or.update({"possede": False, "niveau": 0, "nom": None, "emoji": "",
                       "or_par_bijou": 0, "capacite_jour": 0, "entretien": 0,
                       "qualite_min": 0, "qualite_max": 0})
    stock_bijoux          = []
    bijoux_produits_total = 0

    # Reset conserverie
    conserveur.update({"actif": False, "niveau": 0, "salaire": 0, "nom": None,
                       "efficacite": 0.0, "moral": 100, "jours_travailles": 0, "salaires_impaye": 0})
    conserverie.update({"possede": False, "niveau": 0, "nom": None, "emoji": "",
                        "poisson_par_boite": 0, "sel_par_boite": 0, "capacite_jour": 0,
                        "entretien": 0, "usure": 0, "usure_max": 40, "en_panne": False})
    global stock_conserves, prix_conserves, conserves_produites_total
    global stock_tissu, prix_tissu, tissu_produit_total
    stock_conserves          = 0
    prix_conserves           = CONSERVES_PRIX_BASE
    conserves_produites_total = 0
    offre_demande_conserves.update({"offre": 100, "demande": 100})

    # Reset atelier tissu brodé
    brodeur.update({"actif": False, "niveau": 0, "salaire": 0, "nom": None,
                    "efficacite": 0.0, "moral": 100, "jours_travailles": 0, "salaires_impaye": 0})
    atelier_tissu.update({"possede": False, "niveau": 0, "nom": None, "emoji": "",
                          "soie_par_tissu": 0, "epices_par_tissu": 0, "capacite_jour": 0,
                          "entretien": 0, "usure": 0, "usure_max": 35, "en_panne": False})
    stock_tissu      = 0
    prix_tissu       = TISSU_PRIX_BASE
    tissu_produit_total = 0
    offre_demande_tissu.update({"offre": 100, "demande": 100})

    # Reset concurrents
    global concurrents
    concurrents = [dict(b) for b in CONCURRENTS_BASE]

    initialiser_prix()


def jouer():
    global jour, evenement_actif

    while True:
        evenement_actif = tirer_evenement()
        appliquer_evenement(evenement_actif)
        actualiser_offre_demande(evenement_actif)
        mettre_a_jour_prix(evenement_actif)
        mettre_a_jour_prix_farine()
        mettre_a_jour_prix_vetements()

        jour_termine = False

        while not jour_termine:
            effacer()
            afficher_hud()
            afficher_evenement()
            afficher_marche()
            afficher_menu()

            choix = input().strip().lower()

            if choix == "a":
                action_acheter()
            elif choix == "v":
                action_vendre()
            elif choix == "s":
                action_statistiques()
            elif choix == "t":
                action_atelier()
            elif choix == "u":
                action_atelier_vetements()
            elif choix == "x":
                action_atelier_or()
            elif choix == "c":
                action_atelier_conserves()
            elif choix == "b":
                action_atelier_tissu_brode()
            elif choix == "j":
                payer_employe()
                action_employe()
                payer_meunier_et_entretien()
                action_meunier_auto()
                payer_tisserand_et_metier()
                action_tisserand_auto()
                payer_orfevre_et_atelier()
                action_orfevre_auto()
                payer_conserveur_et_conserverie()
                action_conserveur_auto()
                payer_brodeur_et_atelier_tissu()
                action_brodeur_auto()
                mettre_a_jour_prix_conserves()
                mettre_a_jour_prix_tissu()
                jour_termine = True
                jour += 1
            elif choix == "q":
                print(f"\n  {C.GRIS}A bientot, marchand.{C.RESET}\n")
                return False
            elif choix == "e":
                embaucher_employe()
            elif choix == "l":
                licencier_employe()
            else:
                print(f"  {C.ROUGE}Choix invalide.{C.RESET}")
                input(f"  {C.GRIS}[ENTREE]{C.RESET}")

        patrimoine_reel = (patrimoine_total() + stock_farine * prix_farine
                           + stock_vetements * prix_vetements + valeur_bijoux()
                           + stock_conserves * prix_conserves + stock_tissu * prix_tissu)
        if patrimoine_reel >= OBJECTIF:
            return True
        if jour > JOURS_MAX:
            return False


# ──────────────────────────────────────────────
#  POINT D'ENTRÉE
# ──────────────────────────────────────────────

def main():
    if os.name == "nt":
        os.system("color")

    rejouer = True

    while rejouer:
        reinitialiser()
        ecran_titre()
        victoire = jouer()
        rejouer = ecran_fin(victoire)

    print(f"\n  {C.CYAN}Merci d'avoir joué à MERCATOR !{C.RESET}\n")


if __name__ == "__main__":
    main()