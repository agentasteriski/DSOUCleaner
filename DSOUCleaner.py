import os, yaml
import tkinter as tk
import customtkinter as ctk
from PIL import ImageTk
from CTkMessagebox import CTkMessagebox

#CTk setup
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("assets/ds_gui.json")
ctk.FontManager.load_font("assets/RedHatDisplay-Regular.ttf")

#root window setup
root = ctk.CTk()
root.title("DS OU Cleaner")
root.resizable(False, False)
root.iconpath = ImageTk.PhotoImage(file=os.path.join("assets","hard-drive.png"))
root.wm_iconbitmap()
root.iconphoto(False, root.iconpath)

#font and locale stuff
font_en = 'Red Hat Display'
font = ctk.CTkFont(family=font_en) #add font localization later

#placeholders
spk_rows = []
spk_info = {}

# get singer folder, generate boxes, gather info
def get_model():
    global model_folder
    model_folder = ctk.filedialog.askdirectory(title="Select DiffSinger for OU")
    print(model_folder)
    global chryaml_loc
    for dirpath, dirnames, filenames in os.walk(model_folder):
        if 'character.yaml' in filenames:
            chryaml_loc = os.path.join(dirpath, 'character.yaml')
    with open(chryaml_loc, "r", encoding="UTF-8") as load_chr_yaml:
        chryaml = yaml.safe_load(load_chr_yaml)
    for widget in frame1.winfo_children():
        widget.destroy()

    for index, subbank in enumerate(chryaml['subbanks']):
        color = subbank['color']
        suffix = subbank['suffix']
        embedname = os.path.splitext(os.path.basename(suffix))[0]
        spk_rows.append(ctk.CTkFrame(master=frame1, width=340))
        spk_rows[index].grid(row=index, sticky="EW", padx=5, pady=3)
        checkbox = ctk.CTkCheckBox(master=spk_rows[index], text="")
        checkbox.grid(row=0, column=0, padx=(5,0), pady=5)
        spk_name_box = ctk.CTkEntry(master=spk_rows[index], width=150, font=font)
        spk_name_box.insert(0, color)
        spk_name_box.grid(column=1, row=0, padx=(0,5), pady=5)
        spk_info[index] = {'checkbox': checkbox, 'newcolor': spk_name_box, 'oldcolor': color, 'embedname': embedname, 'suffix': suffix}


def yeet():
    deletewarning = CTkMessagebox(master=root, title="Warning", message="Selected speakers' files will be deleted permanently! It is recommended to back up your files first.", icon="warning", font=font, option_2="Cancel", option_1="Continue")
    response = deletewarning.get()
    if response == "Continue":
        #placeholders
        removespk = []
        changed_colors = []
        #establish what's being modified
        for index, info in spk_info.items():
                checkbox_state = info['checkbox'].get()
                if checkbox_state:
                    removespk.append(info['embedname'])
                newcolor = info['newcolor'].get()
                oldcolor = info['oldcolor']
                if newcolor != oldcolor:
                    changed_colors.append({'old': oldcolor, 'new': newcolor})
        #look for files to clean
        for dirpath, dirnames, filenames in os.walk(model_folder):
            #delete extra speakers from dsconfigs
            if 'dsconfig.yaml' in filenames:
                dsconfig_path = os.path.join(dirpath, 'dsconfig.yaml')
                with open(dsconfig_path, "r", encoding="UTF-8") as load_dsconfig:
                    dsconfig = yaml.safe_load(load_dsconfig)
                new_speakers = []
                for speaker in dsconfig['speakers']:
                    embedname = os.path.splitext(os.path.basename(speaker))[0]
                    if embedname not in removespk:
                        new_speakers.append(speaker)
                dsconfig['speakers'] = new_speakers
                with open(dsconfig_path, "w", encoding="UTF-8") as save_dsconfig:
                    yaml.safe_dump(dsconfig, save_dsconfig)
                print(f"Modified dsconfig.yaml at {dsconfig_path}")
            #delete unwanted embed files
            for filename in filenames:
                if filename.endswith(".emb"):
                    filepath = os.path.join(dirpath, filename)
                    embedname = os.path.splitext(os.path.basename(filename))[0]
                    if embedname in removespk:
                        os.remove(filepath)
        print('deleted embeds!')
        with open(chryaml_loc, "r", encoding="UTF-8") as load_chryaml:
            chryaml = yaml.safe_load(load_chryaml)
        new_subbanks = []
        for subbank in chryaml['subbanks']:
            embedname = os.path.splitext(os.path.basename(subbank['suffix']))[0]
            if embedname not in removespk:
                # update color if changed
                new_color = next((c['new'] for c in changed_colors if c['old'] == subbank['color']), subbank['color'])
                new_subbanks.append({
                    'color': new_color,
                    'suffix': subbank['suffix']
                })
        chryaml['subbanks'] = new_subbanks
        with open(chryaml_loc, "w", encoding="UTF-8") as save_chryaml:
            yaml.safe_dump(chryaml, save_chryaml)
        print('done!')
        yay = CTkMessagebox(master=root, message="Done!", icon="check", option_1="OK", title="Cleaning complete", font=font)
    else:
        print("Changed your mind?")
    

get_model = ctk.CTkButton(master=root, text="Select DiffSinger for OU", font=font, command=get_model)
get_model.grid(row=0, column=0, pady=10)

instructions = ctk.CTkLabel(master=root, text="Check the boxes to \n remove unwanted speakers", font=font)
instructions.grid(row=1, column=0, pady=(0,10))

frame1 = ctk.CTkScrollableFrame(master=root, width=275, height=400)
frame1.grid(row=2, column=0, padx=10)

yeet_button = ctk.CTkButton(master=root, text="Clean speakers", font=font, command=yeet)
yeet_button.grid(row=3, column=0, pady=10)




root.mainloop()
