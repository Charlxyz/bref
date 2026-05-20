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

PRODUITS = {
    "ble":     {"nom": "Blé",       "prix_base": 8,  "volatilite": 0.3, "emoji": "🌾"},
    "soie":    {"nom": "Soie",      "prix_base": 25, "volatilite": 0.5, "emoji": "🧵"},
    "epices":  {"nom": "Épices",    "prix_base": 40, "volatilite": 0.6, "emoji": "🌶"},
    "or":      {"nom": "Or",        "prix_base": 80, "volatilite": 0.7, "emoji": "✨"},
    "poisson": {"nom": "Poisson",   "prix_base": 12, "volatilite": 0.4, "emoji": "🐟"},
}

employe = {
    "actif": False,
    "niveau": 0,
    "salaire": 0,
    "cout_embauche": 0,
    "fiabilite": 0.0,
}

EVENEMENTS = [
    {"msg": "⚡ Tempête ! Vos marchandises sont endommagées.",         "argent": 0,    "mult": 1.0,  "cible": None,      "perte_stock": 0.3},
    {"msg": "🔥 Incendie au marché ! Les prix flambent.",              "argent": 0,    "mult": 1.4,  "cible": "ble",     "perte_stock": 0},
    {"msg": "☀️  Bonne récolte ! Le blé est bradé.",                   "argent": 0,    "mult": 0.6,  "cible": "ble",     "perte_stock": 0},
    {"msg": "🏴‍☠️  Pirates ! Vous perdez de l'argent.",                 "argent": -50,  "mult": 1.0,  "cible": None,      "perte_stock": 0},
    {"msg": "👑 Commande royale ! L'or est très demandé.",             "argent": 0,    "mult": 1.6,  "cible": "or",      "perte_stock": 0},
    {"msg": "🎉 Fête du village ! Vous recevez un bonus.",             "argent": 40,   "mult": 1.0,  "cible": None,      "perte_stock": 0},
    {"msg": "🌊 Inondation ! Stock de poisson gâté.",                  "argent": 0,    "mult": 1.3,  "cible": "poisson", "perte_stock": 0},
    {"msg": "🕵️  Contrebandiers ! Les épices sont rares.",             "argent": 0,    "mult": 1.5,  "cible": "epices",  "perte_stock": 0},
    {"msg": "💎 Caravane de soie ! Prix en chute libre.",              "argent": 0,    "mult": 0.5,  "cible": "soie",    "perte_stock": 0},
    {"msg": "📈 Marché calme. Rien de particulier.",                   "argent": 0,    "mult": 1.0,  "cible": None,      "perte_stock": 0},
]


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
    """

    for cle in PRODUITS:
        variation_offre = random.randint(-10, 10)
        variation_demande = random.randint(-10, 10)

        offre_demande[cle]["offre"] = limiter(offre_demande[cle]["offre"] + variation_offre)
        offre_demande[cle]["demande"] = limiter(offre_demande[cle]["demande"] + variation_demande)

    if evenement is None:
        return

    cible = evenement["cible"]

    # Événement ciblé sur une ressource
    if cible is not None:
        if evenement["mult"] > 1:
            # Ressource rare / très demandée
            offre_demande[cible]["demande"] = limiter(offre_demande[cible]["demande"] + 25)
            offre_demande[cible]["offre"] = limiter(offre_demande[cible]["offre"] - 15)

        elif evenement["mult"] < 1:
            # Ressource abondante / moins chère
            offre_demande[cible]["offre"] = limiter(offre_demande[cible]["offre"] + 25)
            offre_demande[cible]["demande"] = limiter(offre_demande[cible]["demande"] - 15)

    # Perte générale de stock : moins d'offre globale
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
    return sum(stock[cle] * prix_actuels[cle] for cle in stock)


def patrimoine_total():
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


# ──────────────────────────────────────────────
#  ÉCRANS
# ──────────────────────────────────────────────

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
    progression_obj = min(patrimoine, OBJECTIF)

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
    val_txt = f"{C.GRIS}  💎 Valeur stock : {valeur_stock()} €{C.RESET}"

    print(f"{C.CYAN}║{C.RESET}{arg_txt:<40}{stk_txt:<30}{C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}{val_txt:<60} {C.CYAN}║{C.RESET}")

    barre = barre_progression(progression_obj, OBJECTIF, 30)
    obj_txt = f"  🎯 Objectif : {barre}  {C.JAUNE}{patrimoine}/{OBJECTIF} €{C.RESET}"
    print(f"{C.CYAN}║{C.RESET}{obj_txt}")

    print(f"{C.CYAN}╚{'═'*62}╝{C.RESET}")


def afficher_marche():
    print(f"\n  {C.BOLD}{C.BLANC}MARCHÉ DU JOUR{C.RESET}")
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
    print(f"  {couleur}{C.BLANC}{C.BOLD}  ÉVÉNEMENT DU JOUR  {C.RESET}")
    print(f"  {C.BOLD}{ev['msg']}{C.RESET}")

    if ev["argent"] != 0:
        signe = "+" if ev["argent"] > 0 else ""
        print(f"  → Effet : {C.JAUNE}{signe}{ev['argent']} €{C.RESET}")

    if ev["perte_stock"] > 0:
        print(f"  → {C.ROUGE}Perte de {int(ev['perte_stock'] * 100)}% de chaque stock{C.RESET}")

    if ev["cible"] is not None:
        nom = PRODUITS[ev["cible"]]["nom"]
        print(f"  → Marché touché : {C.CYAN}{nom}{C.RESET}")


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
    global argent

    possedes = {cle: qte for cle, qte in stock.items() if qte > 0}

    if not possedes:
        print(f"  {C.ROUGE}Tu n'as aucune marchandise à vendre !{C.RESET}")
        input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")
        return

    cle = choisir_produit("vendre")

    if cle is None:
        return

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

    print(f"\n  {C.BOLD}Patrimoine total   {C.RESET}: {C.JAUNE}{C.BOLD}{patrimoine_total()} €{C.RESET}")
    print(f"  {C.BOLD}Argent disponible  {C.RESET}: {C.VERT}{argent} €{C.RESET}")
    print(f"  {C.BOLD}Valeur du stock    {C.RESET}: {C.CYAN}{valeur_stock()} €{C.RESET}")
    print(f"  {C.BOLD}Jours écoulés      {C.RESET}: {jour}/{JOURS_MAX}")
    print(f"  {C.BOLD}Objectif           {C.RESET}: {OBJECTIF} € {barre_progression(patrimoine_total(), OBJECTIF, 30)}")

    print(f"\n  {C.BOLD}État économique des ressources :{C.RESET}")
    ligne("─", 64, C.GRIS)

    for cle, prod in PRODUITS.items():
        offre = offre_demande[cle]["offre"]
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

    print(f"\n  {C.BOLD}Dernières transactions :{C.RESET}")
    ligne("─", 64, C.GRIS)

    dernieres = historique[-10:] if len(historique) >= 10 else historique

    if not dernieres:
        print(f"  {C.GRIS}Aucune transaction.{C.RESET}")

    for j, action, montant in reversed(dernieres):
        couleur = C.VERT if montant > 0 else C.ROUGE
        signe = "+" if montant > 0 else ""
        print(f"  Jour {j:>2} │ {action:<30} │ {couleur}{signe}{montant} €{C.RESET}")

    ligne("─", 64, C.GRIS)

    input(f"\n  {C.GRIS}[ENTRÉE] pour revenir{C.RESET}")


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

    argent = ARGENT_DEPART
    stock = {}
    prix_actuels = {}
    offre_demande = {}
    jour = 1
    historique = []
    evenement_actif = None

    initialiser_prix()


def jouer():
    global jour, evenement_actif

    while True:
        evenement_actif = tirer_evenement()

        appliquer_evenement(evenement_actif)

        # Nouveau : le marché bouge avant le calcul des prix
        actualiser_offre_demande(evenement_actif)

        mettre_a_jour_prix(evenement_actif)

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

            elif choix == "j":
                jour_termine = True
                jour += 1

            elif choix == "q":
                print(f"\n  {C.GRIS}À bientôt, marchand.{C.RESET}\n")
                return False

            else:
                print(f"  {C.ROUGE}Choix invalide.{C.RESET}")
                input(f"  {C.GRIS}[ENTRÉE]{C.RESET}")

        if patrimoine_total() >= OBJECTIF:
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
