import random

argent = 100
stock = 0
limite_stock = 10
jour = 1

def afficher_statut():
    print("\n--- JOUR", jour, "---")
    print("Argent :", argent, "€")
    print("Stock :", stock)
    print("Prix actuel :", prix, "€")
    print("Limite de stock :", limite_stock)

def menu():
    print("\n1 - Acheter")
    print("2 - Vendre")
    print("3 - Passer au jour suivant")
    print("4 - Quitter")

def acheter():
    global argent, stock
    try:
        quantite = int(input("Combien veux-tu acheter ? "))
    except ValueError:
        print("Valeur invalide. Entre un nombre entier.")
        return

    if quantite <= 0:
        print("La quantité doit être positive.")
        return

    cout = quantite * prix
    if cout > argent:
        print("Pas assez d'argent !")
        return

    if stock + quantite > limite_stock:
        print("Pas assez d'espace dans le stock !")
        return

    argent -= cout
    stock += quantite
    print("Achat réussi !")


def vendre():
    global argent, stock
    try:
        quantite = int(input("Combien veux-tu vendre ? "))
    except ValueError:
        print("Valeur invalide. Entre un nombre entier.")
        return

    if quantite <= 0:
        print("La quantité doit être positive.")
        return

    if quantite <= stock:
        argent += quantite * prix
        stock -= quantite
        print("Vente réussie !")
    else:
        print("Pas assez de stock !")

def changer_prix():
    return random.randint(1, 20)

# boucle principale
while True:
    prix = changer_prix()
    afficher_statut()
    menu()

    choix = input("Choix : ")

    if choix == "1":
        acheter()
    elif choix == "2":
        vendre()
    elif choix == "3":
        jour += 1
    elif choix == "4":
        print("Fin du jeu.")
        break
    else:
        print("Choix invalide.")
