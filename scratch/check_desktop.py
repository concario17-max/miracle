import os

desktop_path = "c:/Users/roadsea/Desktop"
if os.path.exists(desktop_path):
    print("Desktop contents:")
    for f in os.listdir(desktop_path):
        print(f"  {f}")
else:
    print("Desktop path not found")
