import tkinter as tk
from tkinter import messagebox
import main as logic

# Initialisation du prix
logic.prix = logic.changer_prix()

# Fenêtre principale
root = tk.Tk()
root.title("Simulation de Bourse")
root.geometry("500x600")
root.configure(bg="#f3f4f6")

# ====== FONCTIONS ======

def refresh():
    state = logic.get_state()
    label_jour.config(text=state["jour"])
    label_prix.config(text=f"{state['prix']} €")
    label_argent.config(text=f"{state['argent']} €")
    label_stock.config(text=state["stock"])

def get_quantite():
    try:
        q = int(entry_quantite.get())
        if q <= 0:
            raise ValueError
        return q
    except:
        messagebox.showerror("Erreur", "Quantité invalide")
        return None

def acheter():
    quantite = get_quantite()
    if quantite is None:
        return

    result = logic.effectuer_achat(quantite)

    if result != "OK":
        messagebox.showerror("Erreur", result)

    refresh()

def vendre():
    quantite = get_quantite()
    if quantite is None:
        return

    result = logic.effectuer_vente(quantite)

    if result != "OK":
        messagebox.showerror("Erreur", result)

    refresh()

def jour_suivant():
    logic.jour += 1
    logic.prix = logic.changer_prix()
    refresh()

# ====== UI ======

frame = tk.Frame(root, bg="white", padx=20, pady=20)
frame.pack(padx=20, pady=20, fill="both", expand=True)

title = tk.Label(frame, text="Simulation de Bourse", font=("Arial", 18, "bold"))
title.pack(pady=10)

# Infos
info_frame = tk.Frame(frame)
info_frame.pack(pady=10)

def create_box(parent, label_text):
    box = tk.Frame(parent, bg="#f9fafb", padx=10, pady=10)
    title = tk.Label(box, text=label_text, fg="gray")
    value = tk.Label(box, text="", font=("Arial", 12, "bold"))
    title.pack()
    value.pack()
    return box, value

box1, label_jour = create_box(info_frame, "Jour")
box2, label_prix = create_box(info_frame, "Prix de l'action")
box3, label_argent = create_box(info_frame, "Solde")
box4, label_stock = create_box(info_frame, "Actions détenues")

box1.grid(row=0, column=0, padx=5, pady=5)
box2.grid(row=0, column=1, padx=5, pady=5)
box3.grid(row=1, column=0, padx=5, pady=5)
box4.grid(row=1, column=1, padx=5, pady=5)

# Transaction
trans_frame = tk.Frame(frame, bg="#f9fafb", padx=10, pady=10)
trans_frame.pack(pady=20, fill="x")

tk.Label(trans_frame, text="Transactions", font=("Arial", 12, "bold")).pack(pady=5)

entry_quantite = tk.Entry(trans_frame)
entry_quantite.pack(pady=10)

btn_frame = tk.Frame(trans_frame)
btn_frame.pack()

btn_buy = tk.Button(btn_frame, text="Acheter", bg="green", fg="white", width=12, command=acheter)
btn_sell = tk.Button(btn_frame, text="Vendre", bg="red", fg="white", width=12, command=vendre)

btn_buy.grid(row=0, column=0, padx=5)
btn_sell.grid(row=0, column=1, padx=5)

# Bouton jour suivant
btn_next = tk.Button(
    frame,
    text="Passer au jour suivant",
    bg="blue",
    fg="white",
    padx=10,
    pady=5,
    command=jour_suivant
)
btn_next.pack(pady=20)

# Initialisation affichage
refresh()

root.mainloop()