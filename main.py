
from file_manager import FileManager
from ai_engine import AIEngine
from interactive_selector import InteractiveSelector # Import new module

def main():
    fm = FileManager()
    # We don't need a target class for manual mode, so we just init the engine
    ai = AIEngine(target_label="manual") 
    selector = InteractiveSelector()

    print("--- CleanSweep AI: Interactive Mode ---")

    for img_path, filename in fm.get_input_images():
        print(f"\nOpening: {filename}")
        
        # 1. Open GUI for user to mark object
        user_mask = selector.select_object(img_path)

        # 2. If user provided a mask (didn't press 'q')
        if user_mask is not None:
            
            # 3. AI Removal
            cleaned_image = ai.remove_with_mask(img_path, user_mask)
            
            # 4. Save & Log
            saved_path = fm.save_image(cleaned_image, filename)
            fm.log_operation(filename, "User_Selected_Area", 1.0, success=True)
            
            print(f"✔ Object Removed! Saved to: {saved_path}")
        else:
            print("✘ Skipped.")

if __name__ == "__main__":
    main()