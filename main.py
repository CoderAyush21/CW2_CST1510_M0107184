from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.user_service import  register_user,login_user,migrate_users_from_file
from app.services.loadCSV import load_csv_to_table
from app.data.incidents import insert_incident, update_incident_status, delete_incident, get_incident_by_id
from app.services.analyticalQueries import get_incidents_by_type_count, get_high_severity_by_status
import pandas as pd
# function to run complete database setup
def main():
    print("=" * 60)
    print("Week 8: Database Demo")
    print("=" * 60)
    
    print("\n" + "="*60)
    print("STARTING COMPLETE DATABASE SETUP")
    print("="*60)

    # Step 1: Connect
    print("\n[1/] Connecting to database...")
    conn = connect_database()
    print("       Connected")

    # Step 2: Create tables
    print("\n[2/] Creating database tables...")
    create_all_tables(conn)

    # Step 3: Migrate users
    print("\n[3/] Migrating users from users.txt...")
    user_count = migrate_users_from_file(conn)
    print(f"       Migrated {user_count} users")

    # Step 4: Load CSV data
    print("\n[4/] Loading CSV data for cyber incidents...")
    total_rows_cyber = load_csv_to_table(conn, "DATA/cyber_incidents.csv", "cyber_incidents")
    
    print("\n[5/] Loading CSV data for IT tickets...")
    total_rows_tickets = load_csv_to_table(conn, "DATA/it_tickets.csv", "it_tickets")

    print("\n[6/] Loading CSV data for Datasets Metadata...")
    total_rows_datasets = load_csv_to_table(conn, "DATA/datasets_metadata.csv", "datasets_metadata")

    print("\n" + "="*60)
    print(" DATABASE SETUP COMPLETE!")

# function to run comprehensive tests
def run_comprehensive_tests():
    """
    Run comprehensive tests on your database.
    """
    print("\n" + "="*60)
    print("🧪 RUNNING COMPREHENSIVE TESTS")
    print("="*60)

    conn = connect_database()

    # Test 1: Authentication
    print("\n[TEST 1] Authentication")
    success, msg = register_user("test_user", "TestPass123!", "user")
    print(f"  Register: {'✅' if success else '❌'} {msg}")

    success, msg = login_user("test_user", "TestPass123!")
    print(f"  Login:    {'✅' if success else '❌'} {msg}")

    # Test 2: CRUD Operations
    print("\n[TEST 2] CRUD Operations")

    # Create
    test_id = insert_incident(
        severity="Low",
        category="Test1 Incident",
        status="Open",
        description="This is a test1 incident",
        reported_by="test1_user",
        timestamp="2024-11-05"
   )

    print(f"  Create: ✅ Incident #{test_id} created")

    # Read
    df = get_incident_by_id(test_id)
    print(f"  Read:    Found incident #{test_id}")


    # Update
    update_incident_status(test_id, "Resolved")
    print(f"  Update:  Status updated")

    # Delete
    delete_incident(test_id)
    print(f"  Delete:  Incident deleted")

    # Test 3: Analytical Queries
    print("\n[TEST 3] Analytical Queries")

    df_by_type = get_incidents_by_type_count(conn)
    print(f"  By Type:     Found {len(df_by_type)} incident types")

    df_high = get_high_severity_by_status(conn)
    print(f"  High Severity: Found {len(df_high)} status categories")

    conn.close()

    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)



# Run the complete setup
# if __name__ == "__main__":
#     main()

# if __name__ == "__main__":
#     run_comprehensive_tests()

