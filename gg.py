import tkinter as tk
from tkinter import messagebox
from tkinter.simpledialog import askstring
from tkinter import ttk
import json
from PIL import ImageTk, Image,ImageGrab
import shutil
import io
import os
import cv2

class MyApp:

    IMAGE_DIRECTORY = "C:/Users/Tshala Benjamin/AppData/Local/Programs/Python/Python39/ailine/image_corps"
    
    def __init__(self, root):
        self.root = root
        self.root.title("Mon application")
        self.root.geometry("400x400")

         # Change the background color to blue
        self.root.configure(bg='#F0F0F8')

        # Frame pour la séparation
        #self.separator_frame = tk.Frame(root, height=2, bg="black")
        #self.separator_frame.pack(fill=tk.X, padx=10, pady=10)

        # Création du menu
        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)

        # Menu "Patient"
        self.patient_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Patient", menu=self.patient_menu)
        self.patient_menu.add_command(label="Modifier patient", command=self.modify_patient)
        self.patient_menu.add_command(label="Supprimer patients", command=self.delete_patients)
        self.patient_menu.add_command(label="Voir les archives", command=self.view_archives)

        # Bouton "Enregistrer patient"
        self.button_save = tk.Button(root, text="Enregistrer patient", command=self.open_patient_page, bg='#F0F0F8')
        self.button_save.pack(pady=10, fill=tk.BOTH, expand=True)

        # Frame pour la séparation
        #self.separator_frame = tk.Frame(root, height=2, bg="black")
        #self.separator_frame.pack(fill=tk.X, padx=10, pady=10)

        # Label et Combobox pour sélectionner le critère de recherche

        style = ttk.Style()
        style.map('TCombobox', fieldbackground=[('readonly','white')], selectbackground=[('readonly', 'white')], selectforeground=[('readonly', 'black')])
        tk.Label(root, text="Critère de recherche:").pack()
        self.search_criteria = ttk.Combobox(root, values=["Nom", "Prénom", "Âge", "Diagnostic"], style='TCombobox', state='readonly')
        self.search_criteria.pack()

        # Bouton "Rechercher patients"
        self.button_search = tk.Button(root, text="Rechercher patients", command=self.search_patients,  bg='#F0F0F8')
        self.button_search.pack(pady=10, fill=tk.BOTH, expand=True)

        # Bouton "Afficher tous les patients"
        self.button_show_all = tk.Button(root, text="Afficher tous les patients", command=self.show_all_patients,  bg='#F0F0F8')
        self.button_show_all.pack(pady=10, fill=tk.BOTH, expand=True)

        # Liste des patients enregistrés
        self.patient_list = self.load_patients()

        # Création de la barre de défilement
        self.scrollbar = tk.Scrollbar(root)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Création du widget Listbox
        self.patient_listbox = tk.Listbox(root, yscrollcommand=self.scrollbar.set, bg='white')
        self.patient_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

        # Configuration de la barre de défilement
        self.scrollbar.config(command=self.patient_listbox.yview)
        

        # Mettre à jour la Listbox avec les patients enregistrés
        self.update_patient_listbox()

        #interagir avec la listbox
        self.patient_listbox.bind("<Button-3>", self.show_context_menu)



    def show_context_menu(self, event):
                # Obtenir l'index de l'élément le plus proche du curseur de la souris
            nearest_index = self.patient_listbox.nearest(event.y)

                # Désélectionner tous les éléments de la Listbox
            self.patient_listbox.selection_clear(0, tk.END)

            # Sélectionner l'élément le plus proche du curseur de la souris
            self.patient_listbox.selection_set(nearest_index)
             # Afficher le menu contextuel à la position du clic de souris
            if self.patient_listbox.curselection():
                # Créer le menu contextuel
                context_menu = tk.Menu(self.patient_listbox, tearoff=0)
                context_menu.add_command(label="Supprimer", command=self.delete_patient)
                context_menu.add_command(label="Modifier", command=self.modify )
                context_menu.add_command(label="Archiver", command=self.archive_patient)
                context_menu.add_command(label="Diagnostic", command=self.diagnostic_view)
                
                 # Afficher le menu contextuel à la position du clic de souris
                context_menu.tk_popup(event.x_root, event.y_root)


    def delete_patient(self):
        # Obtenir l'index de l'élément sélectionné dans la Listbox
        selected_index = self.patient_listbox.curselection()[0]

        # Obtenir le patient correspondant à l'index sélectionné
        selected_patient = self.patient_list[selected_index]

        # Demander confirmation pour la suppression du patient
        confirmed = messagebox.askyesno("Supprimer patient", f"Êtes-vous sûr de vouloir supprimer le patient {selected_patient['Nom']} ?")
        name = selected_patient["Nom"]
        lastname = selected_patient["Prénom"]
        image_path = f"C:/Users/Tshala Benjamin/AppData/Local/Programs/Python/Python39/ailine/image_corps/{name}_{lastname}.png"           
        perine_image_path = f"C:/Users/Tshala Benjamin/AppData/Local/Programs/Python/Python39/ailine/image_corps/{name}_{lastname}_perine.jpg"

        if confirmed:
            # Supprimer le patient de la liste des patients
            del self.patient_list[selected_index]
            if os.path.exists(image_path):
               os.remove(image_path)

            if os.path.exists(perine_image_path):
               os.remove(perine_image_path)

            # Mettre à jour la Listbox avec les patients restants
            self.update_patient_listbox()

            # Ouvrir le fichier JSON, supprimer le patient, et réécrire le fichier
            with open('patients.json', 'r+') as f:
                data = json.load(f)
                data.remove(selected_patient)
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()

                # Mettre à jour la Listbox avec les patients restants
                self.update_patient_listbox()
                
                # Save the changes in the JSON file
                self.save_patients()

    def diagnostic_view(self):
        # Récupérer l'indice de l'élément sélectionné
        selected_index = self.patient_listbox.curselection()[0]

        # Obtenir les informations du patient sélectionné
        selected_patient = self.patient_list[selected_index]
        

        # Récupérer le diagnostic du patient
        diagnosis = selected_patient["Diagnostic"]

        # Garder une trace du texte initial pour vérifier plus tard s'il a été modifié
        self.initial_diagnosis = diagnosis

        # Créer une nouvelle fenêtre toplevel pour afficher le diagnostic
        diagnosis_window = tk.Toplevel(self.root)
        diagnosis_window.title("Diagnostic du patient")

        # Définir l'icône de la fenêtre
        diagnosis_window.iconbitmap('C:/Users/Tshala Benjamin/Downloads/papio.ico')

        # Définir l'arrière-plan de la fenêtre en bleu clair
        diagnosis_window.configure(bg='light blue')


        # Bloquer la modification de la taille de la fenêtre
        diagnosis_window.resizable(False, False)

        # Créer un widget de texte pour afficher le diagnostic
        text_widget = tk.Text(diagnosis_window, height=14, bg='white', fg='black')
        text_widget.grid(row=0, column=0, sticky='n')

       # Créer une Frame pour les champs Antecedent et Traitement
        entry_frame = tk.Frame(diagnosis_window, bg='light blue')
        entry_frame.grid(row=1, column=0, sticky='ew')
        

        # Ajouter deux champs d'entrée pour Antecedent et Traitement dans la Frame
        antecedent_label = tk.Label(entry_frame, text="Antecedent:", bg='light blue')
        antecedent_label.grid(row=0, column=0, sticky='w', pady=(30, 0))
        antecedent_text = tk.Text(entry_frame, width=80, height=2, bg='white', fg='black')  # changez la hauteur en fonction de vos besoins
        antecedent_text.grid(row=1, column=0, sticky='ew', pady=(5, 20), padx=(20, 0))  # Augmentez la largeur si nécessaire
        #antecedent_entry.grid(row=0, column=1, sticky='ew')
        if 'Antecedent' in selected_patient:
            antecedent_text.insert(tk.END, selected_patient['Antecedent'])


        treatment_label = tk.Label(entry_frame, text="Traitement:", bg='light blue')
        treatment_label.grid(row=1, column=0, sticky='w', pady=(58, 5))
        treatment_text = tk.Text(entry_frame, width=50, height=2, bg='white', fg='black')  # changez la hauteur en fonction de vos besoins
        treatment_text.grid(row=2, column=0, sticky='ew', pady=5, padx=(20, 0))
        #treatment_entry.grid(row=1, column=1, sticky='ew')
                
        if 'Traitement' in selected_patient:
            treatment_text.insert(tk.END, selected_patient['Traitement'])

        # Faire en sorte que la deuxième colonne de la frame (où se trouvent les champs Entry) s'étende pour remplir l'espace disponible
        entry_frame.columnconfigure(1, weight=1)
        # Ajouter une scrollbar
        scrollbar = tk.Scrollbar(diagnosis_window, command=text_widget.yview)  # yview pour la barre de défilement verticale
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Lier la barre de défilement au widget de texte
        text_widget['yscrollcommand'] = scrollbar.set

        # Créer un conteneur Frame pour les boutons
        button_frame = tk.Frame(diagnosis_window, bg='light blue')
        button_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Bouton "Enregistrer"
        button_save = tk.Button(button_frame, text="Enregistrer", command=lambda: self.diagno_save(selected_patient, text_widget, antecedent_text, treatment_text, diagnosis_window), bg='skyblue')
        button_save.pack(pady=5)
        



        # Intercepter l'événement de fermeture de la fenêtre
        diagnosis_window.protocol("WM_DELETE_WINDOW", lambda: self.check_changes_and_close(diagnosis_window, text_widget, selected_patient))

        # Ajouter le diagnostic dans le widget de texte
        text_widget.insert(tk.END, diagnosis)

        # Création du Canvas à droite
        canvas = tk.Canvas(diagnosis_window, width=300, height=300, bg='white')
        canvas.grid(row=0, column=2, rowspan=2, padx=10, pady=10)

        # Recuperer le nom e prenom du patient selectionner
        name = selected_patient["Nom"]
        lastname = selected_patient["Prénom"]

        # Charger l'image du patient
        image_path = f"C:/Users/Tshala Benjamin/AppData/Local/Programs/Python/Python39/ailine/image_corps/{name}_{lastname}.png"  # Mettez ici le vrai chemin de l'image
        image = Image.open(image_path)

        # Redimensionner l'image pour qu'elle s'adapte au Canvas
        image = image.resize((300, 300), Image.ANTIALIAS)

        # Convertir l'image PIL en une image que Tkinter peut utiliser
        tk_image = ImageTk.PhotoImage(image)

        # Ajouter l'image au Canvas
        canvas.create_image(0, 0, image=tk_image, anchor='nw')

        # Stocker une référence à l'image (sinon, elle sera effacée par le garbage collector)
        canvas.image = tk_image

        # Define the perine image path
        perine_image_path = f"C:/Users/Tshala Benjamin/AppData/Local/Programs/Python/Python39/ailine/image_corps/{name}_{lastname}_perine.jpg"

        # Check if the image file exists
        if os.path.isfile(perine_image_path):
            # If the image exists, create the Canvas
            canvas_2 = tk.Canvas(diagnosis_window, width=300, height=300, bg='white')
            canvas_2.grid(row=0, column=3, rowspan=2, padx=10, pady=10)  # Adjust the grid placement accordingly

            # Load the perine image
            perine_image = Image.open(perine_image_path)

            # Resize the image to fit the Canvas
            perine_image = perine_image.resize((300, 300), Image.ANTIALIAS)

            # Convert the PIL image into an image that Tkinter can use
            tk_perine_image = ImageTk.PhotoImage(perine_image)

            # Add the image to the Canvas
            canvas_2.create_image(0, 0, image=tk_perine_image, anchor='nw')

            # Store a reference to the image (otherwise, it will be erased by the garbage collector)
            canvas_2.image = tk_perine_image




    def check_changes_and_close(self, window, text_widget, patient):
        # Obtenir le texte actuel dans le widget
        current_text = text_widget.get("1.0", tk.END).strip()

        # Vérifier si le texte a été modifié
        if current_text != self.initial_diagnosis:
        # Si le texte a été modifié, demander à l'utilisateur s'il souhaite enregistrer les modifications
           if messagebox.askyesno("Enregistrer les modifications", "Le diagnostic a été modifié. Voulez-vous enregistrer les modifications ?"):
        # Si l'utilisateur a répondu oui, enregistrer les modifications
            self.diagno_save(patient, text_widget)

           else:
                # Fermer la fenêtre
                window.destroy()
        else:
            window.destroy()


    def diagno_save(self, patient, text_widget, antecedent_text, treatment_text, window):
        # Mettre à jour le diagnostic du patient
        patient["Diagnostic"] = text_widget.get("1.0", tk.END).strip()
        patient["Antecedent"] = antecedent_text.get("1.0", tk.END).strip()
        patient["Traitement"] = treatment_text.get("1.0", tk.END).strip()
        
        # Sauvegarder les modifications dans le fichier JSON
        self.save_patients()

        # Mettre à jour la Listbox avec les patients enregistrés
        self.update_patient_listbox()

        messagebox.showinfo("Modifier diagnostic", "Le diagnostic du patient a été mis à jour avec succès.")

        window.destroy()
        

    def open_patient_page(self):
        self.patient_window = tk.Toplevel(self.root)
        self.patient_window.title("Page de saisie du patient")

         # Définir l'icône de la fenêtre
        self.patient_window.iconbitmap('C:/Users/Tshala Benjamin/Downloads/papio.ico')

        # Créez un menu principal
        menu = tk.Menu(self.patient_window)
        self.patient_window.config(menu=menu)

        # Ajoutez le sous-menu "Périné"
        perine_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Périné", menu=perine_menu)

        # Ajoutez des options à votre sous-menu "Périné" si nécessaire
        # Par exemple :
        perine_menu.add_command(label="Image", command= self.perine)
    
 
        # Bloquer la modification de la taille de la fenêtre
        self.patient_window.resizable(False, False)
        self.patient_window.configure(bg='lightblue')

        # Create grid layout
        for r in range(8):
            self.patient_window.rowconfigure(r, weight=1)
        for c in range(2):
            self.patient_window.columnconfigure(c, weight=1)

        # Labels et champs de saisie pour le nom, le prénom, la date de naissance
        tk.Label(self.patient_window, text="Nom:", bg='lightblue').grid(row=0, column=0)
        entry_name = tk.Entry(self.patient_window)
        entry_name.grid(row=0, column=1)

        tk.Label(self.patient_window, text="Prénom:", bg='lightblue').grid(row=1, column=0)
        entry_lastname = tk.Entry(self.patient_window)
        entry_lastname.grid(row=1, column=1)

        tk.Label(self.patient_window, text="Âge:", bg='lightblue').grid(row=2, column=0)
        entry_birthdate = tk.Entry(self.patient_window)
        entry_birthdate.grid(row=2, column=1)

        # Label pour le sexe
        tk.Label(self.patient_window, text="Sexe:", bg='lightblue').grid(row=3, column=0)

        # Radio buttons pour le sexe
        self.gender = tk.StringVar()  # crée une variable pour stocker le sexe
        self.gender.set("Homme")
        tk.Radiobutton(self.patient_window, text="H", variable=self.gender, value="Homme", bg='lightblue').grid(row=3, column=1, padx=50)
        tk.Radiobutton(self.patient_window, text="F", variable=self.gender, value="Femme", bg='lightblue').grid(row=3, column=1, sticky='E', padx=50)

        tk.Label(self.patient_window, text="Diagnostic:", bg='lightblue').grid(row=4, column=0)
        entry_diagnosis = tk.Entry(self.patient_window)
        entry_diagnosis.grid(row=4, column=1)

        # Créer une Frame pour les champs Antecedent et Traitement
        entry_frame = tk.Frame(self.patient_window, bg='lightblue')
        entry_frame.grid(row=5, column=0, columnspan=2, padx=10)

        # Ajouter deux champs d'entrée pour Antecedent et Traitement dans la Frame
        tk.Label(entry_frame, text="Antecedent:", bg='lightblue').grid(row=0, column=0)
        entry_antecedent = tk.Text(entry_frame, width=30, height=4, bg='white', fg='black', padx=10)
        entry_antecedent.grid(row=0, column=1, pady=10)

        tk.Label(entry_frame, text="Traitement:", bg='lightblue').grid(row=1, column=0)
        entry_treatment = tk.Text(entry_frame, width=30, height=4, bg='white', fg='black', padx=10)
        entry_treatment.grid(row=1, column=1, pady=10)

        # Définir une fonction intermédiaire pour le bouton "Enregistrer"
        def save_and_on_ok():
            self.save_patient(
                entry_name.get(),
                entry_lastname.get(),
                entry_birthdate.get(),
                entry_diagnosis.get(),
                entry_antecedent.get("1.0", 'end-1c').strip(),
                entry_treatment.get("1.0", 'end-1c').strip(),
                self.gender.get()
            )
            if hasattr(self, 'canvas_2'):
                file_path = self.on_ok(entry_name.get(), entry_lastname.get(), self.canvas_2)
                close_window()
               
            # Utilisez le chemin d'accès à l'image pour le traitement supplémentaire
            # par exemple, enregistrement dans une base de données, affichage, etc.

        # Bouton "Enregistrer"
        button_save_patient = tk.Button(
            self.patient_window,
            text="Enregistrer",
            command=save_and_on_ok,
            bg='skyblue',
            fg='black'
        )
        button_save_patient.grid(row=6, column=0, columnspan=2)

        def close_window():
            self.patient_window.destroy()

        # Création du canevas pour afficher l'image
        self.canvas = tk.Canvas(self.patient_window, width=300, height=300, bg='lightblue')
        self.canvas.grid(row=0, column=2, rowspan=7)

        # Chargement de l'image
        image_path = "C:/Users/Tshala Benjamin/Desktop/corps_humain.jpg"  # Remplacez par le chemin d'accès à votre image
        self.image = Image.open(image_path)
        self.image = self.image.resize((300, 300), Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(self.image)

        # Affichage de l'image sur le canevas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # Ajout de la gestion des événements de souris sur le canevas
        self.canvas.bind("<Button-1>", self.add_red_dot)
        self.canvas.bind("<Button-3>", self.remove_red_dot)

   #mehode pour afficher le périné
    def perine(self):
        # Créer une nouvelle fenêtre
        self.perine_window = tk.Toplevel(self.root)
        self.perine_window.title("Périné")

        # Bloquer la modification de la taille de la fenêtre
        self.perine_window.resizable(False, False)
        self.perine_window.configure(bg='lightblue')

        # Création du canevas pour afficher l'image
        self.canvas_2 = tk.Canvas(self.perine_window, width=300, height=300, bg='lightblue')
        self.canvas_2.pack()

        # Chargement de l'image
        image_path = "C:/Users/Tshala Benjamin/Desktop/perine_image.jpg"  # Remplacez par le chemin d'accès à votre image
        image = Image.open(image_path)
        image = image.resize((300, 300), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)

        # Affichage de l'image sur le canevas
        self.canvas_2.create_image(0, 0, anchor=tk.NW, image=photo)

        # Conserver une référence à l'image pour éviter qu'elle ne soit effacée par le ramasse-miettes de Python
        self.canvas_2.image = photo


        # Fonction pour ajouter un point rouge sur le canevas
        def add_red_dot(event):
            x = event.x
            y = event.y
            self.canvas_2.create_oval(x - 4, y - 4, x + 4, y + 4, fill="lightblue", tags="red_dot")

        # Fonction pour supprimer un point rouge sur le canevas
        def remove_red_dot(event):
             # Suppression du point rouge à la position du clic de souris (bouton droit)
            if event.num == 3:
                red_dots = self.canvas_2.find_withtag("red_dot")
                for dot in red_dots:
                    self.canvas_2.delete(dot)

 
        # Ajout de la gestion des événements de souris sur le canevas
        self.canvas_2.bind("<Button-1>", add_red_dot)
        self.canvas_2.bind("<Button-3>", remove_red_dot)

    #methode bouton ok , périné
    def on_ok(self, name, lastname, canvas_2):
        # Définir le répertoire de destination pour enregistrer l'image
        destination_directory = "C:/Users/Tshala Benjamin/AppData/Local/Programs/Python/Python39/ailine/image_corps"

        # Générer un nom de fichier unique
        file_name = f"{name}_{lastname}_perine.jpg"

        # Chemin complet du fichier
        file_path = os.path.join(destination_directory, file_name)

        # Enregistre le contenu du canvas en format Postscript
        self.canvas_2.postscript(file="temp.ps", colormode='color')

        # Convertit le fichier .ps en .png
        from PIL import Image as NewImage
        img = NewImage.open("temp.ps")
        img.save(file_path, "PNG")

        # Important: Ferme l'image après l'avoir sauvegardée
        img.close()

        # Supprime le fichier temporaire .ps
        os.remove("temp.ps")

        # Ferme la fenêtre 'perine_window' si elle existe
        if hasattr(self, 'perine_window'):
            self.perine_window.destroy()
       
        return file_path

        


    def modify(self): #methode pour modifier dans la listbox
         # Récupérer l'indice de l'élément sélectionné
        selected_index = self.patient_listbox.curselection()[0]

                # Obtenir les informations du patient sélectionné
        selected_patient = self.patient_list[selected_index]

                # Ouvrir une fenêtre de modification du patient avec les données existantes
        self.modify_patient_window(selected_patient)




    def add_red_dot(self, event):
        # Ajout d'un point rouge à la position du clic de souris
        x = event.x
        y = event.y
        self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="lightblue", tags="red_dot")
        
    def remove_red_dot(self, event):
        # Suppression du point rouge à la position du clic de souris (bouton droit)
        if event.num == 3:
            red_dots = self.canvas.find_withtag("red_dot")
            for dot in red_dots:
                self.canvas.delete(dot)

    def save_patient(self, name, lastname, birthdate, diagnosis, antecedent, treatment, gender):
        # Créer un dictionnaire avec les données du patient
        patient_data = {
            "Nom": name,
            "Prénom": lastname,
            "Date de naissance": birthdate,
            "Diagnostic": diagnosis,
            "Sexe": gender,
            "Antecedent": antecedent,
            "Traitement": treatment
            
        }

        # Ajouter le patient à la liste des patients enregistrés
        self.patient_list.append(patient_data)
        # Update gender count and total age
        #self.patient_gender_count[gender] += 1
        #self.patient_total_age += int(birthdate)
        #self.patient_count += 1

        self.save_patients()
        
        #########################################""
        # Enregistrer le canevas et récupérer le chemin d'accès à l'image enregistrée
        image_path = self.save_canvas(name, lastname)

        # Ajouter le chemin d'accès à l'image dans le dictionnaire patient_data
        patient_data["Image"] = image_path

        
        # Enregistrer le canevas
        self.save_canvas(name, lastname)
        ###########################################

        messagebox.showinfo("Enregistrer patient", "Le patient a été enregistré avec succès.")

        # Mettre à jour la Listbox avec les patients enregistrés
        self.update_patient_listbox()  






       ###################################################
    def save_canvas(self, name, lastname):
        # Définir le répertoire de destination pour enregistrer l'image
        destination_directory = "C:/Users/Tshala Benjamin/AppData/Local/Programs/Python/Python39/ailine/image_corps"

        # Générer un nom de fichier unique
        file_name = f"{name}_{lastname}.png"

        # Chemin complet du fichier
        file_path = os.path.join(destination_directory, file_name)

        # Capturer l'image du canevas
        image = ImageGrab.grab(bbox=(self.canvas.winfo_rootx(), self.canvas.winfo_rooty(), self.canvas.winfo_rootx() + self.canvas.winfo_width(), self.canvas.winfo_rooty() + self.canvas.winfo_height()))

        
        # Enregistrer l'image au format PNG
        image.save(file_path, "PNG")

        return file_path
    ########################################################
        

    def save_patients(self):
        with open("C:/Users/Tshala Benjamin/AppData/Local/Programs/Python/Python39/ailine/patients.json", "w") as file:
            json.dump(self.patient_list, file)

    def load_patients(self):
        try:
            with open("C:/Users/Tshala Benjamin/AppData/Local/Programs/Python/Python39/ailine/patients.json", "r") as file:
                patients = json.load(file)
        except FileNotFoundError:
            patients = []

        return patients

    def update_patient_listbox(self):
        # Effacer le contenu de la Listbox
        self.patient_listbox.delete(0, tk.END)

        # Parcourir la liste des patients et les ajouter à la Listbox
        for patient in self.patient_list:
            patient_info = f"Nom: {patient['Nom']} - Prénom: {patient['Prénom']} - Age: {patient['Date de naissance']} - Diagnostic: {patient['Diagnostic']}"
            self.patient_listbox.insert(tk.END, patient_info)

    def search_patients(self):
        # Récupérer le critère de recherche sélectionné
        search_criteria = self.search_criteria.get()

        if search_criteria:
            # Demander la valeur de recherche correspondante au critère sélectionné
            search_value = askstring("Rechercher patients", f"Entrez le {search_criteria.lower()} du patient à rechercher")

            if search_value:
                # Charger les patients depuis le fichier JSON
                self.patient_list = self.load_patients()

                # Chercher les patients correspondant au critère de recherche
                matching_patients = []
                for patient in self.patient_list:
                    if search_criteria == "Nom" and patient["Nom"].lower() == search_value.lower():
                        matching_patients.append(patient)
                    elif search_criteria == "Prénom" and patient["Prénom"].lower() == search_value.lower():
                        matching_patients.append(patient)
                    elif search_criteria == "Âge" and patient["Date de naissance"] == search_value:
                        matching_patients.append(patient)
                    elif search_criteria == "Diagnostic" and patient["Diagnostic"].lower() == search_value.lower():
                        matching_patients.append(patient)

                if matching_patients:
                    # Afficher les résultats de la recherche
                    result_text = ""
                    for patient in matching_patients:
                        result_text += f"Nom: {patient['Nom']}\nPrénom: {patient['Prénom']}\nDate de naissance: {patient['Date de naissance']}\nDiagnostic: {patient['Diagnostic']}\n\n"

                    messagebox.showinfo("Rechercher patients", result_text)
                else:
                    messagebox.showinfo("Rechercher patients", "Aucun patient trouvé avec ce critère de recherche.")

    def show_all_patients(self):
        # Charger les patients depuis le fichier JSON
        self.patient_list = self.load_patients()

        if self.patient_list:
            result_text = ""
            for patient in self.patient_list:
                result_text += f"Nom: {patient['Nom']}\nPrénom: {patient['Prénom']}\nDate de naissance: {patient['Date de naissance']}\nDiagnostic: {patient['Diagnostic']}\n\n"

            messagebox.showinfo("Tous les patients", result_text)
        else:
            messagebox.showinfo("Tous les patients", "Aucun patient enregistré.")

    def modify_patient(self):
        if self.patient_list:
            # Sélectionner le patient à modifier
            selected_patient = askstring("Modifier patient", "Entrez le nom du patient à modifier")

            if selected_patient:
                # Rechercher le patient dans la liste
                for patient in self.patient_list:
                    if patient["Nom"].lower() == selected_patient.lower():
                        # Ouvrir la fenêtre de modification du patient
                        self.modify_patient_window(patient)
                        break
                else:
                    messagebox.showinfo("Modifier patient", "Aucun patient trouvé avec ce nom.")
        else:
            messagebox.showinfo("Modifier patient", "Aucun patient enregistré.")

    def modify_patient_window(self, patient):
        # Ouvrir une fenêtre de modification du patient avec les données existantes
        self.patient_window = tk.Toplevel(self.root)
        self.patient_window.title("Modification du patient")

        # Définir l'icône de la fenêtre
        self.patient_window.iconbitmap('C:/Users/Tshala Benjamin/Downloads/papio.ico')

        # Labels et champs de saisie pour le nom, le prénom, la date de naissance et le diagnostic
        tk.Label(self.patient_window, text="Nom:").pack()
        entry_name = tk.Entry(self.patient_window)
        entry_name.insert(tk.END, patient["Nom"])
        entry_name.pack()

        tk.Label(self.patient_window, text="Prénom:").pack()
        entry_lastname = tk.Entry(self.patient_window)
        entry_lastname.insert(tk.END, patient["Prénom"])
        entry_lastname.pack()

        tk.Label(self.patient_window, text="Âge:").pack()
        entry_birthdate = tk.Entry(self.patient_window)
        entry_birthdate.insert(tk.END, patient["Date de naissance"])
        entry_birthdate.pack()

        tk.Label(self.patient_window, text="Diagnostic:").pack()
        entry_diagnosis = tk.Entry(self.patient_window)
        entry_diagnosis.insert(tk.END, patient["Diagnostic"])
        entry_diagnosis.pack()

        tk.Label(self.patient_window, text="Antecedent:").pack()
        entry_antecedent = tk.Text(self.patient_window, width=30, height=4, bg='white', fg='black', padx=10)
        entry_antecedent.insert(tk.END, patient.get("Antecedent", ""))
        entry_antecedent.pack()

        tk.Label(self.patient_window, text="Traitement:").pack()
        entry_treatment = tk.Text(self.patient_window, width=30, height=4, bg='white', fg='black', padx=10)
        entry_treatment.insert(tk.END, patient.get("Traitement", ""))
        entry_treatment.pack()

        # Bouton "Enregistrer"
        button_save_patient = tk.Button(self.patient_window, text="Enregistrer", command=lambda: self.update_patient(patient, entry_name.get(), entry_lastname.get(), entry_birthdate.get(), entry_diagnosis.get(), entry_antecedent.get("1.0", 'end-1c').strip(), entry_treatment.get("1.0", 'end-1c').strip()))
        button_save_patient.pack(pady=10)
        def close_window():
            self.patient_window.destroy()

        # Ajouter une fonction pour fermer la fenêtre après avoir cliqué sur Enregistrer
        button_save_patient.configure(command=lambda: [self.update_patient(patient, entry_name.get(), entry_lastname.get(), entry_birthdate.get(), entry_diagnosis.get(), entry_antecedent.get("1.0", 'end-1c').strip(), entry_treatment.get("1.0", 'end-1c').strip()), close_window()])

    def update_patient(self, patient, name, lastname, birthdate, diagnosis, antecedent, treatment):
        # Mettre à jour les données du patient
        patient["Nom"] = name
        patient["Prénom"] = lastname
        patient["Date de naissance"] = birthdate
        patient["Diagnostic"] = diagnosis
        patient["Antecedent"] = antecedent
        patient["Traitement"] = treatment

         # Sauvegarder les modifications dans le fichier JSON
        self.save_patients()

        messagebox.showinfo("Modifier patient", "Les informations du patient ont été mises à jour.")

        # Mettre à jour la Listbox avec les patients enregistrés
        self.update_patient_listbox()
       
        

    def delete_patients(self):
        if self.patient_list:
            # Demander confirmation pour la suppression des patients
            selected_patient = askstring("Supprimer patient", "Entrez le nom du patient à supprimer")
            confirmed = messagebox.askyesno("Supprimer patients", "Êtes-vous sûr de vouloir supprimer le patient ?")

            if selected_patient and confirmed:
                # Rechercher le patient dans la liste
                for patient in self.patient_list:
                    if patient["Nom"].lower() == selected_patient.lower():
                        # Supprimer le patient de la liste
                        self.patient_list.remove(patient)
                        # Recuperer le nom e prenom du patient selectionner
                        name = patient["Nom"]
                        lastname = patient["Prénom"]
                        image_path = f"C:/Users/Tshala Benjamin/AppData/Local/Programs/Python/Python39/ailine/image_corps/{name}_{lastname}.png"
                        perine_image_path = f"C:/Users/Tshala Benjamin/AppData/Local/Programs/Python/Python39/ailine/image_corps/{name}_{lastname}_perine.jpg"
                        if os.path.exists(image_path):
                            os.remove(image_path)
                         # Delete the perine image if it exists
                        if os.path.exists(perine_image_path):
                            os.remove(perine_image_path)
                        # Sauvegarder les modifications dans le fichier JSON
                        self.save_patients()
                        messagebox.showinfo("Supprimer patient", "Le patient a été supprimé avec succès.")
                        break
                else:
                    messagebox.showinfo("Supprimer patient", "Aucun patient trouvé avec ce nom.")
        else:
            messagebox.showinfo("Supprimer patient", "Aucun patient enregistré.")


    def archive_patient(self):
         # Récupérer l'indice de l'élément sélectionné
        selected_index = self.patient_listbox.curselection()[0]

        # Obtenir les informations du patient sélectionné
        selected_patient = self.patient_list[selected_index]

        name = selected_patient["Nom"]
        lastname = selected_patient["Prénom"]
        # Spécifier le chemin des images originales
        image_path = f"C:/Users/Tshala Benjamin/AppData/Local/Programs/Python/Python39/ailine/image_corps/{name}_{lastname}.png"
        perine_image_path = f"C:/Users/Tshala Benjamin/AppData/Local/Programs/Python/Python39/ailine/image_corps/{name}_{lastname}_perine.jpg"

        # Spécifier le chemin de destination (le "dossier d'archives")
        archive_dir = "C:/Users/Tshala Benjamin/AppData/Local/Programs/Python/Python39/ailine/Archives"
        archive_image_path = os.path.join(archive_dir, f"{name}_{lastname}.png")
        archive_perine_image_path = os.path.join(archive_dir, f"{name}_{lastname}_perine.jpg")

        # Déplacer les images vers le dossier d'archives
        if os.path.exists(image_path):
            shutil.move(image_path, archive_image_path)
        if os.path.exists(perine_image_path):
            shutil.move(perine_image_path, archive_perine_image_path)

        # Supprimer le patient de la liste de patients
        self.patient_list.remove(selected_patient)

        # Sauvegarder la liste de patients mise à jour
        self.save_patients()

        
        # Mettre à jour la Listbox avec les patients restants
        self.update_patient_listbox()



        # Ajouter le patient à une liste d'archives
        # Ajouter le patient à une liste d'archives
        if os.path.exists('archive.json'):
            with open('archive.json', 'r+') as f:
                try:
                    archive = json.load(f)
                except json.JSONDecodeError:
                    archive = []
                archive.append(selected_patient)
                f.seek(0)
                json.dump(archive, f)
                f.truncate()
        else:
            with open('archive.json', 'w') as f:
                json.dump([selected_patient], f)

    def view_archives(self):

        # initialize the archived_patients attribute
        self.archived_patients = []


        # Créer une nouvelle fenêtre toplevel
        archive_window = tk.Toplevel(self.root)
        archive_window.title("Patients archivés")

        # Définir l'icône de la fenêtre
        archive_window.iconbitmap('C:/Users/Tshala Benjamin/Downloads/papio.ico')

        # Définir l'arrière-plan de la fenêtre en bleu clair
        archive_window.configure(bg='light blue')

        # Bloquer la modification de la taille de la fenêtre
        archive_window.resizable(False, False)

        # Créer une Listbox pour afficher les patients archivés
        self.archive_listbox = tk.Listbox(archive_window, height=14, width=70, bg='white', fg='black')
        self.archive_listbox.grid(row=0, column=0, sticky='n')

        # Ajouter une scrollbar
        scrollbar = tk.Scrollbar(archive_window, command=self.archive_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Lier la barre de défilement à la Listbox
        self.archive_listbox['yscrollcommand'] = scrollbar.set

        # Charger les patients archivés à partir du fichier JSON
        if os.path.exists('archive.json'):
            with open('archive.json', 'r') as f:
                self.archived_patients = json.load(f)  # chargez les données dans self.archived_patients

            # Ajouter les patients archivés à la Listbox
            for patient in self.archived_patients:
                self.archive_listbox.insert(tk.END, patient['Nom'] + ' ' + patient['Prénom'])
        
        # Create a Menu
        self.context_menu = tk.Menu(archive_window, tearoff=0)
        self.context_menu.add_command(label="Restaurer le patient", command=self.restore_patient)  # Add your function
        self.context_menu.add_command(label="Supprimer définitivement", command=self.delete_permanently)  # Add your function

        # Bind right click
        def do_popup(event):
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

        self.archive_listbox.bind("<Button-3>", do_popup)


        # Bouton pour fermer la fenêtre
        button_close = tk.Button(archive_window, text="Fermer", command=archive_window.destroy, bg='skyblue')
        button_close.grid(row=1, column=0, columnspan=2, pady=10)


   
    def restore_patient(self):
        # Check if any item is selected
        if self.archive_listbox.curselection():
            # Récupérer l'indice de l'élément sélectionné
            selected_index = self.archive_listbox.curselection()[0]

            # Obtenir les informations du patient sélectionné
            selected_patient = self.archived_patients[selected_index]
            
            archive_dir = "C:/Users/Tshala Benjamin/AppData/Local/Programs/Python/Python39/ailine/Archives"

            # Spécifier le chemin des images archivées
            archive_image_path = os.path.join(archive_dir, f"{selected_patient['Nom']}_{selected_patient['Prénom']}.png")
            archive_perine_image_path = os.path.join(archive_dir, f"{selected_patient['Nom']}_{selected_patient['Prénom']}_perine.jpg")

            # Spécifier le chemin de destination (le "dossier original")
            original_dir = "C:/Users/Tshala Benjamin/AppData/Local/Programs/Python/Python39/ailine/image_corps"
            original_image_path = os.path.join(original_dir, f"{selected_patient['Nom']}_{selected_patient['Prénom']}.png")
            original_perine_image_path = os.path.join(original_dir, f"{selected_patient['Nom']}_{selected_patient['Prénom']}_perine.jpg")

            # Déplacer les images vers le dossier original
            if os.path.exists(archive_image_path):
                shutil.move(archive_image_path, original_image_path)
            if os.path.exists(archive_perine_image_path):
                shutil.move(archive_perine_image_path, original_perine_image_path)

            # Ajouter le patient à la liste de patients
            self.patient_list.append(selected_patient)

            # Sauvegarder la liste de patients mise à jour
            self.save_patients()

            # Mettre à jour la Listbox avec les patients
            self.update_patient_listbox()

            # Supprimer le patient de la liste d'archives
            self.archived_patients.remove(selected_patient)

            # Sauvegarder la liste d'archives mise à jour
            with open('archive.json', 'w') as f:
                json.dump(self.archived_patients, f)

                # Mettre à jour la Listbox d'archives
                self.update_archive_listbox()
        else:
            messagebox.showinfo("Restore Patient", "No patient selected.")

    def delete_permanently(self):
        # Check if any item is selected
        if self.archive_listbox.curselection():
            # Récupérer l'indice de l'élément sélectionné
            selected_index = self.archive_listbox.curselection()[0]

            # Obtenir les informations du patient sélectionné
            selected_patient = self.archived_patients[selected_index]

            archive_dir = "C:/Users/Tshala Benjamin/AppData/Local/Programs/Python/Python39/ailine/Archives"
            
            # Spécifier le chemin des images archivées
            archive_image_path = os.path.join(archive_dir, f"{selected_patient['Nom']}_{selected_patient['Prénom']}.png")
            archive_perine_image_path = os.path.join(archive_dir, f"{selected_patient['Nom']}_{selected_patient['Prénom']}_perine.jpg")

            # Supprimer les images du dossier d'archives
            if os.path.exists(archive_image_path):
                os.remove(archive_image_path)
            if os.path.exists(archive_perine_image_path):
                os.remove(archive_perine_image_path)

            # Supprimer le patient de la liste d'archives
            self.archived_patients.remove(selected_patient)

            # Sauvegarder la liste d'archives mise à jour
            with open('archive.json', 'w') as f:
                json.dump(self.archived_patients, f)
            # Mettre à jour la Listbox d'archives
            self.update_archive_listbox()


            # Mettre à jour la Listbox d'archives
            self.update_archive_listbox()
        else:
            messagebox.showinfo("Delete Permanently", "No patient selected.")

            

    def update_archive_listbox(self):
        # Clear the ListBox
        self.archive_listbox.delete(0, tk.END)

        # Add items from self.archived_patients to the ListBox
        for patient in self.archived_patients:
            self.archive_listbox.insert(tk.END, patient['Nom'] + ' ' + patient['Prénom'])


if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap('C:/Users/Tshala Benjamin/Downloads/papio.ico')
    app = MyApp(root)
    root.mainloop()
