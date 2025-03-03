from app.rfid.service import MFRC522Service
import sys

def main():
    service = MFRC522Service()
    
    try:
        while True:
            print("\nRFID Card Management")
            print("1. Write new card")
            print("2. Start card reader")
            print("3. Exit")
            
            choice = input("Select option: ")
            
            if choice == "1":
                print("\nWriting new card...")
                print("Note: Special characters will be converted to ASCII equivalents")
                name = input("Enter name: ")
                is_admin = input("Is admin? (y/n): ").lower() == 'y'
                
                print("\nPlace card on reader to write...")
                try:
                    card_id = service.write_card(name, is_admin)
                    print(f"\nSuccess! Card written with ID: {card_id}")
                    print(f"Name stored as: {service.normalize_text(name)}")
                except ValueError as ve:
                    print(f"\nError: {str(ve)}")
                except Exception as e:
                    print(f"\nError writing card: {str(e)}")
                
            elif choice == "2":
                print("\nStarting card reader...")
                print("Place card on reader to read (Ctrl+C to stop)")
                try:
                    while True:
                        service.read_card()
                except KeyboardInterrupt:
                    print("\nStopping card reader...")
                    
            elif choice == "3":
                print("\nExiting...")
                break
            else:
                print("\nInvalid option, please try again")
                
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        service.cleanup()

if __name__ == "__main__":
    main() 