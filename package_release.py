import os
import json
import shutil
import zipfile

def package():
    v_name = "ルベカウントタイマー_ver1.6"
    if os.path.exists(v_name):
        shutil.rmtree(v_name)
    os.makedirs(v_name)

    # 1. Copy EXE
    shutil.copy("dist/ルベカウントタイマー.exe", v_name)

    # 1b. Copy Icon
    if os.path.exists("icon.ico"):
        shutil.copy("icon.ico", v_name)

    # 2. Copy README.txt
    shutil.copy("README.txt", v_name)

    # 3. Copy sounds
    shutil.copytree("sounds", os.path.join(v_name, "sounds"))

    # 4. Prepare settings.json (Ja mode)
    with open("settings.json", "r", encoding="utf-8") as f:
        settings = json.load(f)
    
    settings["language"] = "ja"
    
    with open(os.path.join(v_name, "settings.json"), "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

    # 5. Create ZIP
    zip_name = f"{v_name}.zip"
    if os.path.exists(zip_name):
        os.remove(zip_name)
        
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(v_name):
            for file in files:
                filepath = os.path.join(root, file)
                z.write(filepath, os.path.relpath(filepath, "."))

    print(f"Successfully created {zip_name}")

if __name__ == "__main__":
    package()
