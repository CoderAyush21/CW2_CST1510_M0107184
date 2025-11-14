import bcrypt
import os


USER_DATA_FILE = "users.txt"

 # function to produce hashed password
def hash_password(plain_text_password) :
    password_bytes= plain_text_password.encode("utf-8")
    salt= bcrypt.gensalt()
    hashed_password= bcrypt.hashpw(password_bytes, salt)
    hashed_password_str= hashed_password.decode("utf-8")
    return hashed_password_str

 # function to verify if the hashed password is correct 
def verify_password(plain_text_password, hashed_password) :
    password_bytes= plain_text_password.encode("utf-8")
    hashed_password_bytes= hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)

'''
Test data for the program
.................................................
test_password = "SecurePassword123"

hashed = hash_password(test_password)
print(f"Original password: {test_password}")
print(f"Hashed password: {hashed}")
print(f"Hash length: {len(hashed)} characters")

is_valid = verify_password(test_password, hashed)
print(f"\nVerification with correct password: {is_valid}")
is_invalid = verify_password("WrongPassword", hashed)
print(f"Verification with incorrect password: {is_invalid}")
'''
# function to check if file exists or if username already in file
def user_exists(userName):
   if not os.path.exists(USER_DATA_FILE):
       return "Path does not exist"
   with open(USER_DATA_FILE,"r") as f :
       for line in f.readlines() :
           stored_username, _ , _ = line.strip().split(",", 2)
           if stored_username == userName:
               return True
       return False    
       
 # function for user registration
def register_user(user_name, password,role) :
    if user_exists(user_name) == True:
        print(f"Username {user_name} already exists ! ")
        return 
    
    hashed_password = hash_password(password) 
    with open(USER_DATA_FILE, "a") as f: 
        f.write(f"{user_name},{hashed_password},{role}\n") 
    print(f"User '{user_name}' registered.")
# function for failed to login
 
# function to login existing user
def login_user(userName1, password1):
  if not os.path.exists(USER_DATA_FILE):
   print("No users registered yet!")
   return False

  with open(USER_DATA_FILE, "r") as f:
    for line in f:
     stored_username, stored_hash, role = line.strip().split(",", 2)
     if stored_username == userName1:
        if verify_password(password1, stored_hash):
         print(f"Login successful for Role {role}!")
         return True
        else:
         print("Incorrect password.")
         return False
     print("Username not found!")
     return False

def validate_userName(user_name2) -> tuple[bool,str]: 
    if len(user_name2) < 3:
        return False, "Username must be at least 3 characters long."
    if not user_name2.isidentifier():  # checks if it's a valid name (letters, digits, underscores, no spaces)
        return False , "UserName does not contain valid characters"
    return True , "UserName is valid !"
  
def validate_password(password) -> tuple[bool,str] :
        
       if " " in password:
        return False, "Password cannot contain spaces."
       if len(password) <= 8:
        return False, "Password must be more than 8 characters long."
       if not any(c.isupper() for c in password):
        return False, "Must contain at least one uppercase letter."
       if not any(c.islower() for c in password):
        return False, "Must contain at least one lowercase letter."
       if not any(c.isdigit() for c in password):
        return False, "Must contain at least one digit."
       if not any(c in "@#$%^&*!?" for c in password):
        return False, "Must contain at least one special character (@, #, $, etc.)."
       return True, "Strong password."
        
def display_menu():
    """Displays the main menu options."""
    print("\n" + "="*50)
    print("  MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print("  Secure Authentication System")
    print("="*50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)
def main():
    """Main program loop."""
    print("\nWelcome to the Week 7 Authentication System!")
    
    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()
        
        if choice == '1':
            # Registration flow
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()
            
            # Validate username
            is_valid, error_msg = validate_userName(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue
            
            password = input("Enter a password: ").strip()
             # Validate password
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue
            
            # Confirm password
            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue
            # Ask user to enter a role
            role = input("Enter a role [user, analyst, admin] : ").strip().lower()
            if role not in ["user", "analyst", "admin"] :
               print("Invalid input ! Default role set to 'user' ")
               role= "user"
            # Register the user
            register_user(username, password,role)
        
        elif choice == '2':
            # Login flow
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()
            
            # Attempt login
            if login_user(username, password):
                print("\nYou are now logged in.")
                
                # Optional: Ask if they want to logout or exit
                input("\nPress Enter to return to main menu...")
        
        elif choice == '3':
            # Exit
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break
        
        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()