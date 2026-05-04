import random

argent = 100
stock = 0
limite_stock = 10
jour = 1
prix = 0

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

def acheter_console():
    global argent, stock
    try:
        quantite = int(input("Combien veux-tu acheter ? "))
    except ValueError:
        print("Valeur invalide.")
        return

    effectuer_achat(quantite)

def vendre_console():
    global argent, stock
    try:
        quantite = int(input("Combien veux-tu vendre ? "))
    except ValueError:
        print("Valeur invalide.")
        return

    effectuer_vente(quantite)

# ✅ Fonctions utilisables par Tkinter
def effectuer_achat(quantite):
    global argent, stock

    if quantite <= 0:
        return "Quantité invalide"

    cout = quantite * prix

    if cout > argent:
        return "Pas assez d'argent"

    if stock + quantite > limite_stock:
        return "Stock plein"

    argent -= cout
    stock += quantite
    return "OK"

def effectuer_vente(quantite):
    global argent, stock

    if quantite <= 0:
        return "Quantité invalide"

    if quantite > stock:
        return "Pas assez de stock"

    argent += quantite * prix
    stock -= quantite
    return "OK"

def changer_prix():
    return random.randint(1, 20)

# ✅ Fonction pour récupérer les valeurs (utile Tkinter)
def get_state():
    return {
        "jour": jour,
        "argent": argent,
        "stock": stock,
        "prix": prix,
        "limite": limite_stock
    }

# ✅ Boucle console isolée
def main():
    global prix, jour

    while True:
        prix = changer_prix()
        afficher_statut()
        menu()

        choix = input("Choix : ")

        if choix == "1":
            acheter_console()
        elif choix == "2":
            vendre_console()
        elif choix == "3":
            jour += 1
        elif choix == "4":
            print("Fin du jeu.")
            break
        else:
            print("Choix invalide.")

# ⚠️ IMPORTANT
if __name__ == "__main__":
    main()