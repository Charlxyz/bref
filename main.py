import random

# ----------------------------
# PARAMÈTRES DU JEU
# ----------------------------

argent = 100
jour = 1
objectif_argent = 500

# Stock total maximum
limite_stock = 20

# Chaque produit a son prix de départ et son stock
produits = {
    "nourriture": {"prix": 10, "stock": 0},
    "outils": {"prix": 25, "stock": 0},
    "jouets": {"prix": 15, "stock": 0}
}

# Niveau de difficulté : augmente avec les jours
difficulte = 1


# ----------------------------
# FONCTIONS D'AFFICHAGE
# ----------------------------

def afficher_statut():
    print("\n" + "-" * 30)
    print("JOUR", jour)
    print("Argent :", argent, "€")
    print("Objectif :", objectif_argent, "€")
    print("Stock utilisé :", stock_total(), "/", limite_stock)
    print("Difficulté :", difficulte)
    print("-" * 30)

    print("Produits disponibles :")
    for nom, infos in produits.items():
        print("-", nom, "| prix :", infos["prix"], "€ | stock :", infos["stock"])


def menu():
    print("\n1 - Acheter un produit")
    print("2 - Vendre un produit")
    print("3 - Passer au jour suivant")
    print("4 - Quitter")


def stock_total():
    total = 0
    for infos in produits.values():
        total += infos["stock"]
    return total


# ----------------------------
# FONCTIONS DE JEU
# ----------------------------

def choisir_produit():
    print("\nProduits disponibles :")
    noms = list(produits.keys())
    for i in range(len(noms)):
        nom = noms[i]
        print(i + 1, "-", nom, "(prix :", produits[nom]["prix"], "€)")

    try:
        choix = int(input("Choisis un produit : "))
    except ValueError:
        print("Valeur invalide.")
        return None

    if choix < 1 or choix > len(noms):
        print("Choix invalide.")
        return None

    return noms[choix - 1]


def acheter():
    global argent

    produit = choisir_produit()
    if produit is None:
        return

    try:
        quantite = int(input("Combien veux-tu acheter ? "))
    except ValueError:
        print("Valeur invalide. Entre un nombre entier.")
        return

    if quantite <= 0:
        print("La quantité doit être positive.")
        return

    prix = produits[produit]["prix"]
    cout = quantite * prix

    if cout > argent:
        print("Pas assez d'argent !")
        return

    if stock_total() + quantite > limite_stock:
        print("Pas assez de place dans le stock !")
        return

    argent -= cout
    produits[produit]["stock"] += quantite
    print("Achat réussi de", quantite, produit + ".")


def vendre():
    global argent

    produit = choisir_produit()
    if produit is None:
        return

    try:
        quantite = int(input("Combien veux-tu vendre ? "))
    except ValueError:
        print("Valeur invalide. Entre un nombre entier.")
        return

    if quantite <= 0:
        print("La quantité doit être positive.")
        return

    if quantite > produits[produit]["stock"]:
        print("Pas assez de stock pour ce produit !")
        return

    prix = produits[produit]["prix"]
    argent += quantite * prix
    produits[produit]["stock"] -= quantite
    print("Vente réussie de", quantite, produit + ".")


def evenement_aleatoire():
    global argent, limite_stock

    chance = random.randint(1, 100)

    # Événements positifs
    if chance <= 25:
        gain = random.randint(10, 40)
        argent += gain
        print("\nÉVÉNEMENT : un client exceptionnel te donne", gain, "€ !")

    elif chance <= 40:
        bonus = random.choice(list(produits.keys()))
        produits[bonus]["stock"] += 1
        print("\nÉVÉNEMENT : tu reçois 1", bonus, "gratuitement !")

    elif chance <= 50:
        limite_stock += 2
        print("\nÉVÉNEMENT : tu agrandis ton entrepôt ! Limite de stock +2.")

    # Événements négatifs
    elif chance <= 65:
        perte = random.randint(5, 25)
        argent = max(0, argent - perte)
        print("\nÉVÉNEMENT : une taxe surprise te fait perdre", perte, "€.")

    elif chance <= 80:
        mauvais = random.choice(list(produits.keys()))
        perte_stock = random.randint(1, 2)
        if produits[mauvais]["stock"] >= perte_stock:
            produits[mauvais]["stock"] -= perte_stock
            print("\nÉVÉNEMENT : un incident détruit", perte_stock, mauvais + ".")
        else:
            print("\nÉVÉNEMENT : incident sans stock perdu sur", mauvais + ".")

    # Rien ne se passe
    else:
        print("\nAucun événement spécial aujourd'hui.")


def faire_evoluer_prix():
    # Plus les jours avancent, plus les prix peuvent varier
    amplitude = 2 + difficulte
    for nom in produits:
        variation = random.randint(-amplitude, amplitude)
        nouveaux_prix = produits[nom]["prix"] + variation
        if nouveaux_prix < 1:
            nouveaux_prix = 1
        produits[nom]["prix"] = nouveaux_prix


def augmenter_difficulte():
    global difficulte, limite_stock

    # Tous les 3 jours, le jeu devient un peu plus dur
    if jour % 3 == 0:
        difficulte += 1
        limite_stock = max(10, limite_stock - 1)
        print("\nLa difficulté augmente ! Les prix deviennent plus instables.")


def verifier_fin():
    if argent >= objectif_argent:
        print("\nBRAVO ! Tu as atteint l'objectif de", objectif_argent, "€.")
        print("Tu as gagné en", jour, "jours.")
        return True
    return False


# ----------------------------
# BOUCLE PRINCIPALE
# ----------------------------

while True:
    afficher_statut()
    menu()

    choix = input("Choix : ")

    if choix == "1":
        acheter()

    elif choix == "2":
        vendre()

    elif choix == "3":
        jour += 1
        faire_evoluer_prix()
        evenement_aleatoire()
        augmenter_difficulte()

        if verifier_fin():
            break

    elif choix == "4":
        print("Fin du jeu.")
        break

    else:
        print("Choix invalide.")