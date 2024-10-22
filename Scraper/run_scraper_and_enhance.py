import os
import subprocess

def run_script(script_name):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    try:
        subprocess.run(["python", script_path], check=True)
        print(f"{script_name} completed successfully.")
    except subprocess.CalledProcessError:
        print(f"An error occurred while running {script_name}.")

def main():
    print("Welcome to the Scraper and Model Reference Enhancer!")

    # Ask about running scraper.py
    run_scraper = input("Do you want to run scraper.py? (yes/no): ").lower().strip()
    if run_scraper == 'yes':
        run_script("scraper.py")
    else:
        print("Skipping scraper.py")

    # Ask about running enhance_model_reference.py
    run_enhance = input("Do you want to run enhance_model_reference.py? (yes/no): ").lower().strip()
    if run_enhance == 'yes':
        run_script("enhance_model_reference.py")
    else:
        print("Skipping enhance_model_reference.py")

    print("All operations completed.")

if __name__ == "__main__":
    main()
