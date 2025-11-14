# Python Project for CST1510

 # Week 7: Secure Authentication System
 Student Name: Ayush Mani Tripathi
 Student ID: M01071841
 Course: CST1510 -CW2 -  Multi-Domain Intelligence Platform 
## Project Description
 A command-line authentication system implementing secure password hashing
 This system allows users to register accounts and log in with proper pass
 ## Features
 -Secure password hashing using bcrypt with automatic salt generation
 -User registration with duplicate username prevention
 -User login with password verification
 -Input validation for usernames and passwords
 -File-based user data persistence
 ## Technical Implementation
 -Hashing Algorithm: bcrypt with automatic salting
 -Data Storage: Plain text file (`users.txt`) with comma-separated values
 -Password Security: One-way hashing, no plaintext storage
 -Validation: Username (More than 3 characters long and must be of valid type), Password (More than 8 characters long)
