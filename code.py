import os
import sys
import time
import json
import random
import pandas as pd
from datetime import datetime
from colorama import init, Fore, Style
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re

# Initialize colorama
init(autoreset=True)

class WhatsAppContactSaver:
    def __init__(self, data_file='numbers.csv', delay=5):
        """
        Initialize WhatsApp Contact Saver
        
        Args:
            data_file: File containing phone numbers
            delay: Delay between operations (in seconds)
        """
        self.data_file = data_file
        self.delay = delay
        self.driver = None
        self.wait = None
        self.contacts_saved = 0
        self.contacts_failed = 0
        self.log_file = 'whatsapp_contact_log.json'
        
        # Load existing logs
        self.load_log()
        
        print(Fore.CYAN + Style.BRIGHT + """
╔═══════════════════════════════════════════════════╗
║    WhatsApp Auto Contact Saver Bot               ║
║    Version 1.0 - By Python Developer             ║
║    Save contacts as A1-A100, B1-B100, etc.       ║
╚═══════════════════════════════════════════════════╝
        """)
    
    def load_log(self):
        """Load saved contacts log"""
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                self.saved_log = json.load(f)
        else:
            self.saved_log = {
                'saved_contacts': [],
                'failed_contacts': [],
                'last_run': None,
                'total_saved': 0
            }
    
    def save_log(self):
        """Save contacts log"""
        self.saved_log['last_run'] = datetime.now().isoformat()
        self.saved_log['total_saved'] = self.contacts_saved
        
        with open(self.log_file, 'w') as f:
            json.dump(self.saved_log, f, indent=2)
    
    def setup_driver(self):
        """Setup Chrome driver with WhatsApp Web options"""
        print(Fore.YELLOW + "[SETUP] Setting up Chrome driver...")
        
        chrome_options = Options()
        
        # Chrome options for WhatsApp Web
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Uncomment for headless mode (no GUI)
        # chrome_options.add_argument('--headless')
        
        # Disable notifications
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.media_stream_camera": 2,
            "profile.default_content_setting_values.media_stream_mic": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        })
        
        try:
            # Try to use webdriver-manager first
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except:
            # Fallback to system chromedriver
            self.driver = webdriver.Chrome(options=chrome_options)
        
        self.wait = WebDriverWait(self.driver, 30)
        print(Fore.GREEN + "[SUCCESS] Chrome driver setup complete!")
    
    def login_whatsapp(self):
        """Login to WhatsApp Web"""
        print(Fore.YELLOW + "[LOGIN] Opening WhatsApp Web...")
        
        self.driver.get('https://web.whatsapp.com')
        
        print(Fore.YELLOW + "[INFO] Please scan QR code within 60 seconds...")
        print(Fore.CYAN + "[TIP] You can scan QR code from your phone: WhatsApp → Menu → Linked Devices")
        
        # Wait for login
        try:
            # Wait for main WhatsApp interface
            search_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            time.sleep(5)
            print(Fore.GREEN + "[SUCCESS] Successfully logged in to WhatsApp!")
            return True
        except Exception as e:
            print(Fore.RED + f"[ERROR] Login failed: {str(e)}")
            return False
    
    def validate_phone_number(self, number):
        """Validate and format phone number"""
        # Remove non-digit characters
        clean_number = re.sub(r'\D', '', str(number))
        
        # Check if number has minimum length
        if len(clean_number) < 8:
            return None
        
        # For Indonesian numbers
        if clean_number.startswith('0'):
            clean_number = '62' + clean_number[1:]
        elif clean_number.startswith('8'):
            clean_number = '62' + clean_number
        elif clean_number.startswith('+'):
            clean_number = clean_number[1:]
        
        # Final check
        if not clean_number.startswith('62'):
            return None
        
        return clean_number
    
    def generate_contact_name(self, index):
        """Generate contact name A1-A100, B1-B100, etc."""
        if index <= 100:
            return f"A{index}"
        elif index <= 200:
            return f"B{index-100}"
        elif index <= 300:
            return f"C{index-200}"
        elif index <= 400:
            return f"D{index-300}"
        elif index <= 500:
            return f"E{index-400}"
        elif index <= 600:
            return f"F{index-500}"
        elif index <= 700:
            return f"G{index-600}"
        elif index <= 800:
            return f"H{index-700}"
        elif index <= 900:
            return f"I{index-800}"
        else:
            return f"J{index-900}"
    
    def save_single_contact(self, phone_number, contact_name):
        """Save a single contact to WhatsApp"""
        try:
            print(Fore.BLUE + f"[PROCESS] Saving {contact_name} ({phone_number})...")
            
            # Click on new chat button
            new_chat_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//div[@title="New chat"]'))
            )
            new_chat_btn.click()
            time.sleep(2)
            
            # Enter phone number in search box
            search_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            
            # Clear and enter number
            search_input.click()
            time.sleep(1)
            search_input.send_keys(Keys.CONTROL + "a")
            search_input.send_keys(Keys.DELETE)
            time.sleep(1)
            search_input.send_keys(phone_number)
            time.sleep(3)
            
            # Check if "Message" button appears (contact exists)
            try:
                message_btn = self.driver.find_element(By.XPATH, '//span[@data-icon="message"]')
                print(Fore.YELLOW + f"[INFO] {phone_number} already exists, adding name...")
            except:
                # If contact doesn't exist, create new
                print(Fore.YELLOW + f"[INFO] Creating new contact for {phone_number}...")
            
            # Click on three dots menu
            try:
                menu_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="menu"]'))
                )
                menu_btn.click()
                time.sleep(2)
                
                # Click on "Save contact" option
                save_option = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Save contact"]'))
                )
                save_option.click()
                time.sleep(2)
                
                # Fill contact name
                name_input = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                )
                name_input.click()
                time.sleep(1)
                name_input.send_keys(Keys.CONTROL + "a")
                name_input.send_keys(Keys.DELETE)
                time.sleep(1)
                name_input.send_keys(contact_name)
                time.sleep(2)
                
                # Click save button
                save_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Save"]'))
                )
                save_btn.click()
                time.sleep(3)
                
                # Verify save success
                try:
                    self.driver.find_element(By.XPATH, '//div[contains(text(), "saved")]')
                    print(Fore.GREEN + f"[SUCCESS] Contact {contact_name} saved successfully!")
                    return True
                except:
                    # Sometimes no confirmation appears
                    print(Fore.GREEN + f"[SUCCESS] Contact {contact_name} likely saved!")
                    return True
                    
            except Exception as e:
                print(Fore.RED + f"[ERROR] Failed to save contact: {str(e)}")
                return False
            
        except Exception as e:
            print(Fore.RED + f"[ERROR] Contact save process failed: {str(e)}")
            return False
    
    def load_numbers_from_file(self):
        """Load phone numbers from file"""
        print(Fore.YELLOW + f"[LOAD] Loading numbers from {self.data_file}...")
        
        # Check if file exists
        if not os.path.exists(self.data_file):
            print(Fore.RED + f"[ERROR] File {self.data_file} not found!")
            print(Fore.YELLOW + "[INFO] Creating sample numbers file...")
            self.create_sample_file()
            return self.load_numbers_from_file()
        
        try:
            # Try different file formats
            if self.data_file.endswith('.csv'):
                df = pd.read_csv(self.data_file)
            elif self.data_file.endswith('.xlsx'):
                df = pd.read_excel(self.data_file)
            elif self.data_file.endswith('.txt'):
                with open(self.data_file, 'r') as f:
                    numbers = f.read().splitlines()
                df = pd.DataFrame(numbers, columns=['number'])
            else:
                print(Fore.RED + "[ERROR] Unsupported file format!")
                return []
            
            # Extract numbers from first column
            if df.empty:
                print(Fore.RED + "[ERROR] File is empty!")
                return []
            
            # Get column name
            col_name = df.columns[0]
            numbers = df[col_name].astype(str).tolist()
            
            print(Fore.GREEN + f"[SUCCESS] Loaded {len(numbers)} numbers from file")
            return numbers
            
        except Exception as e:
            print(Fore.RED + f"[ERROR] Failed to load numbers: {str(e)}")
            return []
    
    def create_sample_file(self):
        """Create sample numbers file"""
        sample_numbers = [
            "081234567890",
            "081298765432",
            "085712345678",
            "087812345678",
            "089512345678"
        ]
        
        df = pd.DataFrame(sample_numbers, columns=['phone_number'])
        df.to_csv(self.data_file, index=False)
        print(Fore.YELLOW + f"[INFO] Created sample file: {self.data_file}")
    
    def process_numbers(self, numbers_list):
        """Process list of numbers and save contacts"""
        print(Fore.CYAN + f"\n[START] Processing {len(numbers_list)} numbers...")
        
        for idx, number in enumerate(numbers_list, 1):
            # Validate number
            valid_number = self.validate_phone_number(number)
            
            if not valid_number:
                print(Fore.RED + f"[SKIP] Invalid number format: {number}")
                self.contacts_failed += 1
                continue
            
            # Check if already saved
            if valid_number in self.saved_log['saved_contacts']:
                print(Fore.YELLOW + f"[SKIP] {valid_number} already saved")
                continue
            
            # Generate contact name
            contact_name = self.generate_contact_name(idx)
            
            # Save contact
            success = self.save_single_contact(valid_number, contact_name)
            
            if success:
                self.contacts_saved += 1
                self.saved_log['saved_contacts'].append(valid_number)
                
                # Save log periodically
                if self.contacts_saved % 10 == 0:
                    self.save_log()
            else:
                self.contacts_failed += 1
                self.saved_log['failed_contacts'].append(valid_number)
            
            # Random delay between operations
            delay_time = random.uniform(self.delay * 0.5, self.delay * 1.5)
            print(Fore.MAGENTA + f"[WAIT] Waiting {delay_time:.1f} seconds...")
            time.sleep(delay_time)
            
            # Show progress
            progress = (idx / len(numbers_list)) * 100
            print(Fore.CYAN + f"[PROGRESS] {idx}/{len(numbers_list)} ({progress:.1f}%) - Saved: {self.contacts_saved}, Failed: {self.contacts_failed}")
    
    def run(self):
        """Main run method"""
        try:
            # Setup driver
            self.setup_driver()
            
            # Login to WhatsApp
            if not self.login_whatsapp():
                print(Fore.RED + "[ERROR] Login failed. Exiting...")
                return
            
            # Load numbers
            numbers = self.load_numbers_from_file()
            
            if not numbers:
                print(Fore.RED + "[ERROR] No numbers to process!")
                return
            
            # Process numbers
            self.process_numbers(numbers)
            
            # Final report
            print(Fore.GREEN + "\n" + "="*50)
            print(Fore.GREEN + Style.BRIGHT + "PROCESS COMPLETED!")
            print(Fore.GREEN + f"Total Contacts Saved: {self.contacts_saved}")
            print(Fore.RED + f"Total Contacts Failed: {self.contacts_failed}")
            print(Fore.CYAN + f"Log saved to: {self.log_file}")
            print(Fore.GREEN + "="*50)
            
            # Save final log
            self.save_log()
            
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n[INFO] Process interrupted by user")
            self.save_log()
        except Exception as e:
            print(Fore.RED + f"\n[ERROR] Unexpected error: {str(e)}")
        finally:
            if self.driver:
                print(Fore.YELLOW + "[INFO] Closing browser...")
                self.driver.quit()

def main():
    """Main function"""
    print(Fore.CYAN + Style.BRIGHT + "WhatsApp Auto Contact Saver")
    print(Fore.YELLOW + "="*50)
    
    # Get user input
    data_file = input(Fore.WHITE + "Enter numbers file (CSV/TXT/XLSX) [default: numbers.csv]: ").strip()
    if not data_file:
        data_file = 'numbers.csv'
    
    delay_input = input(Fore.WHITE + "Enter delay between saves in seconds [default: 5]: ").strip()
    try:
        delay = int(delay_input) if delay_input else 5
    except:
        delay = 5
    
    # Create and run bot
    bot = WhatsAppContactSaver(data_file=data_file, delay=delay)
    bot.run()
    
    print(Fore.GREEN + "\n[INFO] Program completed successfully!")
    print(Fore.YELLOW + "[TIP] Check 'whatsapp_contact_log.json' for saved contacts")

if __name__ == "__main__":
    main()
