import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Zoo Daiza Pairi")
root.geometry("1000x700")
root.configure(bg="#EDE3E3")

# ================= HEADER =================
header = tk.Frame(root, bg="black", height=300)
header.pack(fill="x")

title = tk.Label(header, text="Bienvenue", fg="white", bg="black",
                 font=("Arial", 32, "bold"))
title.place(relx=0.5, rely=0.35, anchor="center")

subtitle = tk.Label(header, text="Au zoo de Daiza Pairi",
                    fg="white", bg="black",
                    font=("Arial", 18))
subtitle.place(relx=0.5, rely=0.55, anchor="center")

def scroll_to_content():
    content_frame.focus_set()

btn = tk.Button(header, text="Nous découvrir ↓",
                bg="#16a34a", fg="white",
                font=("Arial", 12, "bold"),
                command=scroll_to_content)
btn.place(relx=0.5, rely=0.75, anchor="center")

# ================= CONTENT =================
content_frame = tk.Frame(root, bg="white", padx=20, pady=20)
content_frame.pack(pady=20, padx=20, fill="both", expand=True)

title2 = tk.Label(content_frame,
                  text="🌿 Bienvenue au Zoo Daiza Pairi",
                  fg="#15803d",
                  bg="white",
                  font=("Arial", 20, "bold"))
title2.pack(pady=10)

text = tk.Label(content_frame,
                text=("Entrez dans un sanctuaire naturel unique en Europe.\n"
                      "Une expérience immersive et inoubliable."),
                bg="white",
                fg="gray",
                font=("Arial", 12),
                justify="center")
text.pack(pady=10)

# Buttons section
btn_frame = tk.Frame(content_frame, bg="white")
btn_frame.pack(pady=15)

tk.Button(btn_frame, text="🐾 Explorer les animaux",
          bg="#16a34a", fg="white", padx=10, pady=5).pack(side="left", padx=10)

tk.Button(btn_frame, text="🎉 Événements à venir",
          bg="#16a34a", fg="white", padx=10, pady=5).pack(side="left", padx=10)

# Separator
ttk.Separator(content_frame, orient="horizontal").pack(fill="x", pady=20)

quote = tk.Label(content_frame,
                 text="« Un voyage à travers les continents et les espèces. »",
                 bg="white",
                 fg="gray",
                 font=("Arial", 11, "italic"))
quote.pack(pady=10)

# Calendar placeholder
calendar_frame = tk.Frame(content_frame, bg="#EDE3E3", height=200)
calendar_frame.pack(fill="x", pady=20)

calendar_label = tk.Label(calendar_frame,
                          text="📅 Calendrier (version simplifiée)",
                          bg="#EDE3E3",
                          font=("Arial", 14))
calendar_label.pack(pady=50)

root.mainloop()