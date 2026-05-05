import pygame
import random
import math
import json
import os

# ============================================================
# MERCATOR — Neon Market Empire
# Jeu de commerce stratégique en Pygame
# Niveau : Lycée / NSI
# ============================================================


# -----------------------------
# Initialisation de Pygame
# -----------------------------
pygame.init()

LARGEUR = 1280
HAUTEUR = 720
FPS = 60

fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("MERCATOR — Neon Market Empire")

clock = pygame.time.Clock()


# -----------------------------
# Couleurs du thème néon
# -----------------------------
BLEU_NUIT = (8, 12, 28)
BLEU_FOND = (12, 18, 42)
CARTE = (18, 26, 56)
CARTE_2 = (24, 34, 72)

BLANC = (245, 248, 255)
GRIS = (150, 160, 180)
GRIS_FONCE = (70, 80, 110)

CYAN = (0, 225, 255)
VIOLET = (160, 80, 255)
BLEU = (70, 130, 255)
VERT = (70, 255, 150)
JAUNE = (255, 210, 80)
ROUGE = (255, 80, 105)
ORANGE = (255, 140, 70)

NOIR_TRANSPARENT = (0, 0, 0, 150)


# -----------------------------
# Polices
# -----------------------------
FONT_TITRE = pygame.font.SysFont("arial", 58, bold=True)
FONT_SOUS_TITRE = pygame.font.SysFont("arial", 26, bold=True)
FONT_GRAND = pygame.font.SysFont("arial", 34, bold=True)
FONT_MOYEN = pygame.font.SysFont("arial", 23, bold=True)
FONT_NORMAL = pygame.font.SysFont("arial", 20)
FONT_PETIT = pygame.font.SysFont("arial", 16)


# ============================================================
# Fonctions utiles d'affichage
# ============================================================

def dessiner_texte(surface, texte, police, couleur, x, y, centre=False):
    """Affiche un texte sur l'écran."""
    rendu = police.render(str(texte), True, couleur)
    rect = rendu.get_rect()

    if centre:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    surface.blit(rendu, rect)
    return rect


def dessiner_rect_arrondi(surface, rect, couleur, rayon=18, bordure=0, couleur_bordure=None):
    """Dessine un rectangle arrondi."""
    pygame.draw.rect(surface, couleur, rect, border_radius=rayon)

    if bordure > 0 and couleur_bordure is not None:
        pygame.draw.rect(surface, couleur_bordure, rect, bordure, border_radius=rayon)


def dessiner_barre(surface, x, y, largeur, hauteur, valeur, maximum, couleur):
    """Dessine une barre de progression."""
    pygame.draw.rect(surface, GRIS_FONCE, (x, y, largeur, hauteur), border_radius=10)

    if maximum > 0:
        ratio = valeur / maximum
    else:
        ratio = 0

    ratio = max(0, min(1, ratio))
    largeur_remplie = int(largeur * ratio)

    pygame.draw.rect(surface, couleur, (x, y, largeur_remplie, hauteur), border_radius=10)


def texte_multiligne(surface, texte, police, couleur, x, y, largeur_max, espace=8):
    """Affiche un texte sur plusieurs lignes."""
    mots = texte.split(" ")
    ligne = ""
    hauteur_ligne = police.get_height() + espace

    for mot in mots:
        test = ligne + mot + " "
        if police.size(test)[0] <= largeur_max:
            ligne = test
        else:
            dessiner_texte(surface, ligne, police, couleur, x, y)
            y += hauteur_ligne
            ligne = mot + " "

    if ligne:
        dessiner_texte(surface, ligne, police, couleur, x, y)


# ============================================================
# Classe Button
# ============================================================

class Button:
    """Bouton avec animation au survol."""

    def __init__(self, x, y, largeur, hauteur, texte, couleur, couleur_hover):
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.texte = texte
        self.couleur = couleur
        self.couleur_hover = couleur_hover
        self.scale = 1.0
        self.hover = False

    def update(self, souris_pos):
        """Met à jour l'animation du bouton."""
        self.hover = self.rect.collidepoint(souris_pos)

        if self.hover:
            self.scale += (1.06 - self.scale) * 0.18
        else:
            self.scale += (1.0 - self.scale) * 0.18

    def draw(self, surface):
        """Dessine le bouton."""
        w = int(self.rect.width * self.scale)
        h = int(self.rect.height * self.scale)

        rect_anim = pygame.Rect(0, 0, w, h)
        rect_anim.center = self.rect.center

        couleur = self.couleur_hover if self.hover else self.couleur

        # Ombre légère
        ombre = rect_anim.copy()
        ombre.y += 6
        dessiner_rect_arrondi(surface, ombre, (4, 6, 18), 20)

        # Bouton
        dessiner_rect_arrondi(surface, rect_anim, couleur, 20, 2, CYAN if self.hover else GRIS_FONCE)

        # Texte
        dessiner_texte(surface, self.texte, FONT_MOYEN, BLANC, rect_anim.centerx, rect_anim.centery, centre=True)

    def clicked(self, event):
        """Renvoie True si le bouton est cliqué."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False


# ============================================================
# Classe Particle
# ============================================================

class Particle:
    """Particule du fond animé."""

    def __init__(self):
        self.x = random.randint(0, LARGEUR)
        self.y = random.randint(0, HAUTEUR)
        self.rayon = random.randint(1, 3)
        self.vitesse_x = random.uniform(-0.3, 0.3)
        self.vitesse_y = random.uniform(0.2, 0.9)
        self.alpha = random.randint(60, 170)
        self.couleur = random.choice([CYAN, VIOLET, BLEU])

    def update(self):
        self.x += self.vitesse_x
        self.y += self.vitesse_y

        if self.y > HAUTEUR:
            self.y = -10
            self.x = random.randint(0, LARGEUR)

        if self.x < -10:
            self.x = LARGEUR + 10

        if self.x > LARGEUR + 10:
            self.x = -10

    def draw(self, surface):
        particule_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
        couleur = (*self.couleur, self.alpha)
        pygame.draw.circle(particule_surface, couleur, (5, 5), self.rayon)
        surface.blit(particule_surface, (self.x, self.y))


# ============================================================
# Classe FloatingText
# ============================================================

class FloatingText:
    """Texte flottant pour afficher +€ ou -€."""

    def __init__(self, texte, x, y, couleur):
        self.texte = texte
        self.x = x
        self.y = y
        self.couleur = couleur
        self.alpha = 255
        self.vie = 1.3

    def update(self, dt):
        self.y -= 45 * dt
        self.vie -= dt
        self.alpha = max(0, int(255 * self.vie / 1.3))

    def draw(self, surface):
        rendu = FONT_MOYEN.render(self.texte, True, self.couleur)
        rendu.set_alpha(self.alpha)
        surface.blit(rendu, (self.x, self.y))

    def est_mort(self):
        return self.vie <= 0


# ============================================================
# Classe Toast / Notification
# ============================================================

class Toast:
    """Notification animée pour les événements du marché."""

    def __init__(self, texte, couleur=CYAN):
        self.texte = texte
        self.couleur = couleur
        self.y = -80
        self.alpha = 255
        self.temps = 4.0

    def update(self, dt):
        # Descente douce vers le haut de l'écran
        self.y += (28 - self.y) * 0.12

        self.temps -= dt
        if self.temps < 1:
            self.alpha = max(0, int(255 * self.temps))

    def draw(self, surface):
        largeur = 760
        hauteur = 64
        x = LARGEUR // 2 - largeur // 2

        notif = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
        fond = (15, 22, 50, self.alpha)
        bord = (*self.couleur, self.alpha)

        pygame.draw.rect(notif, fond, (0, 0, largeur, hauteur), border_radius=22)
        pygame.draw.rect(notif, bord, (0, 0, largeur, hauteur), 2, border_radius=22)

        texte_rendu = FONT_NORMAL.render(self.texte, True, BLANC)
        texte_rendu.set_alpha(self.alpha)
        notif.blit(texte_rendu, (28, 21))

        surface.blit(notif, (x, self.y))

    def est_mort(self):
        return self.alpha <= 0


# ============================================================
# Classe Game
# ============================================================

class Game:
    """Gère toute la logique du jeu."""

    def __init__(self):
        self.argent_depart = 200
        self.argent = self.argent_depart

        self.jour = 1
        self.jours_max = 30
        self.objectif = 1500

        self.limite_stock = 20

        # Dictionnaire des ressources
        self.produits = {
            "ble": {
                "nom": "Ble",
                "prix_base": 8,
                "volatilite": 0.25,
                "couleur": JAUNE,
            },
            "soie": {
                "nom": "Soie",
                "prix_base": 25,
                "volatilite": 0.45,
                "couleur": VIOLET,
            },
            "epices": {
                "nom": "Epices",
                "prix_base": 40,
                "volatilite": 0.55,
                "couleur": ORANGE,
            },
            "or": {
                "nom": "Or",
                "prix_base": 80,
                "volatilite": 0.65,
                "couleur": JAUNE,
            },
            "poisson": {
                "nom": "Poisson",
                "prix_base": 12,
                "volatilite": 0.35,
                "couleur": CYAN,
            },
        }

        self.prix = {}
        self.stock = {}
        self.historique_prix = {}
        self.offre_demande = {}

        self.produit_selectionne = "ble"

        self.dernier_evenement = "Bienvenue sur le marche de MERCATOR."
        self.floating_texts = []
        self.toasts = []

        self.partie_terminee = False
        self.victoire = False

        self.reinitialiser()

    def reinitialiser(self):
        """Réinitialise la partie."""
        self.argent = self.argent_depart
        self.jour = 1
        self.partie_terminee = False
        self.victoire = False
        self.produit_selectionne = "ble"
        self.dernier_evenement = "Bienvenue sur le marche de MERCATOR."

        self.prix = {}
        self.stock = {}
        self.historique_prix = {}
        self.offre_demande = {}
        self.floating_texts = []
        self.toasts = []

        for cle, produit in self.produits.items():
            self.prix[cle] = produit["prix_base"]
            self.stock[cle] = 0
            self.historique_prix[cle] = [produit["prix_base"]]

            # 100 = marché équilibré
            self.offre_demande[cle] = {
                "offre": 100,
                "demande": 100
            }

    def stock_total(self):
        """Retourne le stock total."""
        return sum(self.stock.values())

    def valeur_stock(self):
        """Retourne la valeur du stock."""
        total = 0
        for cle in self.produits:
            total += self.stock[cle] * self.prix[cle]
        return total

    def patrimoine_total(self):
        """Argent + valeur du stock."""
        return self.argent + self.valeur_stock()

    def facteur_offre_demande(self, cle):
        """Calcule un facteur de prix selon l'offre et la demande."""
        offre = self.offre_demande[cle]["offre"]
        demande = self.offre_demande[cle]["demande"]

        ratio = demande / offre

        facteur = 1 + (ratio - 1) * 0.45

        return max(0.65, min(1.75, facteur))

    def limiter_marche(self, valeur):
        """Limite l'offre et la demande entre 20 et 180."""
        return max(20, min(180, valeur))

    def tendance(self, cle):
        """Renvoie une phrase selon l'état économique."""
        offre = self.offre_demande[cle]["offre"]
        demande = self.offre_demande[cle]["demande"]

        if demande > offre + 30:
            return "Demande forte"
        elif offre > demande + 30:
            return "Offre forte"
        else:
            return "Equilibre"

    def conseil(self):
        """Donne un conseil simple au joueur."""
        cle = self.produit_selectionne
        prix = self.prix[cle]
        base = self.produits[cle]["prix_base"]
        tendance = self.tendance(cle)

        if prix <= base * 0.8:
            return "Conseil : prix bas, acheter peut etre interessant."
        elif prix >= base * 1.4:
            return "Conseil : prix haut, vendre peut etre malin."
        elif tendance == "Demande forte":
            return "Conseil : la demande est forte, le prix peut encore monter."
        elif tendance == "Offre forte":
            return "Conseil : beaucoup d'offre, attention a la baisse."
        else:
            return "Conseil : marche stable, observe avant d'agir."

    def choisir_evenement(self):
        """Choisit un événement aléatoire."""
        evenements = [
            {
                "nom": "Forte demande",
                "texte": "Forte demande : les acheteurs se ruent sur le marche.",
                "type": "hausse",
                "mult": 1.25,
                "couleur": VERT,
            },
            {
                "nom": "Surproduction",
                "texte": "Surproduction : il y a trop de marchandises disponibles.",
                "type": "baisse",
                "mult": 0.75,
                "couleur": ROUGE,
            },
            {
                "nom": "Crise economique",
                "texte": "Crise economique : le marche devient tres instable.",
                "type": "instable",
                "mult": 1.00,
                "couleur": ORANGE,
            },
            {
                "nom": "Produit tendance",
                "texte": "Produit tendance : une ressource devient tres populaire.",
                "type": "forte_hausse",
                "mult": 1.50,
                "couleur": VIOLET,
            },
            {
                "nom": "Transport bloque",
                "texte": "Transport bloque : les marchandises arrivent difficilement.",
                "type": "hausse",
                "mult": 1.35,
                "couleur": JAUNE,
            },
            {
                "nom": "Marche stable",
                "texte": "Marche stable : petites variations seulement.",
                "type": "stable",
                "mult": 1.00,
                "couleur": CYAN,
            },
        ]

        return random.choice(evenements)

    def modifier_offre_demande_evenement(self, cle, event):
        """Modifie l'offre/demande selon l'événement."""
        if event["type"] == "hausse":
            self.offre_demande[cle]["demande"] += 25
            self.offre_demande[cle]["offre"] -= 12

        elif event["type"] == "forte_hausse":
            self.offre_demande[cle]["demande"] += 40
            self.offre_demande[cle]["offre"] -= 20

        elif event["type"] == "baisse":
            self.offre_demande[cle]["offre"] += 30
            self.offre_demande[cle]["demande"] -= 15

        elif event["type"] == "instable":
            self.offre_demande[cle]["offre"] += random.randint(-35, 35)
            self.offre_demande[cle]["demande"] += random.randint(-35, 35)

        elif event["type"] == "stable":
            self.offre_demande[cle]["offre"] += random.randint(-8, 8)
            self.offre_demande[cle]["demande"] += random.randint(-8, 8)

        self.offre_demande[cle]["offre"] = self.limiter_marche(self.offre_demande[cle]["offre"])
        self.offre_demande[cle]["demande"] = self.limiter_marche(self.offre_demande[cle]["demande"])

    def passer_jour(self):
        """Passe au jour suivant et change les prix."""
        if self.partie_terminee:
            return

        if self.jour >= self.jours_max:
            self.finir_partie()
            return

        self.jour += 1

        event = self.choisir_evenement()
        cible = random.choice(list(self.produits.keys()))

        self.dernier_evenement = event["texte"] + " Ressource touchee : " + self.produits[cible]["nom"] + "."
        self.toasts.append(Toast(self.dernier_evenement, event["couleur"]))

        for cle, produit in self.produits.items():
            # Evolution naturelle de l'offre/demande
            self.offre_demande[cle]["offre"] += random.randint(-10, 10)
            self.offre_demande[cle]["demande"] += random.randint(-10, 10)

            self.offre_demande[cle]["offre"] = self.limiter_marche(self.offre_demande[cle]["offre"])
            self.offre_demande[cle]["demande"] = self.limiter_marche(self.offre_demande[cle]["demande"])

            # L'événement a un effet plus fort sur une ressource cible
            mult_event = 1.0
            if cle == cible:
                mult_event = event["mult"]
                self.modifier_offre_demande_evenement(cle, event)

            base = produit["prix_base"]
            volatilite = produit["volatilite"]

            facteur_marche = self.facteur_offre_demande(cle)
            variation = random.uniform(-volatilite, volatilite)

            # Si crise économique, tous les prix bougent plus violemment
            if event["type"] == "instable":
                variation *= 1.8

            nouveau_prix = base * (1 + variation) * facteur_marche * mult_event
            nouveau_prix = max(1, round(nouveau_prix))

            self.prix[cle] = nouveau_prix
            self.historique_prix[cle].append(nouveau_prix)

            if len(self.historique_prix[cle]) > 30:
                self.historique_prix[cle].pop(0)

        if self.jour >= self.jours_max:
            self.finir_partie()

    def acheter(self, quantite):
        """Acheter une quantité du produit sélectionné."""
        cle = self.produit_selectionne
        prix = self.prix[cle]
        cout = prix * quantite

        if self.stock_total() + quantite > self.limite_stock:
            self.toasts.append(Toast("Stock maximum atteint.", ROUGE))
            return

        if self.argent < cout:
            self.toasts.append(Toast("Argent insuffisant pour cet achat.", ROUGE))
            return

        self.argent -= cout
        self.stock[cle] += quantite

        # Le joueur influence le marché
        self.offre_demande[cle]["demande"] = self.limiter_marche(self.offre_demande[cle]["demande"] + quantite * 2)
        self.offre_demande[cle]["offre"] = self.limiter_marche(self.offre_demande[cle]["offre"] - quantite)

        self.floating_texts.append(FloatingText("-" + str(cout) + " EUR", 1000, 145, ROUGE))

    def vendre(self, quantite):
        """Vendre une quantité du produit sélectionné."""
        cle = self.produit_selectionne

        if self.stock[cle] <= 0:
            self.toasts.append(Toast("Tu n'as pas cette marchandise en stock.", ROUGE))
            return

        if quantite == "tout":
            quantite = self.stock[cle]

        if quantite > self.stock[cle]:
            self.toasts.append(Toast("Stock insuffisant pour cette vente.", ROUGE))
            return

        gain = self.prix[cle] * quantite

        self.stock[cle] -= quantite
        self.argent += gain

        # Le joueur influence le marché
        self.offre_demande[cle]["offre"] = self.limiter_marche(self.offre_demande[cle]["offre"] + quantite * 2)
        self.offre_demande[cle]["demande"] = self.limiter_marche(self.offre_demande[cle]["demande"] - quantite)

        self.floating_texts.append(FloatingText("+" + str(gain) + " EUR", 1000, 145, VERT))

    def finir_partie(self):
        """Détermine la victoire ou la défaite."""
        self.partie_terminee = True
        self.victoire = self.patrimoine_total() >= self.objectif
        self.sauvegarder_score()

    def sauvegarder_score(self):
        """Sauvegarde le dernier score dans un fichier JSON."""
        donnees = {
            "argent": self.argent,
            "valeur_stock": self.valeur_stock(),
            "patrimoine_total": self.patrimoine_total(),
            "jour": self.jour,
            "victoire": self.victoire
        }

        try:
            with open("score_mercator.json", "w", encoding="utf-8") as fichier:
                json.dump(donnees, fichier, indent=4)
        except:
            pass


# ============================================================
# Interface principale
# ============================================================

class Interface:
    """Gère les écrans et l'affichage."""

    def __init__(self):
        self.game = Game()

        self.ecran = "menu"

        self.particles = [Particle() for _ in range(95)]

        self.temps = 0

        # Boutons menu
        self.btn_jouer = Button(520, 325, 240, 62, "JOUER", (20, 110, 160), (0, 180, 230))
        self.btn_regles = Button(520, 405, 240, 62, "REGLES", (70, 50, 140), (120, 80, 230))
        self.btn_quitter = Button(520, 485, 240, 62, "QUITTER", (120, 40, 70), (210, 60, 100))

        # Boutons jeu
        self.btn_acheter_1 = Button(885, 420, 155, 50, "Acheter x1", (25, 105, 90), (50, 190, 140))
        self.btn_acheter_5 = Button(1060, 420, 155, 50, "Acheter x5", (25, 105, 90), (50, 190, 140))
        self.btn_vendre_1 = Button(885, 490, 155, 50, "Vendre x1", (120, 70, 30), (220, 130, 50))
        self.btn_vendre_tout = Button(1060, 490, 155, 50, "Vendre tout", (120, 45, 60), (220, 70, 100))
        self.btn_jour = Button(885, 580, 330, 56, "Jour suivant", (30, 90, 150), (0, 180, 255))

        self.btn_pause = Button(1110, 25, 120, 42, "Pause", (60, 60, 100), (100, 100, 180))
        self.btn_retour_menu = Button(520, 585, 240, 56, "Menu", (40, 80, 130), (0, 160, 220))
        self.btn_rejouer = Button(510, 500, 260, 58, "Rejouer", (20, 120, 90), (50, 220, 150))

        # Boutons ressources
        self.boutons_produits = []
        x = 55
        y = 235

        for cle in self.game.produits:
            bouton = Button(x, y, 145, 48, self.game.produits[cle]["nom"], (35, 45, 85), (55, 90, 150))
            self.boutons_produits.append((cle, bouton))
            y += 62

    def update(self, dt):
        """Met à jour animations et logique visuelle."""
        self.temps += dt
        souris = pygame.mouse.get_pos()

        for p in self.particles:
            p.update()

        tous_boutons = [
            self.btn_jouer,
            self.btn_regles,
            self.btn_quitter,
            self.btn_acheter_1,
            self.btn_acheter_5,
            self.btn_vendre_1,
            self.btn_vendre_tout,
            self.btn_jour,
            self.btn_pause,
            self.btn_retour_menu,
            self.btn_rejouer,
        ]

        for cle, bouton in self.boutons_produits:
            tous_boutons.append(bouton)

        for bouton in tous_boutons:
            bouton.update(souris)

        for texte in self.game.floating_texts:
            texte.update(dt)

        self.game.floating_texts = [t for t in self.game.floating_texts if not t.est_mort()]

        for toast in self.game.toasts:
            toast.update(dt)

        self.game.toasts = [t for t in self.game.toasts if not t.est_mort()]

    def draw_background(self):
        """Dessine le fond animé."""
        fenetre.fill(BLEU_NUIT)

        # Cercles néon de fond
        t = self.temps
        x1 = 180 + math.sin(t * 0.5) * 30
        y1 = 140 + math.cos(t * 0.4) * 25
        x2 = 1030 + math.cos(t * 0.35) * 35
        y2 = 540 + math.sin(t * 0.45) * 25

        pygame.draw.circle(fenetre, (14, 34, 75), (int(x1), int(y1)), 210)
        pygame.draw.circle(fenetre, (45, 18, 80), (int(x2), int(y2)), 240)

        for p in self.particles:
            p.draw(fenetre)

    def handle_events(self):
        """Gère les événements clavier/souris."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.ecran == "menu":
                if self.btn_jouer.clicked(event):
                    self.game.reinitialiser()
                    self.ecran = "jeu"

                elif self.btn_regles.clicked(event):
                    self.ecran = "regles"

                elif self.btn_quitter.clicked(event):
                    return False

            elif self.ecran == "regles":
                if self.btn_retour_menu.clicked(event):
                    self.ecran = "menu"

            elif self.ecran == "jeu":
                if self.btn_pause.clicked(event):
                    self.ecran = "pause"

                for cle, bouton in self.boutons_produits:
                    if bouton.clicked(event):
                        self.game.produit_selectionne = cle

                if self.btn_acheter_1.clicked(event):
                    self.game.acheter(1)

                elif self.btn_acheter_5.clicked(event):
                    self.game.acheter(5)

                elif self.btn_vendre_1.clicked(event):
                    self.game.vendre(1)

                elif self.btn_vendre_tout.clicked(event):
                    self.game.vendre("tout")

                elif self.btn_jour.clicked(event):
                    self.game.passer_jour()
                    if self.game.partie_terminee:
                        self.ecran = "fin"

            elif self.ecran == "pause":
                if self.btn_jouer.clicked(event):
                    self.ecran = "jeu"

                elif self.btn_retour_menu.clicked(event):
                    self.ecran = "menu"

            elif self.ecran == "fin":
                if self.btn_rejouer.clicked(event):
                    self.game.reinitialiser()
                    self.ecran = "jeu"

                elif self.btn_retour_menu.clicked(event):
                    self.ecran = "menu"

        return True

    def draw_menu(self):
        """Écran d'accueil."""
        self.draw_background()

        # Titre animé
        offset = math.sin(self.temps * 2) * 6

        dessiner_texte(fenetre, "MERCATOR", FONT_TITRE, CYAN, LARGEUR // 2, 170 + offset, centre=True)
        dessiner_texte(fenetre, "Neon Market Empire", FONT_SOUS_TITRE, VIOLET, LARGEUR // 2, 230, centre=True)
        dessiner_texte(
            fenetre,
            "Achete bas, vends haut, domine le marche.",
            FONT_NORMAL,
            GRIS,
            LARGEUR // 2,
            270,
            centre=True
        )

        self.btn_jouer.draw(fenetre)
        self.btn_regles.draw(fenetre)
        self.btn_quitter.draw(fenetre)

    def draw_regles(self):
        """Écran des règles."""
        self.draw_background()

        dessiner_texte(fenetre, "REGLES DU JEU", FONT_GRAND, CYAN, LARGEUR // 2, 90, centre=True)

        rect = pygame.Rect(230, 150, 820, 360)
        dessiner_rect_arrondi(fenetre, rect, CARTE, 24, 2, CYAN)

        texte = (
            "Tu es un marchand dans un marche futuriste. Ton objectif est de faire grandir ton patrimoine "
            "en achetant et en vendant des ressources. Chaque jour, les prix changent selon des evenements "
            "aleatoires, mais aussi selon l'offre et la demande. Quand la demande est forte, les prix montent. "
            "Quand l'offre est forte, les prix baissent. La partie dure 30 jours. A la fin, ton score correspond "
            "a ton argent + la valeur de ton stock."
        )

        texte_multiligne(fenetre, texte, FONT_NORMAL, BLANC, 270, 190, 740, 10)

        dessiner_texte(fenetre, "Commandes :", FONT_MOYEN, JAUNE, 270, 365)
        dessiner_texte(fenetre, "- Clique sur une ressource pour la selectionner.", FONT_NORMAL, BLANC, 270, 405)
        dessiner_texte(fenetre, "- Achete x1 ou x5 si tu as assez d'argent et de place.", FONT_NORMAL, BLANC, 270, 435)
        dessiner_texte(fenetre, "- Vends x1 ou tout ton stock quand le prix est haut.", FONT_NORMAL, BLANC, 270, 465)

        self.btn_retour_menu.draw(fenetre)

    def draw_hud(self):
        """Affiche les informations principales du joueur."""
        rect = pygame.Rect(35, 25, 810, 155)
        dessiner_rect_arrondi(fenetre, rect, CARTE, 22, 2, CYAN)

        dessiner_texte(fenetre, "MERCATOR", FONT_GRAND, CYAN, 60, 45)
        dessiner_texte(fenetre, "Jour " + str(self.game.jour) + " / " + str(self.game.jours_max), FONT_MOYEN, JAUNE, 60, 95)

        dessiner_texte(fenetre, "Argent", FONT_PETIT, GRIS, 310, 48)
        dessiner_texte(fenetre, str(self.game.argent) + " EUR", FONT_GRAND, VERT, 310, 75)

        dessiner_texte(fenetre, "Stock", FONT_PETIT, GRIS, 520, 48)
        dessiner_texte(
            fenetre,
            str(self.game.stock_total()) + " / " + str(self.game.limite_stock),
            FONT_GRAND,
            CYAN,
            520,
            75
        )

        dessiner_texte(fenetre, "Patrimoine", FONT_PETIT, GRIS, 680, 48)
        dessiner_texte(fenetre, str(self.game.patrimoine_total()) + " EUR", FONT_GRAND, JAUNE, 680, 75)

        # Barre objectif
        dessiner_texte(fenetre, "Objectif : " + str(self.game.objectif) + " EUR", FONT_PETIT, GRIS, 60, 135)
        dessiner_barre(fenetre, 220, 138, 560, 14, self.game.patrimoine_total(), self.game.objectif, VERT)

        self.btn_pause.draw(fenetre)

    def draw_liste_produits(self):
        """Affiche la liste des ressources."""
        rect = pygame.Rect(35, 205, 210, 400)
        dessiner_rect_arrondi(fenetre, rect, CARTE, 22, 2, VIOLET)

        dessiner_texte(fenetre, "RESSOURCES", FONT_MOYEN, BLANC, 70, 215)

        for cle, bouton in self.boutons_produits:
            if cle == self.game.produit_selectionne:
                bouton.couleur = (35, 90, 145)
            else:
                bouton.couleur = (35, 45, 85)

            bouton.draw(fenetre)

    def draw_carte_produit(self):
        """Affiche les infos du produit sélectionné."""
        cle = self.game.produit_selectionne
        produit = self.game.produits[cle]

        rect = pygame.Rect(270, 205, 570, 400)
        dessiner_rect_arrondi(fenetre, rect, CARTE, 22, 2, produit["couleur"])

        dessiner_texte(fenetre, produit["nom"], FONT_GRAND, produit["couleur"], 300, 230)

        prix = self.game.prix[cle]
        base = produit["prix_base"]
        stock = self.game.stock[cle]

        dessiner_texte(fenetre, "Prix actuel", FONT_PETIT, GRIS, 310, 295)
        dessiner_texte(fenetre, str(prix) + " EUR", FONT_GRAND, BLANC, 310, 318)

        dessiner_texte(fenetre, "Prix de base", FONT_PETIT, GRIS, 510, 295)
        dessiner_texte(fenetre, str(base) + " EUR", FONT_GRAND, CYAN, 510, 318)

        dessiner_texte(fenetre, "Ton stock", FONT_PETIT, GRIS, 690, 295)
        dessiner_texte(fenetre, str(stock), FONT_GRAND, JAUNE, 690, 318)

        offre = self.game.offre_demande[cle]["offre"]
        demande = self.game.offre_demande[cle]["demande"]

        dessiner_texte(fenetre, "Offre", FONT_PETIT, GRIS, 310, 385)
        dessiner_barre(fenetre, 310, 415, 210, 16, offre, 180, CYAN)
        dessiner_texte(fenetre, str(offre), FONT_NORMAL, BLANC, 530, 406)

        dessiner_texte(fenetre, "Demande", FONT_PETIT, GRIS, 310, 455)
        dessiner_barre(fenetre, 310, 485, 210, 16, demande, 180, VIOLET)
        dessiner_texte(fenetre, str(demande), FONT_NORMAL, BLANC, 530, 476)

        tendance = self.game.tendance(cle)
        dessiner_texte(fenetre, "Tendance : " + tendance, FONT_MOYEN, JAUNE, 600, 420)

        conseil = self.game.conseil()
        texte_multiligne(fenetre, conseil, FONT_NORMAL, BLANC, 600, 465, 210)

    def draw_actions(self):
        """Dessine les boutons d'action."""
        rect = pygame.Rect(865, 205, 375, 455)
        dessiner_rect_arrondi(fenetre, rect, CARTE, 22, 2, CYAN)

        dessiner_texte(fenetre, "ACTIONS", FONT_MOYEN, BLANC, 895, 225)

        cle = self.game.produit_selectionne
        produit = self.game.produits[cle]

        dessiner_texte(fenetre, "Selection : " + produit["nom"], FONT_NORMAL, produit["couleur"], 895, 270)
        dessiner_texte(fenetre, "Prix : " + str(self.game.prix[cle]) + " EUR", FONT_NORMAL, BLANC, 895, 300)
        dessiner_texte(fenetre, "Stock : " + str(self.game.stock[cle]), FONT_NORMAL, BLANC, 895, 330)

        self.btn_acheter_1.draw(fenetre)
        self.btn_acheter_5.draw(fenetre)
        self.btn_vendre_1.draw(fenetre)
        self.btn_vendre_tout.draw(fenetre)
        self.btn_jour.draw(fenetre)

    def draw_graphique(self):
        """Dessine le graphique d'évolution du prix."""
        cle = self.game.produit_selectionne
        historique = self.game.historique_prix[cle]
        produit = self.game.produits[cle]

        rect = pygame.Rect(270, 620, 570, 70)
        dessiner_rect_arrondi(fenetre, rect, (12, 18, 42), 18, 2, GRIS_FONCE)

        dessiner_texte(fenetre, "Evolution du prix", FONT_PETIT, GRIS, 290, 628)

        if len(historique) < 2:
            return

        valeurs = historique[-20:]
        mini = min(valeurs)
        maxi = max(valeurs)

        if maxi == mini:
            maxi += 1

        points = []
        marge_x = 25
        marge_y = 20

        for i, valeur in enumerate(valeurs):
            x = rect.x + marge_x + i * ((rect.width - 2 * marge_x) / max(1, len(valeurs) - 1))
            ratio = (valeur - mini) / (maxi - mini)
            y = rect.bottom - marge_y - ratio * (rect.height - 2 * marge_y)
            points.append((x, y))

        if len(points) >= 2:
            pygame.draw.lines(fenetre, produit["couleur"], False, points, 3)

        for point in points:
            pygame.draw.circle(fenetre, produit["couleur"], (int(point[0]), int(point[1])), 4)

    def draw_evenement(self):
        """Affiche le dernier événement."""
        rect = pygame.Rect(35, 620, 210, 70)
        dessiner_rect_arrondi(fenetre, rect, CARTE, 18, 2, JAUNE)

        dessiner_texte(fenetre, "Evenement", FONT_PETIT, JAUNE, 55, 628)
        texte_multiligne(fenetre, self.game.dernier_evenement, FONT_PETIT, BLANC, 55, 652, 170, 2)

    def draw_jeu(self):
        """Écran principal du jeu."""
        self.draw_background()
        self.draw_hud()
        self.draw_liste_produits()
        self.draw_carte_produit()
        self.draw_actions()
        self.draw_graphique()
        self.draw_evenement()

        for texte in self.game.floating_texts:
            texte.draw(fenetre)

        for toast in self.game.toasts:
            toast.draw(fenetre)

    def draw_pause(self):
        """Écran de pause."""
        self.draw_jeu()

        overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        overlay.fill(NOIR_TRANSPARENT)
        fenetre.blit(overlay, (0, 0))

        rect = pygame.Rect(430, 220, 420, 300)
        dessiner_rect_arrondi(fenetre, rect, CARTE, 28, 2, CYAN)

        dessiner_texte(fenetre, "PAUSE", FONT_GRAND, CYAN, LARGEUR // 2, 285, centre=True)

        self.btn_jouer.texte = "REPRENDRE"
        self.btn_jouer.rect = pygame.Rect(520, 345, 240, 62)
        self.btn_jouer.draw(fenetre)

        self.btn_retour_menu.rect = pygame.Rect(520, 425, 240, 56)
        self.btn_retour_menu.draw(fenetre)

    def draw_fin(self):
        """Écran de fin de partie."""
        self.draw_background()

        victoire = self.game.victoire

        if victoire:
            titre = "VICTOIRE"
            couleur = VERT
            phrase = "Tu as domine le marche."
        else:
            titre = "FIN DE PARTIE"
            couleur = ROUGE
            phrase = "Le commerce ne pardonne pas."

        dessiner_texte(fenetre, titre, FONT_TITRE, couleur, LARGEUR // 2, 140, centre=True)
        dessiner_texte(fenetre, phrase, FONT_SOUS_TITRE, BLANC, LARGEUR // 2, 205, centre=True)

        rect = pygame.Rect(390, 260, 500, 190)
        dessiner_rect_arrondi(fenetre, rect, CARTE, 26, 2, couleur)

        dessiner_texte(fenetre, "Score final", FONT_MOYEN, GRIS, LARGEUR // 2, 290, centre=True)
        dessiner_texte(
            fenetre,
            str(self.game.patrimoine_total()) + " EUR",
            FONT_TITRE,
            JAUNE,
            LARGEUR // 2,
            350,
            centre=True
        )

        details = "Argent : " + str(self.game.argent) + " EUR   |   Valeur stock : " + str(self.game.valeur_stock()) + " EUR"
        dessiner_texte(fenetre, details, FONT_NORMAL, BLANC, LARGEUR // 2, 420, centre=True)

        self.btn_rejouer.draw(fenetre)

        self.btn_retour_menu.rect = pygame.Rect(510, 575, 260, 56)
        self.btn_retour_menu.draw(fenetre)

    def draw(self):
        """Dessine l'écran actuel."""
        if self.ecran == "menu":
            # On remet le texte original au cas où il a été changé dans pause
            self.btn_jouer.texte = "JOUER"
            self.btn_jouer.rect = pygame.Rect(520, 325, 240, 62)
            self.draw_menu()

        elif self.ecran == "regles":
            self.draw_regles()

        elif self.ecran == "jeu":
            self.draw_jeu()

        elif self.ecran == "pause":
            self.draw_pause()

        elif self.ecran == "fin":
            self.draw_fin()


# ============================================================
# Boucle principale
# ============================================================

def main():
    interface = Interface()
    running = True

    while running:
        dt = clock.tick(FPS) / 1000

        running = interface.handle_events()
        interface.update(dt)
        interface.draw()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
