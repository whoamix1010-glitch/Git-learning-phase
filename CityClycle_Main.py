# ============================================================================
# CITYCYCLE URBAN BIKE SHARING MANAGEMENT SYSTEM
# Python-based Text File Management System (No OOP, No External Libraries)
# ============================================================================
# This system manages bikes, stations, users, rides, and maintenance records
# for a city-wide bike-sharing program using text file storage.
# ============================================================================

import datetime
import random
import os

# ============================================================================
# CONSTANTS - Defined as per assignment requirements
# ============================================================================

# Pricing Constants (in USD)
RENTAL_RATE_PER_MINUTE = 0.10
LATE_FEE_PER_MINUTE = 0.05
STANDARD_RENTAL_MINUTES = 60

# File Names
FILE_BIKES = 'bikes.txt'
FILE_STATIONS = 'stations.txt'
FILE_USERS = 'users.txt'
FILE_RIDES = 'rides.txt'
FILE_MAINTENANCE = 'maintenance.txt'
FILE_LOGS = 'logs.txt'

# Bike Status Values
STATUS_AVAILABLE = 'available'
STATUS_RENTED = 'rented'
STATUS_MAINTENANCE = 'maintenance'
STATUS_REPAIR = 'repair'

# Ride Status Values
RIDE_ACTIVE = 'active'
RIDE_COMPLETED = 'completed'
RIDE_CANCELLED = 'cancelled'
RIDE_EXTENDED = 'extended'

# Maintenance Types
MAINT_SERVICE = 'service'
MAINT_REPAIR = 'repair'
MAINT_INSPECTION = 'inspection'

# User Roles
ROLE_ADMIN = '1'
ROLE_RIDE_OFFICER = '2'
ROLE_USER = '3'
ROLE_MAINTENANCE = '4'
ROLE_STATION_MANAGER = '5'

# ============================================================================
# FILE OPERATIONS - Core utility functions for reading/writing data
# ============================================================================

def read_file(filename):
    """
    Read data from a text file and return as list of lists.
    Each line is split by pipe (|) delimiter.
    Returns empty list if file doesn't exist or is empty.
    
    Args:
        filename (str): Name of the file to read
        
    Returns:
        list: List of lists containing file data, or empty list if file not found
    """
    try:
        if not os.path.exists(filename):
            return []
        
        data = []
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    row = line.split('|')
                    data.append(row)
        return data
        
    except IOError as e:
        print(f"ERROR reading file {filename}: {e}")
        return []


def write_file(filename, data):
    """
    Write data to a text file in pipe-delimited format.
    Overwrites existing file content.
    
    Args:
        filename (str): Name of the file to write
        data (list): List of lists to write (each sublist is a row)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(filename, 'w') as f:
            for row in data:
                # Convert all values to strings and join with pipe delimiter
                line = '|'.join(str(item) for item in row)
                f.write(line + '\n')
        return True
        
    except IOError as e:
        print(f"ERROR writing to file {filename}: {e}")
        return False


def append_to_file(filename, data):
    """
    Append a row to a text file without overwriting existing content.
    
    Args:
        filename (str): Name of the file to append to
        data (list): List of values to append as a single row
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(filename, 'a') as f:
            line = '|'.join(str(item) for item in data)
            f.write(line + '\n')
        return True
        
    except IOError as e:
        print(f"ERROR appending to file {filename}: {e}")
        return False


def log_activity(activity_message):
    """
    Log system activities with timestamp for auditing purposes.
    All daily activities are recorded in logs.txt file.
    
    Args:
        activity_message (str): Description of the activity to log
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = [timestamp, activity_message]
    append_to_file(FILE_LOGS, log_entry)


# ============================================================================
# VALIDATION FUNCTIONS - Input validation and data consistency checks
# ============================================================================

def validate_email(email):
    """
    Validate email format - must contain @ and . symbols.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if email format appears valid
    """
    if not email or len(email) < 5:
        return False
    if '@' not in email or '.' not in email:
        return False
    return True


def validate_phone(phone):
    """
    Validate phone number - must contain only digits and be 7-15 characters.
    
    Args:
        phone (str): Phone number to validate
        
    Returns:
        bool: True if phone format appears valid
    """
    if not phone:
        return False
    digits_only = ''.join(c for c in phone if c.isdigit())
    return 7 <= len(digits_only) <= 15


def validate_user_id(user_id, users_list):
    """
    Validate that user ID exists in the system.
    
    Args:
        user_id (str): User ID to validate
        users_list (list): List of all users
        
    Returns:
        bool: True if user exists
    """
    for user in users_list:
        if user[0] == user_id:
            return True
    return False


def validate_bike_id(bike_id, bikes_list):
    """
    Validate that bike ID exists in the system.
    
    Args:
        bike_id (str): Bike ID to validate
        bikes_list (list): List of all bikes
        
    Returns:
        bool: True if bike exists
    """
    for bike in bikes_list:
        if bike[0] == bike_id:
            return True
    return False


def validate_station_id(station_id, stations_list):
    """
    Validate that station ID exists in the system.
    
    Args:
        station_id (str): Station ID to validate
        stations_list (list): List of all stations
        
    Returns:
        bool: True if station exists
    """
    for station in stations_list:
        if station[0] == station_id:
            return True
    return False


def get_next_numeric_id(prefix, existing_list, id_index=0):
    """
    Generate the next available numeric ID with given prefix (e.g., U001, B002).
    
    Args:
        prefix (str): Prefix for ID (e.g., 'U', 'B', 'R')
        existing_list (list): List of existing records
        id_index (int): Index of ID column in each record
        
    Returns:
        str: Next available ID with prefix
    """
    max_number = 0
    
    for record in existing_list:
        if record[id_index].startswith(prefix):
            try:
                # Extract numeric part after prefix
                num_part = record[id_index][len(prefix):]
                num = int(num_part)
                if num > max_number:
                    max_number = num
            except ValueError:
                # Skip if not a valid number
                pass
    
    next_number = max_number + 1
    # Format with leading zeros (e.g., U001, U002)
    return f"{prefix}{next_number:03d}"


def calculate_ride_cost(start_time_str, end_time_str):
    """
    Calculate rental cost based on ride duration.
    Implements unique feature: Late Return Fee / Time-Based Rental Calculation
    - Standard rate: 0.10 USD per minute for up to 60 minutes
    - Late fee: Additional 0.05 USD per minute after 60 minutes
    
    Args:
        start_time_str (str): Start time in format "YYYY-MM-DD HH:MM:SS"
        end_time_str (str): End time in format "YYYY-MM-DD HH:MM:SS"
        
    Returns:
        tuple: (total_cost, duration_minutes, is_late)
    """
    try:
        start_time = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
        
        # Calculate duration in minutes
        duration_seconds = (end_time - start_time).total_seconds()
        duration_minutes = int(duration_seconds / 60)
        
        # Calculate cost
        if duration_minutes <= STANDARD_RENTAL_MINUTES:
            total_cost = duration_minutes * RENTAL_RATE_PER_MINUTE
            is_late = False
        else:
            # Standard rental cost + late fees
            standard_cost = STANDARD_RENTAL_MINUTES * RENTAL_RATE_PER_MINUTE
            late_minutes = duration_minutes - STANDARD_RENTAL_MINUTES
            late_cost = late_minutes * LATE_FEE_PER_MINUTE
            total_cost = standard_cost + late_cost
            is_late = True
        
        return (total_cost, duration_minutes, is_late)
        
    except ValueError:
        print("ERROR: Invalid time format")
        return (0, 0, False)


# ============================================================================
# RIDE OFFICER FUNCTIONS - Register users, process checkouts/returns
# ============================================================================

def register_new_user():
    """
    Register a new user in the system.
    Collects user information and generates unique user ID.
    Validates all inputs before saving.
    """
    print("\n" + "="*60)
    print("REGISTER NEW USER")
    print("="*60)
    
    # Input collection with validation
    while True:
        name = input("Enter user full name: ").strip()
        if not name or len(name) < 2:
            print("ERROR: Name must be at least 2 characters. Try again.")
            continue
        break
    
    while True:
        email = input("Enter user email address: ").strip()
        if not validate_email(email):
            print("ERROR: Invalid email format. Must contain @ and . symbols. Try again.")
            continue
        break
    
    while True:
        phone = input("Enter user phone number: ").strip()
        if not validate_phone(phone):
            print("ERROR: Invalid phone format. Enter 7-15 digits. Try again.")
            continue
        break
    
    # Generate unique user ID
    users = read_file(FILE_USERS)
    new_user_id = get_next_numeric_id('U', users)
    
    # Create and save new user record
    new_user = [new_user_id, name, email, phone]
    users.append(new_user)
    
    if write_file(FILE_USERS, users):
        print(f"\n✓ User registered successfully!")
        print(f"  User ID: {new_user_id}")
        print(f"  Name: {name}")
        log_activity(f"NEW_USER_REGISTERED | ID={new_user_id} | Name={name} | Email={email}")
    else:
        print("ERROR: Failed to save user to file.")


def process_bike_checkout():
    """
    Process a bike rental/checkout.
    Updates bike status, creates ride record, and logs activity.
    Implements unique feature: Automatic Ride ID Generator
    """
    print("\n" + "="*60)
    print("PROCESS BIKE CHECKOUT")
    print("="*60)
    
    # Verify user exists
    users = read_file(FILE_USERS)
    user_id = input("Enter user ID (e.g., U001): ").strip()
    
    if not validate_user_id(user_id, users):
        print(f"ERROR: User {user_id} not found in system.")
        return
    
    # Get user details for display
    user_name = "Unknown"
    for user in users:
        if user[0] == user_id:
            user_name = user[1]
            break
    
    # Show available bikes
    bikes = read_file(FILE_BIKES)
    available_bikes = []
    for bike in bikes:
        if bike[1] == STATUS_AVAILABLE:
            available_bikes.append(bike)
    
    if not available_bikes:
        print("ERROR: No available bikes in system right now.")
        return
    
    print("\nAvailable bikes:")
    print(f"{'Bike ID':<8} {'Status':<12} {'Station':<15}")
    print("-" * 40)
    for bike in available_bikes:
        print(f"{bike[0]:<8} {bike[1]:<12} {bike[2]:<15}")
    
    # Select bike
    bike_id = input("\nEnter bike ID to checkout: ").strip().upper()
    
    if not validate_bike_id(bike_id, bikes):
        print(f"ERROR: Bike {bike_id} not found.")
        return
    
    # Check if selected bike is available
    bike_found = False
    for bike in bikes:
        if bike[0] == bike_id and bike[1] == STATUS_AVAILABLE:
            bike[1] = STATUS_RENTED
            bike_found = True
            break
    
    if not bike_found:
        print(f"ERROR: Bike {bike_id} is not available for checkout.")
        return
    
    # Generate unique ride ID
    # Format: RIDE + timestamp + random 2-digit suffix
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = random.randint(10, 99)
    ride_id = f"RIDE{timestamp}{random_suffix}"
    
    # Record checkout time
    checkout_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create ride record [ride_id, bike_id, user_id, checkout_time, return_time, status, extended_times]
    rides = read_file(FILE_RIDES)
    new_ride = [ride_id, bike_id, user_id, checkout_time, "", RIDE_ACTIVE, "0"]
    rides.append(new_ride)
    
    # Save changes
    if write_file(FILE_BIKES, bikes) and write_file(FILE_RIDES, rides):
        print(f"\n✓ CHECKOUT SUCCESSFUL")
        print(f"  Ride ID: {ride_id}")
        print(f"  User: {user_name} ({user_id})")
        print(f"  Bike: {bike_id}")
        print(f"  Checkout Time: {checkout_time}")
        print(f"  Standard rental: {STANDARD_RENTAL_MINUTES} minutes")
        print(f"  Late fee applies after {STANDARD_RENTAL_MINUTES} minutes")
        log_activity(f"BIKE_CHECKOUT | RideID={ride_id} | User={user_id} | Bike={bike_id}")
    else:
        print("ERROR: Failed to save checkout to files.")


def process_bike_return():
    """
    Process a bike return.
    Calculates rental cost, handles late fees, updates bike status.
    Implements unique features:
    - Late Return Fee calculation
    - Time-Based Rental Calculation
    - File-Based Logging for daily activities
    """
    print("\n" + "="*60)
    print("PROCESS BIKE RETURN")
    print("="*60)
    
    rides = read_file(FILE_RIDES)
    
    # Show active rides
    active_rides = []
    for ride in rides:
        if ride[5] == RIDE_ACTIVE:
            active_rides.append(ride)
    
    if not active_rides:
        print("No active rides to return.")
        return
    
    print("\nActive rides:")
    print(f"{'Ride ID':<20} {'Bike ID':<8} {'User ID':<8} {'Checkout Time':<20}")
    print("-" * 60)
    for ride in active_rides:
        print(f"{ride[0]:<20} {ride[1]:<8} {ride[2]:<8} {ride[3]:<20}")
    
    ride_id = input("\nEnter ride ID to return: ").strip().upper()
    
    # Find the ride
    ride_found_index = -1
    for i, ride in enumerate(rides):
        if ride[0] == ride_id and ride[5] == RIDE_ACTIVE:
            ride_found_index = i
            break
    
    if ride_found_index == -1:
        print(f"ERROR: Active ride {ride_id} not found.")
        return
    
    # Get ride details
    ride = rides[ride_found_index]
    bike_id = ride[1]
    user_id = ride[2]
    start_time = ride[3]
    
    # Record return time
    return_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Calculate cost
    cost, duration_minutes, is_late = calculate_ride_cost(start_time, return_time)
    
    # Update ride record
    ride[4] = return_time
    ride[5] = RIDE_COMPLETED
    
    # Update bike status back to available
    bikes = read_file(FILE_BIKES)
    for bike in bikes:
        if bike[0] == bike_id:
            bike[1] = STATUS_AVAILABLE
            # Increment usage count
            if len(bike) > 3:
                try:
                    bike[3] = str(int(bike[3]) + 1)
                except ValueError:
                    bike[3] = "1"
            break
    
    # Save all changes
    if write_file(FILE_BIKES, bikes) and write_file(FILE_RIDES, rides):
        print(f"\n✓ RETURN SUCCESSFUL")
        print(f"  Ride ID: {ride_id}")
        print(f"  Bike: {bike_id}")
        print(f"  Duration: {duration_minutes} minutes")
        print(f"  Return Time: {return_time}")
        
        if is_late:
            print(f"  ⚠ LATE RETURN - Additional fee applied")
            print(f"  Standard rental ({STANDARD_RENTAL_MINUTES} min): ${STANDARD_RENTAL_MINUTES * RENTAL_RATE_PER_MINUTE:.2f}")
            late_minutes = duration_minutes - STANDARD_RENTAL_MINUTES
            print(f"  Late fee ({late_minutes} min @ ${LATE_FEE_PER_MINUTE}/min): ${late_minutes * LATE_FEE_PER_MINUTE:.2f}")
        else:
            print(f"  Rental duration within standard period")
        
        print(f"  TOTAL COST: ${cost:.2f}")
        log_activity(f"BIKE_RETURN | RideID={ride_id} | Bike={bike_id} | User={user_id} | Duration={duration_minutes}min | Cost=${cost:.2f}")
    else:
        print("ERROR: Failed to save return to files.")


def cancel_active_ride():
    """
    Cancel an active ride without charges.
    Returns bike to available status and updates ride status to cancelled.
    """
    print("\n" + "="*60)
    print("CANCEL ACTIVE RIDE")
    print("="*60)
    
    rides = read_file(FILE_RIDES)
    
    # Show active rides
    active_rides = []
    for ride in rides:
        if ride[5] == RIDE_ACTIVE:
            active_rides.append(ride)
    
    if not active_rides:
        print("No active rides to cancel.")
        return
    
    print("\nActive rides:")
    for i, ride in enumerate(active_rides):
        print(f"{i+1}. Ride ID: {ride[0]}, Bike: {ride[1]}, User: {ride[2]}")
    
    ride_id = input("\nEnter ride ID to cancel: ").strip().upper()
    
    # Find and cancel ride
    ride_found_index = -1
    for i, ride in enumerate(rides):
        if ride[0] == ride_id and ride[5] == RIDE_ACTIVE:
            ride_found_index = i
            break
    
    if ride_found_index == -1:
        print(f"ERROR: Active ride {ride_id} not found.")
        return
    
    # Get ride details
    ride = rides[ride_found_index]
    bike_id = ride[1]
    user_id = ride[2]
    
    # Update ride status
    ride[5] = RIDE_CANCELLED
    
    # Return bike to available
    bikes = read_file(FILE_BIKES)
    for bike in bikes:
        if bike[0] == bike_id:
            bike[1] = STATUS_AVAILABLE
            break
    
    # Save changes
    if write_file(FILE_BIKES, bikes) and write_file(FILE_RIDES, rides):
        print(f"\n✓ RIDE CANCELLED")
        print(f"  Ride ID: {ride_id}")
        print(f"  Bike {bike_id} returned to available status")
        print(f"  No charges applied")
        log_activity(f"RIDE_CANCELLED | RideID={ride_id} | User={user_id} | Bike={bike_id}")
    else:
        print("ERROR: Failed to save cancellation to files.")


def view_current_active_rides():
    """
    Display all currently active rides in the system.
    Shows ride details including bike, user, and start time.
    """
    print("\n" + "="*60)
    print("CURRENT ACTIVE RIDES")
    print("="*60)
    
    rides = read_file(FILE_RIDES)
    active_rides = []
    
    for ride in rides:
        if ride[5] == RIDE_ACTIVE:
            active_rides.append(ride)
    
    if not active_rides:
        print("\nNo active rides at this time.")
        return
    
    print(f"\nTotal active rides: {len(active_rides)}\n")
    print(f"{'Ride ID':<20} {'Bike ID':<8} {'User ID':<8} {'Start Time':<20}")
    print("-" * 60)
    
    for ride in active_rides:
        print(f"{ride[0]:<20} {ride[1]:<8} {ride[2]:<8} {ride[3]:<20}")
    
    # Calculate stats
    print(f"\nTotal bikes currently out: {len(active_rides)}")


def view_user_ride_history():
    """
    Display all rides (active, completed, cancelled) for a specific user.
    Shows detailed ride information including dates, times, and status.
    """
    print("\n" + "="*60)
    print("VIEW USER RIDE HISTORY")
    print("="*60)
    
    users = read_file(FILE_USERS)
    user_id = input("Enter user ID (e.g., U001): ").strip().upper()
    
    if not validate_user_id(user_id, users):
        print(f"ERROR: User {user_id} not found.")
        return
    
    # Get user name
    user_name = "Unknown"
    for user in users:
        if user[0] == user_id:
            user_name = user[1]
            break
    
    rides = read_file(FILE_RIDES)
    user_rides = []
    
    for ride in rides:
        if ride[2] == user_id:
            user_rides.append(ride)
    
    if not user_rides:
        print(f"\nNo ride history found for user {user_id}.")
        return
    
    print(f"\nRide history for {user_name} ({user_id}):\n")
    print(f"{'Ride ID':<20} {'Bike ID':<8} {'Start Time':<20} {'End Time':<20} {'Status':<12}")
    print("-" * 85)
    
    for ride in user_rides:
        ride_id = ride[0]
        bike_id = ride[1]
        start_time = ride[3]
        end_time = ride[4] if ride[4] else "Ongoing"
        status = ride[5]
        
        print(f"{ride_id:<20} {bike_id:<8} {start_time:<20} {end_time:<20} {status:<12}")
    
    # Summary stats
    completed = sum(1 for r in user_rides if r[5] == RIDE_COMPLETED)
    active = sum(1 for r in user_rides if r[5] == RIDE_ACTIVE)
    cancelled = sum(1 for r in user_rides if r[5] == RIDE_CANCELLED)
    
    print(f"\n--- RIDE SUMMARY ---")
    print(f"Total rides: {len(user_rides)}")
    print(f"  Completed: {completed}")
    print(f"  Active: {active}")
    print(f"  Cancelled: {cancelled}")


def ride_officer_menu():
    """Main menu for Ride Officer role"""
    while True:
        print("\n" + "="*60)
        print("RIDE OFFICER MENU")
        print("="*60)
        print("1. Register new user")
        print("2. Process bike checkout")
        print("3. Process bike return")
        print("4. Cancel active ride")
        print("5. View current active rides")
        print("6. View user ride history")
        print("0. Return to main menu")
        print("-"*60)
        
        choice = input("Select option (0-6): ").strip()
        
        if choice == '1':
            register_new_user()
        elif choice == '2':
            process_bike_checkout()
        elif choice == '3':
            process_bike_return()
        elif choice == '4':
            cancel_active_ride()
        elif choice == '5':
            view_current_active_rides()
        elif choice == '6':
            view_user_ride_history()
        elif choice == '0':
            break
        else:
            print("ERROR: Invalid option. Please select 0-6.")
            input("Press Enter to continue...")


# ============================================================================
# USER / MEMBER FUNCTIONS - View bikes/stations, request rental/extension
# ============================================================================

def view_available_bikes_and_stations():
    """
    Display all available bikes and their current locations.
    Also show station status with bike counts and capacity.
    """
    print("\n" + "="*60)
    print("AVAILABLE BIKES AND STATIONS")
    print("="*60)
    
    bikes = read_file(FILE_BIKES)
    stations = read_file(FILE_STATIONS)
    
    # Filter available bikes
    available_bikes = []
    for bike in bikes:
        if bike[1] == STATUS_AVAILABLE:
            available_bikes.append(bike)
    
    if not available_bikes:
        print("\nNo bikes available for rental at this moment.")
    else:
        print(f"\nAvailable bikes: {len(available_bikes)}\n")
        print(f"{'Bike ID':<8} {'Status':<12} {'Station ID':<12} {'Station Name':<20}")
        print("-" * 60)
        
        for bike in available_bikes:
            bike_id = bike[0]
            station_id = bike[2]
            
            # Find station name
            station_name = "Unknown"
            for station in stations:
                if station[0] == station_id:
                    station_name = station[1]
                    break
            
            print(f"{bike_id:<8} {STATUS_AVAILABLE:<12} {station_id:<12} {station_name:<20}")
    
    # Show station status
    print(f"\n{'='*60}")
    print("STATION STATUS")
    print("="*60 + "\n")
    print(f"{'Station ID':<12} {'Station Name':<20} {'Available':<12} {'Capacity':<10} {'Utilization':<12}")
    print("-" * 70)
    
    for station in stations:
        station_id = station[0]
        station_name = station[1]
        capacity = int(station[2])
        current_bikes = int(station[3])
        
        utilization = (capacity - current_bikes) / capacity * 100 if capacity > 0 else 0
        
        print(f"{station_id:<12} {station_name:<20} {current_bikes:<12} {capacity:<10} {utilization:<11.0f}%")


def request_bike_rental():
    """
    Allow a user to request a bike rental.
    User must provide valid user ID and select available bike.
    """
    print("\n" + "="*60)
    print("REQUEST BIKE RENTAL")
    print("="*60)
    
    users = read_file(FILE_USERS)
    user_id = input("\nEnter your user ID (e.g., U001): ").strip().upper()
    
    if not validate_user_id(user_id, users):
        print(f"ERROR: User ID {user_id} not found. Please register first.")
        return
    
    # Get user name
    user_name = "Unknown"
    for user in users:
        if user[0] == user_id:
            user_name = user[1]
            break
    
    # Show available bikes
    bikes = read_file(FILE_BIKES)
    stations = read_file(FILE_STATIONS)
    
    available_bikes = []
    for bike in bikes:
        if bike[1] == STATUS_AVAILABLE:
            available_bikes.append(bike)
    
    if not available_bikes:
        print("ERROR: No available bikes at this moment. Please try again later.")
        return
    
    print(f"\nHello {user_name}! Here are available bikes:\n")
    print(f"{'Bike ID':<8} {'Station ID':<12} {'Station Name':<20}")
    print("-" * 45)
    
    for bike in available_bikes:
        bike_id = bike[0]
        station_id = bike[2]
        
        station_name = "Unknown"
        for station in stations:
            if station[0] == station_id:
                station_name = station[1]
                break
        
        print(f"{bike_id:<8} {station_id:<12} {station_name:<20}")
    
    bike_id = input("\nEnter bike ID to rent: ").strip().upper()
    
    if not validate_bike_id(bike_id, bikes):
        print(f"ERROR: Bike {bike_id} not found.")
        return
    
    # Check if bike is available
    bike_found = False
    for bike in bikes:
        if bike[0] == bike_id and bike[1] == STATUS_AVAILABLE:
            bike[1] = STATUS_RENTED
            bike_found = True
            break
    
    if not bike_found:
        print(f"ERROR: Bike {bike_id} is not available.")
        return
    
    # Generate ride ID
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = random.randint(10, 99)
    ride_id = f"RIDE{timestamp}{random_suffix}"
    
    checkout_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create ride record
    rides = read_file(FILE_RIDES)
    new_ride = [ride_id, bike_id, user_id, checkout_time, "", RIDE_ACTIVE, "0"]
    rides.append(new_ride)
    
    if write_file(FILE_BIKES, bikes) and write_file(FILE_RIDES, rides):
        print(f"\n✓ RENTAL REQUEST APPROVED")
        print(f"  Ride ID: {ride_id}")
        print(f"  Bike: {bike_id}")
        print(f"  Checkout time: {checkout_time}")
        print(f"  Standard rental period: {STANDARD_RENTAL_MINUTES} minutes")
        print(f"  Keep your Ride ID for return/extension requests")
        log_activity(f"USER_RENTAL_REQUEST | RideID={ride_id} | User={user_id} | Bike={bike_id}")
    else:
        print("ERROR: Failed to process rental request.")


def request_ride_extension():
    """
    Allow user to request extension for active ride.
    Extends standard rental period by additional time.
    """
    print("\n" + "="*60)
    print("REQUEST RIDE EXTENSION")
    print("="*60)
    
    users = read_file(FILE_USERS)
    user_id = input("\nEnter your user ID: ").strip().upper()
    
    if not validate_user_id(user_id, users):
        print(f"ERROR: User {user_id} not found.")
        return
    
    rides = read_file(FILE_RIDES)
    
    # Show active rides for this user
    active_user_rides = []
    for ride in rides:
        if ride[2] == user_id and ride[5] == RIDE_ACTIVE:
            active_user_rides.append(ride)
    
    if not active_user_rides:
        print("ERROR: You have no active rides to extend.")
        return
    
    print("\nYour active rides:\n")
    print(f"{'Ride ID':<20} {'Bike ID':<8} {'Start Time':<20}")
    print("-" * 50)
    
    for ride in active_user_rides:
        print(f"{ride[0]:<20} {ride[1]:<8} {ride[3]:<20}")
    
    ride_id = input("\nEnter ride ID to extend: ").strip().upper()
    
    # Find ride
    ride_index = -1
    for i, ride in enumerate(rides):
        if ride[0] == ride_id and ride[2] == user_id and ride[5] == RIDE_ACTIVE:
            ride_index = i
            break
    
    if ride_index == -1:
        print(f"ERROR: Active ride {ride_id} not found for your account.")
        return
    
    # Get extension time
    while True:
        try:
            extension_minutes = int(input("Enter extension time in minutes (e.g., 30): "))
            if extension_minutes <= 0:
                print("ERROR: Extension time must be positive.")
                continue
            if extension_minutes > 240:
                print("ERROR: Maximum extension is 240 minutes.")
                continue
            break
        except ValueError:
            print("ERROR: Please enter a valid number.")
    
    # Update ride record
    ride = rides[ride_index]
    current_extensions = int(ride[6]) if len(ride) > 6 else 0
    ride[6] = str(current_extensions + extension_minutes)
    
    if write_file(FILE_RIDES, rides):
        print(f"\n✓ EXTENSION APPROVED")
        print(f"  Ride ID: {ride_id}")
        print(f"  Additional time: {extension_minutes} minutes")
        print(f"  Please return bike before new deadline")
        print(f"  Late fees will apply if you exceed the new limit")
        log_activity(f"RIDE_EXTENSION_REQUEST | RideID={ride_id} | User={user_id} | ExtensionMin={extension_minutes}")
    else:
        print("ERROR: Failed to process extension.")


def view_my_ride_history():
    """
    Display ride history for the current user.
    User provides their ID and sees all their rides.
    """
    print("\n" + "="*60)
    print("MY RIDE HISTORY")
    print("="*60)
    
    users = read_file(FILE_USERS)
    user_id = input("\nEnter your user ID: ").strip().upper()
    
    if not validate_user_id(user_id, users):
        print(f"ERROR: User {user_id} not found.")
        return
    
    # Get user name
    user_name = "Unknown"
    for user in users:
        if user[0] == user_id:
            user_name = user[1]
            break
    
    rides = read_file(FILE_RIDES)
    user_rides = []
    
    for ride in rides:
        if ride[2] == user_id:
            user_rides.append(ride)
    
    if not user_rides:
        print(f"\nNo ride history for {user_name}.")
        return
    
    print(f"\nRide history for {user_name}:\n")
    print(f"{'Ride ID':<20} {'Bike':<8} {'Start Time':<20} {'End Time':<20} {'Status':<12}")
    print("-" * 85)
    
    for ride in user_rides:
        ride_id = ride[0]
        bike_id = ride[1]
        start_time = ride[3]
        end_time = ride[4] if ride[4] else "Ongoing"
        status = ride[5]
        
        print(f"{ride_id:<20} {bike_id:<8} {start_time:<20} {end_time:<20} {status:<12}")
    
    # Summary
    completed = sum(1 for r in user_rides if r[5] == RIDE_COMPLETED)
    active = sum(1 for r in user_rides if r[5] == RIDE_ACTIVE)
    
    print(f"\n--- SUMMARY ---")
    print(f"Total rides: {len(user_rides)}")
    print(f"Completed: {completed}")
    print(f"Active: {active}")


def user_menu():
    """Main menu for User/Member role"""
    while True:
        print("\n" + "="*60)
        print("USER / MEMBER MENU")
        print("="*60)
        print("1. View available bikes and stations")
        print("2. Request bike rental")
        print("3. Request ride extension")
        print("4. View my ride history")
        print("0. Return to main menu")
        print("-"*60)
        
        choice = input("Select option (0-4): ").strip()
        
        if choice == '1':
            view_available_bikes_and_stations()
        elif choice == '2':
            request_bike_rental()
        elif choice == '3':
            request_ride_extension()
        elif choice == '4':
            view_my_ride_history()
        elif choice == '0':
            break
        else:
            print("ERROR: Invalid option. Please select 0-4.")
            input("Press Enter to continue...")


# ============================================================================
# MAINTENANCE STAFF FUNCTIONS - Update status, log records, generate reports
# ============================================================================

def update_bike_maintenance_status():
    """
    Update maintenance status of a bike.
    Statuses: available, maintenance, repair
    """
    print("\n" + "="*60)
    print("UPDATE BIKE MAINTENANCE STATUS")
    print("="*60)
    
    bikes = read_file(FILE_BIKES)
    
    print("\nBike status options:")
    print("  1. available  - Bike is ready for use")
    print("  2. maintenance - Bike requires service")
    print("  3. repair     - Bike is broken and needs repair")
    
    bike_id = input("\nEnter bike ID to update: ").strip().upper()
    
    if not validate_bike_id(bike_id, bikes):
        print(f"ERROR: Bike {bike_id} not found.")
        return
    
    # Find bike and show current status
    current_status = None
    for bike in bikes:
        if bike[0] == bike_id:
            current_status = bike[1]
            print(f"\nCurrent status of {bike_id}: {current_status}")
            break
    
    while True:
        status_choice = input("\nSelect new status (1-3): ").strip()
        
        if status_choice == '1':
            new_status = STATUS_AVAILABLE
            break
        elif status_choice == '2':
            new_status = STATUS_MAINTENANCE
            break
        elif status_choice == '3':
            new_status = STATUS_REPAIR
            break
        else:
            print("ERROR: Invalid option. Please select 1-3.")
            continue
    
    # Update bike status
    for bike in bikes:
        if bike[0] == bike_id:
            bike[1] = new_status
            break
    
    if write_file(FILE_BIKES, bikes):
        print(f"\n✓ STATUS UPDATED")
        print(f"  Bike: {bike_id}")
        print(f"  Previous status: {current_status}")
        print(f"  New status: {new_status}")
        log_activity(f"MAINTENANCE_STATUS_UPDATE | Bike={bike_id} | OldStatus={current_status} | NewStatus={new_status}")
    else:
        print("ERROR: Failed to save status update.")


def log_maintenance_record():
    """
    Log a maintenance record for a bike.
    Records type of maintenance, date, and cost.
    """
    print("\n" + "="*60)
    print("LOG MAINTENANCE RECORD")
    print("="*60)
    
    bikes = read_file(FILE_BIKES)
    bike_id = input("\nEnter bike ID: ").strip().upper()
    
    if not validate_bike_id(bike_id, bikes):
        print(f"ERROR: Bike {bike_id} not found.")
        return
    
    print("\nMaintenance types:")
    print("  1. service    - Regular maintenance/cleaning")
    print("  2. repair     - Fix broken parts")
    print("  3. inspection - Safety inspection")
    
    while True:
        maint_choice = input("\nSelect maintenance type (1-3): ").strip()
        
        if maint_choice == '1':
            maint_type = MAINT_SERVICE
            break
        elif maint_choice == '2':
            maint_type = MAINT_REPAIR
            break
        elif maint_choice == '3':
            maint_type = MAINT_INSPECTION
            break
        else:
            print("ERROR: Invalid option. Please select 1-3.")
            continue
    
    # Get maintenance cost
    while True:
        try:
            cost = float(input("Enter maintenance cost in USD: $"))
            if cost < 0:
                print("ERROR: Cost cannot be negative.")
                continue
            break
        except ValueError:
            print("ERROR: Please enter a valid number.")
    
    # Generate maintenance record ID
    maintenance = read_file(FILE_MAINTENANCE)
    record_id = get_next_numeric_id('MAINT', maintenance)
    
    # Record current date
    record_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Create maintenance record
    new_record = [record_id, bike_id, record_date, maint_type, str(cost)]
    maintenance.append(new_record)
    
    # Update bike status if it's available
    for bike in bikes:
        if bike[0] == bike_id and bike[1] == STATUS_AVAILABLE:
            bike[1] = STATUS_MAINTENANCE
            break
    
    if write_file(FILE_MAINTENANCE, maintenance) and write_file(FILE_BIKES, bikes):
        print(f"\n✓ MAINTENANCE RECORD LOGGED")
        print(f"  Record ID: {record_id}")
        print(f"  Bike: {bike_id}")
        print(f"  Type: {maint_type}")
        print(f"  Date: {record_date}")
        print(f"  Cost: ${cost:.2f}")
        log_activity(f"MAINTENANCE_RECORD_LOGGED | RecordID={record_id} | Bike={bike_id} | Type={maint_type} | Cost=${cost:.2f}")
    else:
        print("ERROR: Failed to save maintenance record.")


def generate_maintenance_report():
    """
    Generate comprehensive maintenance summary report.
    Shows bikes in maintenance, all records, costs, and statistics.
    """
    print("\n" + "="*60)
    print("MAINTENANCE SUMMARY REPORT")
    print("="*60)
    
    bikes = read_file(FILE_BIKES)
    maintenance = read_file(FILE_MAINTENANCE)
    
    # Section 1: Bikes currently in maintenance/repair
    print("\n--- BIKES CURRENTLY UNDER MAINTENANCE/REPAIR ---")
    problem_bikes = []
    for bike in bikes:
        if bike[1] in [STATUS_MAINTENANCE, STATUS_REPAIR]:
            problem_bikes.append(bike)
    
    if not problem_bikes:
        print("No bikes currently in maintenance or repair.")
    else:
        print(f"\n{'Bike ID':<8} {'Status':<12} {'Station':<12} {'Usage Count':<12}")
        print("-" * 50)
        for bike in problem_bikes:
            bike_id = bike[0]
            status = bike[1]
            station = bike[2]
            usage = bike[3] if len(bike) > 3 else "N/A"
            print(f"{bike_id:<8} {status:<12} {station:<12} {usage:<12}")
    
    # Section 2: All maintenance records
    print(f"\n--- ALL MAINTENANCE RECORDS ---")
    if not maintenance:
        print("No maintenance records found.")
    else:
        print(f"\n{'Record ID':<10} {'Bike':<8} {'Date':<12} {'Type':<12} {'Cost':<10}")
        print("-" * 55)
        
        for record in maintenance:
            record_id = record[0]
            bike_id = record[1]
            date = record[2]
            maint_type = record[3]
            cost = float(record[4])
            
            print(f"{record_id:<10} {bike_id:<8} {date:<12} {maint_type:<12} ${cost:<9.2f}")
    
    # Section 3: Statistics
    print(f"\n--- MAINTENANCE STATISTICS ---")
    
    total_cost = 0.0
    for record in maintenance:
        total_cost += float(record[4])
    
    print(f"Total maintenance cost: ${total_cost:.2f}")
    print(f"Total maintenance records: {len(maintenance)}")
    print(f"Average cost per record: ${total_cost / len(maintenance):.2f}" if maintenance else "Average: N/A")
    
    # Find most serviced bike
    bike_service_count = {}
    for record in maintenance:
        bike_id = record[1]
        bike_service_count[bike_id] = bike_service_count.get(bike_id, 0) + 1
    
    if bike_service_count:
        most_serviced_bike = None
        max_services = 0
        for bike_id, count in bike_service_count.items():
            if count > max_services:
                max_services = count
                most_serviced_bike = bike_id
        
        print(f"Most serviced bike: {most_serviced_bike} ({max_services} records)")
    
    log_activity(f"MAINTENANCE_REPORT_GENERATED | TotalRecords={len(maintenance)} | TotalCost=${total_cost:.2f}")


def maintenance_menu():
    """Main menu for Maintenance Staff role"""
    while True:
        print("\n" + "="*60)
        print("MAINTENANCE STAFF MENU")
        print("="*60)
        print("1. Update bike maintenance status")
        print("2. Log maintenance record")
        print("3. Generate maintenance summary report")
        print("0. Return to main menu")
        print("-"*60)
        
        choice = input("Select option (0-3): ").strip()
        
        if choice == '1':
            update_bike_maintenance_status()
        elif choice == '2':
            log_maintenance_record()
        elif choice == '3':
            generate_maintenance_report()
        elif choice == '0':
            break
        else:
            print("ERROR: Invalid option. Please select 0-3.")
            input("Press Enter to continue...")


# ============================================================================
# STATION MANAGER FUNCTIONS - Monitor availability, redistribute bikes
# ============================================================================

def monitor_bike_availability():
    """
    Monitor and display current bike availability at each station.
    Shows capacity, current bikes, and utilization percentage.
    """
    print("\n" + "="*60)
    print("MONITOR BIKE AVAILABILITY AT ALL STATIONS")
    print("="*60)
    
    stations = read_file(FILE_STATIONS)
    
    if not stations:
        print("No station data found.")
        return
    
    print(f"\n{'Station ID':<12} {'Station Name':<20} {'Available':<12} {'Capacity':<10} {'Status':<15}")
    print("-" * 75)
    
    for station in stations:
        station_id = station[0]
        name = station[1]
        capacity = int(station[2])
        current = int(station[3])
        
        # Determine status based on availability
        if current <= 2:
            status = "⚠ LOW STOCK"
        elif current >= capacity * 0.8:
            status = "🔥 HIGH DEMAND"
        else:
            status = "✓ OK"
        
        print(f"{station_id:<12} {name:<20} {current:<12} {capacity:<10} {status:<15}")
    
    # Calculate total stats
    total_capacity = sum(int(s[2]) for s in stations)
    total_available = sum(int(s[3]) for s in stations)
    
    print(f"\n--- SYSTEM SUMMARY ---")
    print(f"Total capacity: {total_capacity} bikes")
    print(f"Total available: {total_available} bikes")
    print(f"Utilization: {((total_capacity - total_available) / total_capacity * 100):.1f}%")


def redistribute_bikes_between_stations():
    """
    Move a bike from one station to another.
    Implements load balancing for better bike distribution.
    """
    print("\n" + "="*60)
    print("REDISTRIBUTE BIKES BETWEEN STATIONS")
    print("="*60)
    
    stations = read_file(FILE_STATIONS)
    bikes = read_file(FILE_BIKES)
    
    if len(stations) < 2:
        print("ERROR: Need at least two stations to redistribute bikes.")
        return
    
    # Show current station status
    print("\nCurrent station status:\n")
    print(f"{'Station ID':<12} {'Name':<20} {'Available':<12} {'Capacity':<10}")
    print("-" * 60)
    
    for station in stations:
        station_id = station[0]
        name = station[1]
        capacity = int(station[2])
        current = int(station[3])
        print(f"{station_id:<12} {name:<20} {current:<12} {capacity:<10}")
    
    # Get source and destination stations
    while True:
        source_id = input("\nEnter source station ID (from): ").strip().upper()
        source_station = None
        for s in stations:
            if s[0] == source_id:
                source_station = s
                break
        
        if not source_station:
            print(f"ERROR: Station {source_id} not found.")
            continue
        
        if int(source_station[3]) == 0:
            print(f"ERROR: Station {source_id} has no bikes to move.")
            continue
        
        break
    
    while True:
        dest_id = input("Enter destination station ID (to): ").strip().upper()
        
        if source_id == dest_id:
            print("ERROR: Source and destination must be different.")
            continue
        
        dest_station = None
        for s in stations:
            if s[0] == dest_id:
                dest_station = s
                break
        
        if not dest_station:
            print(f"ERROR: Station {dest_id} not found.")
            continue
        
        if int(dest_station[3]) >= int(dest_station[2]):
            print(f"ERROR: Station {dest_id} is at full capacity.")
            continue
        
        break
    
    # Find available bike at source station
    bike_to_move = None
    for bike in bikes:
        if bike[2] == source_id and bike[1] == STATUS_AVAILABLE:
            bike_to_move = bike
            break
    
    if not bike_to_move:
        print(f"ERROR: No available bikes at station {source_id}.")
        return
    
    # Perform redistribution
    bike_to_move[2] = dest_id
    source_station[3] = str(int(source_station[3]) - 1)
    dest_station[3] = str(int(dest_station[3]) + 1)
    
    if write_file(FILE_BIKES, bikes) and write_file(FILE_STATIONS, stations):
        print(f"\n✓ BIKE REDISTRIBUTION COMPLETED")
        print(f"  Bike ID: {bike_to_move[0]}")
        print(f"  From: {source_id} -> To: {dest_id}")
        print(f"  Source station now has: {source_station[3]} bikes")
        print(f"  Destination station now has: {dest_station[3]} bikes")
        log_activity(f"BIKE_REDISTRIBUTION | BikeID={bike_to_move[0]} | FromStation={source_id} | ToStation={dest_id}")
    else:
        print("ERROR: Failed to save redistribution changes.")


def report_low_stock_high_demand():
    """
    Generate report for administrator showing low-stock and high-demand stations.
    Provides recommendations for bike redistribution.
    """
    print("\n" + "="*60)
    print("REPORT: LOW-STOCK & HIGH-DEMAND STATIONS")
    print("="*60)
    
    stations = read_file(FILE_STATIONS)
    
    low_stock_stations = []
    high_demand_stations = []
    
    for station in stations:
        station_id = station[0]
        name = station[1]
        capacity = int(station[2])
        current = int(station[3])
        
        # Low stock: 2 or fewer bikes
        if current <= 2:
            low_stock_stations.append((station_id, name, current, capacity))
        
        # High demand: 70% or more bikes are rented (i.e., < 30% available)
        if capacity > 0 and current < capacity * 0.3:
            high_demand_stations.append((station_id, name, current, capacity))
    
    print("\n--- LOW-STOCK STATIONS (2 or fewer bikes) ---")
    if not low_stock_stations:
        print("No low-stock stations at this time.")
    else:
        print(f"\n{'Station ID':<12} {'Name':<20} {'Available':<12} {'Capacity':<10}")
        print("-" * 60)
        for station_id, name, current, capacity in low_stock_stations:
            print(f"{station_id:<12} {name:<20} {current:<12} {capacity:<10}")
    
    print("\n--- HIGH-DEMAND STATIONS (< 30% bikes available) ---")
    if not high_demand_stations:
        print("No high-demand stations at this time.")
    else:
        print(f"\n{'Station ID':<12} {'Name':<20} {'Available':<12} {'Capacity':<10} {'Utilization':<12}")
        print("-" * 70)
        for station_id, name, current, capacity in high_demand_stations:
            utilization = ((capacity - current) / capacity * 100)
            print(f"{station_id:<12} {name:<20} {current:<12} {capacity:<10} {utilization:<11.0f}%")
    
    # Recommendations
    print("\n--- RECOMMENDATIONS ---")
    if low_stock_stations or high_demand_stations:
        print("⚠ ACTION REQUIRED:")
        print("  1. Move bikes from nearby high-capacity stations to low-stock stations")
        print("  2. Monitor demand patterns and plan maintenance accordingly")
        print("  3. Consider adding more bikes to high-demand stations")
    else:
        print("✓ All stations are well-balanced. Good operational status.")
    
    log_activity(f"STATION_REPORT_GENERATED | LowStockCount={len(low_stock_stations)} | HighDemandCount={len(high_demand_stations)}")


def station_manager_menu():
    """Main menu for Station Manager role"""
    while True:
        print("\n" + "="*60)
        print("STATION MANAGER MENU")
        print("="*60)
        print("1. Monitor bike availability at all stations")
        print("2. Redistribute bikes between stations")
        print("3. Report low-stock and high-demand stations")
        print("0. Return to main menu")
        print("-"*60)
        
        choice = input("Select option (0-3): ").strip()
        
        if choice == '1':
            monitor_bike_availability()
        elif choice == '2':
            redistribute_bikes_between_stations()
        elif choice == '3':
            report_low_stock_high_demand()
        elif choice == '0':
            break
        else:
            print("ERROR: Invalid option. Please select 0-3.")
            input("Press Enter to continue...")


# ============================================================================
# ADMINISTRATOR FUNCTIONS - Manage bikes/stations, view all data, reports
# ============================================================================

def add_new_bike():
    """Add a new bike to the system"""
    print("\n" + "="*60)
    print("ADD NEW BIKE")
    print("="*60)
    
    stations = read_file(FILE_STATIONS)
    bikes = read_file(FILE_BIKES)
    
    if not stations:
        print("ERROR: No stations exist. Create station first.")
        return
    
    # Show existing stations
    print("\nExisting stations:\n")
    print(f"{'Station ID':<12} {'Name':<20} {'Capacity':<10}")
    print("-" * 45)
    for s in stations:
        print(f"{s[0]:<12} {s[1]:<20} {s[2]:<10}")
    
    bike_id = input("\nEnter new bike ID (e.g., B011): ").strip().upper()
    
    # Check for duplicate ID
    for bike in bikes:
        if bike[0] == bike_id:
            print(f"ERROR: Bike ID {bike_id} already exists.")
            return
    
    station_id = input("Enter station ID where bike will be placed: ").strip().upper()
    
    if not validate_station_id(station_id, stations):
        print(f"ERROR: Station {station_id} not found.")
        return
    
    # Create bike record [id, status, station_id, usage_count]
    new_bike = [bike_id, STATUS_AVAILABLE, station_id, "0"]
    bikes.append(new_bike)
    
    # Update station's bike count
    for station in stations:
        if station[0] == station_id:
            station[3] = str(int(station[3]) + 1)
            break
    
    if write_file(FILE_BIKES, bikes) and write_file(FILE_STATIONS, stations):
        print(f"\n✓ BIKE ADDED")
        print(f"  Bike ID: {bike_id}")
        print(f"  Status: {STATUS_AVAILABLE}")
        print(f"  Station: {station_id}")
        log_activity(f"BIKE_ADDED | BikeID={bike_id} | Station={station_id}")
    else:
        print("ERROR: Failed to save bike.")


def update_existing_bike():
    """Update bike details"""
    print("\n" + "="*60)
    print("UPDATE BIKE")
    print("="*60)
    
    bikes = read_file(FILE_BIKES)
    stations = read_file(FILE_STATIONS)
    
    bike_id = input("\nEnter bike ID to update: ").strip().upper()
    
    if not validate_bike_id(bike_id, bikes):
        print(f"ERROR: Bike {bike_id} not found.")
        return
    
    # Find bike
    bike_index = -1
    for i, bike in enumerate(bikes):
        if bike[0] == bike_id:
            bike_index = i
            print(f"\nCurrent details:")
            print(f"  Status: {bike[1]}")
            print(f"  Station: {bike[2]}")
            break
    
    # Update status
    update_status = input("\nUpdate status? (Y/N): ").strip().upper()
    if update_status == 'Y':
        print("Options: available, maintenance, repair")
        new_status = input("Enter new status: ").strip().lower()
        if new_status in [STATUS_AVAILABLE, STATUS_MAINTENANCE, STATUS_REPAIR]:
            bikes[bike_index][1] = new_status
        else:
            print("Invalid status, unchanged.")
    
    # Update station
    update_station = input("\nMove to different station? (Y/N): ").strip().upper()
    if update_station == 'Y':
        new_station_id = input("Enter new station ID: ").strip().upper()
        
        if not validate_station_id(new_station_id, stations):
            print(f"ERROR: Station {new_station_id} not found.")
        else:
            old_station_id = bikes[bike_index][2]
            
            # Update station bike counts
            for s in stations:
                if s[0] == old_station_id:
                    s[3] = str(max(0, int(s[3]) - 1))
                if s[0] == new_station_id:
                    s[3] = str(int(s[3]) + 1)
            
            bikes[bike_index][2] = new_station_id
            write_file(FILE_STATIONS, stations)
    
    if write_file(FILE_BIKES, bikes):
        print(f"\n✓ BIKE UPDATED: {bike_id}")
        log_activity(f"BIKE_UPDATED | BikeID={bike_id}")
    else:
        print("ERROR: Failed to save updates.")


def remove_existing_bike():
    """Remove a bike from system"""
    print("\n" + "="*60)
    print("REMOVE BIKE")
    print("="*60)
    
    bikes = read_file(FILE_BIKES)
    stations = read_file(FILE_STATIONS)
    
    bike_id = input("\nEnter bike ID to remove: ").strip().upper()
    
    if not validate_bike_id(bike_id, bikes):
        print(f"ERROR: Bike {bike_id} not found.")
        return
    
    # Find bike
    bike_index = -1
    station_id = None
    for i, bike in enumerate(bikes):
        if bike[0] == bike_id:
            bike_index = i
            station_id = bike[2]
            
            # Cannot remove rented bikes
            if bike[1] == STATUS_RENTED:
                print(f"ERROR: Cannot remove {bike_id} - it is currently rented.")
                return
            break
    
    # Remove bike
    del bikes[bike_index]
    
    # Update station count
    for s in stations:
        if s[0] == station_id:
            s[3] = str(max(0, int(s[3]) - 1))
            break
    
    if write_file(FILE_BIKES, bikes) and write_file(FILE_STATIONS, stations):
        print(f"\n✓ BIKE REMOVED: {bike_id}")
        log_activity(f"BIKE_REMOVED | BikeID={bike_id}")
    else:
        print("ERROR: Failed to save changes.")


def add_new_station():
    """Add a new station to the system"""
    print("\n" + "="*60)
    print("ADD NEW STATION")
    print("="*60)
    
    stations = read_file(FILE_STATIONS)
    
    station_id = input("\nEnter station ID (e.g., S06): ").strip().upper()
    
    # Check for duplicate
    for s in stations:
        if s[0] == station_id:
            print(f"ERROR: Station ID {station_id} already exists.")
            return
    
    station_name = input("Enter station name (e.g., Downtown Center): ").strip()
    if not station_name:
        print("ERROR: Station name cannot be empty.")
        return
    
    while True:
        try:
            capacity = int(input("Enter bike capacity (max bikes at this station): "))
            if capacity <= 0:
                print("ERROR: Capacity must be positive.")
                continue
            break
        except ValueError:
            print("ERROR: Please enter a valid number.")
    
    # Create station record [id, name, capacity, current_bikes]
    new_station = [station_id, station_name, str(capacity), "0"]
    stations.append(new_station)
    
    if write_file(FILE_STATIONS, stations):
        print(f"\n✓ STATION ADDED")
        print(f"  Station ID: {station_id}")
        print(f"  Name: {station_name}")
        print(f"  Capacity: {capacity} bikes")
        log_activity(f"STATION_ADDED | StationID={station_id} | Name={station_name} | Capacity={capacity}")
    else:
        print("ERROR: Failed to save station.")


def update_existing_station():
    """Update station details"""
    print("\n" + "="*60)
    print("UPDATE STATION")
    print("="*60)
    
    stations = read_file(FILE_STATIONS)
    
    station_id = input("\nEnter station ID to update: ").strip().upper()
    
    if not validate_station_id(station_id, stations):
        print(f"ERROR: Station {station_id} not found.")
        return
    
    # Find station
    station_index = -1
    for i, s in enumerate(stations):
        if s[0] == station_id:
            station_index = i
            print(f"\nCurrent details:")
            print(f"  Name: {s[1]}")
            print(f"  Capacity: {s[2]} bikes")
            print(f"  Current bikes: {s[3]}")
            break
    
    # Update name
    update_name = input("\nUpdate station name? (Y/N): ").strip().upper()
    if update_name == 'Y':
        new_name = input("Enter new name: ").strip()
        if new_name:
            stations[station_index][1] = new_name
    
    # Update capacity
    update_capacity = input("Update capacity? (Y/N): ").strip().upper()
    if update_capacity == 'Y':
        while True:
            try:
                new_capacity = int(input("Enter new capacity: "))
                if new_capacity <= 0:
                    print("ERROR: Capacity must be positive.")
                    continue
                
                current_bikes = int(stations[station_index][3])
                if new_capacity < current_bikes:
                    print(f"WARNING: New capacity ({new_capacity}) is less than current bikes ({current_bikes})")
                    confirm = input("Continue anyway? (Y/N): ").strip().upper()
                    if confirm != 'Y':
                        continue
                    stations[station_index][3] = str(new_capacity)
                
                stations[station_index][2] = str(new_capacity)
                break
            except ValueError:
                print("ERROR: Please enter a valid number.")
    
    if write_file(FILE_STATIONS, stations):
        print(f"\n✓ STATION UPDATED: {station_id}")
        log_activity(f"STATION_UPDATED | StationID={station_id}")
    else:
        print("ERROR: Failed to save updates.")


def remove_existing_station():
    """Remove a station from system"""
    print("\n" + "="*60)
    print("REMOVE STATION")
    print("="*60)
    
    stations = read_file(FILE_STATIONS)
    bikes = read_file(FILE_BIKES)
    
    station_id = input("\nEnter station ID to remove: ").strip().upper()
    
    if not validate_station_id(station_id, stations):
        print(f"ERROR: Station {station_id} not found.")
        return
    
    # Check for bikes at this station
    bikes_at_station = []
    for bike in bikes:
        if bike[2] == station_id:
            bikes_at_station.append(bike[0])
    
    if bikes_at_station:
        print(f"ERROR: Station has {len(bikes_at_station)} bikes. Remove bikes first.")
        print(f"Bikes: {', '.join(bikes_at_station)}")
        return
    
    # Remove station
    station_index = -1
    for i, s in enumerate(stations):
        if s[0] == station_id:
            station_index = i
            break
    
    del stations[station_index]
    
    if write_file(FILE_STATIONS, stations):
        print(f"\n✓ STATION REMOVED: {station_id}")
        log_activity(f"STATION_REMOVED | StationID={station_id}")
    else:
        print("ERROR: Failed to save changes.")


def view_all_system_data():
    """Display all data in the system - comprehensive data overview"""
    print("\n" + "="*60)
    print("SYSTEM DATA OVERVIEW")
    print("="*60)
    
    users = read_file(FILE_USERS)
    bikes = read_file(FILE_BIKES)
    stations = read_file(FILE_STATIONS)
    rides = read_file(FILE_RIDES)
    maintenance = read_file(FILE_MAINTENANCE)
    
    # Users
    print("\n--- USERS ---")
    if not users:
        print("No users registered.")
    else:
        print(f"\n{'User ID':<8} {'Name':<20} {'Email':<25} {'Phone':<12}")
        print("-" * 70)
        for user in users:
            print(f"{user[0]:<8} {user[1]:<20} {user[2]:<25} {user[3]:<12}")
    
    # Bikes
    print(f"\n--- BIKES ({len(bikes)} total) ---")
    if not bikes:
        print("No bikes in system.")
    else:
        print(f"\n{'Bike ID':<8} {'Status':<12} {'Station':<12} {'Usage':<8}")
        print("-" * 50)
        for bike in bikes:
            usage = bike[3] if len(bike) > 3 else "0"
            print(f"{bike[0]:<8} {bike[1]:<12} {bike[2]:<12} {usage:<8}")
    
    # Stations
    print(f"\n--- STATIONS ({len(stations)} total) ---")
    if not stations:
        print("No stations in system.")
    else:
        print(f"\n{'Station ID':<12} {'Name':<20} {'Capacity':<10} {'Current':<10}")
        print("-" * 55)
        for s in stations:
            print(f"{s[0]:<12} {s[1]:<20} {s[2]:<10} {s[3]:<10}")
    
    # Rides
    print(f"\n--- RIDES ({len(rides)} total) ---")
    if not rides:
        print("No rides recorded.")
    else:
        active = sum(1 for r in rides if r[5] == RIDE_ACTIVE)
        completed = sum(1 for r in rides if r[5] == RIDE_COMPLETED)
        cancelled = sum(1 for r in rides if r[5] == RIDE_CANCELLED)
        print(f"Active: {active} | Completed: {completed} | Cancelled: {cancelled}")
    
    # Maintenance
    print(f"\n--- MAINTENANCE RECORDS ({len(maintenance)} total) ---")
    if not maintenance:
        print("No maintenance records.")
    else:
        total_cost = sum(float(m[4]) for m in maintenance)
        print(f"Total records: {len(maintenance)}")
        print(f"Total maintenance cost: ${total_cost:.2f}")


def generate_overall_system_report():
    """
    Generate comprehensive system report.
    Shows total rides, available bikes, high-demand stations, and usage statistics.
    Implements unique features:
    - Bike Usage Frequency Tracking
    - Station Demand Tracking
    """
    print("\n" + "="*60)
    print("OVERALL SYSTEM REPORT")
    print("="*60)
    
    bikes = read_file(FILE_BIKES)
    stations = read_file(FILE_STATIONS)
    rides = read_file(FILE_RIDES)
    users = read_file(FILE_USERS)
    
    # Rides statistics
    total_rides = len(rides)
    completed_rides = sum(1 for r in rides if r[5] == RIDE_COMPLETED)
    active_rides = sum(1 for r in rides if r[5] == RIDE_ACTIVE)
    cancelled_rides = sum(1 for r in rides if r[5] == RIDE_CANCELLED)
    
    print("\n--- RIDE STATISTICS ---")
    print(f"Total rides recorded: {total_rides}")
    print(f"  Completed: {completed_rides}")
    print(f"  Active: {active_rides}")
    print(f"  Cancelled: {cancelled_rides}")
    
    # Bike statistics
    print("\n--- BIKE STATUS ---")
    available_count = sum(1 for b in bikes if b[1] == STATUS_AVAILABLE)
    rented_count = sum(1 for b in bikes if b[1] == STATUS_RENTED)
    maintenance_count = sum(1 for b in bikes if b[1] == STATUS_MAINTENANCE)
    repair_count = sum(1 for b in bikes if b[1] == STATUS_REPAIR)
    
    print(f"Total bikes: {len(bikes)}")
    print(f"  Available: {available_count}")
    print(f"  Rented: {rented_count}")
    print(f"  In maintenance: {maintenance_count}")
    print(f"  In repair: {repair_count}")
    
    # Bike usage frequency
    print("\n--- TOP USED BIKES (Usage Frequency) ---")
    bike_usage = []
    for bike in bikes:
        if len(bike) > 3:
            try:
                usage = int(bike[3])
                bike_usage.append((bike[0], usage))
            except ValueError:
                pass
    
    if bike_usage:
        bike_usage.sort(key=lambda x: x[1], reverse=True)
        print(f"\n{'Bike ID':<8} {'Usage Count':<12}")
        print("-" * 25)
        for bike_id, usage in bike_usage[:5]:
            print(f"{bike_id:<8} {usage:<12}")
        avg_usage = sum(u for _, u in bike_usage) / len(bike_usage)
        print(f"\nAverage usage per bike: {avg_usage:.1f}")
    
    # Station demand analysis
    print("\n--- STATION DEMAND ANALYSIS ---")
    high_demand_stations = []
    low_stock_stations = []
    
    for station in stations:
        station_id = station[0]
        name = station[1]
        capacity = int(station[2])
        current = int(station[3])
        
        if current <= 2:
            low_stock_stations.append((station_id, name, current, capacity))
        if capacity > 0 and current < capacity * 0.3:
            high_demand_stations.append((station_id, name, current, capacity))
    
    print(f"Total stations: {len(stations)}")
    print(f"High-demand stations: {len(high_demand_stations)}")
    print(f"Low-stock stations: {len(low_stock_stations)}")
    
    if high_demand_stations:
        print(f"\nHigh-demand stations requiring bikes:")
        for sid, name, current, cap in high_demand_stations[:3]:
            print(f"  {sid} - {name}: {current}/{cap} bikes")
    
    # User statistics
    print("\n--- USER STATISTICS ---")
    print(f"Total registered users: {len(users)}")
    
    # Calculate revenue (if tracking completed rides)
    print("\n--- REVENUE ESTIMATE ---")
    total_revenue = 0
    for ride in rides:
        if ride[5] == RIDE_COMPLETED:
            start_time = ride[3]
            end_time = ride[4]
            cost, _, _ = calculate_ride_cost(start_time, end_time)
            total_revenue += cost
    print(f"Estimated revenue from completed rides: ${total_revenue:.2f}")
    
    print("\n--- SYSTEM STATUS ---")
    print("✓ System operational and functioning normally")
    
    log_activity(f"OVERALL_REPORT_GENERATED | TotalRides={total_rides} | CompletedRides={completed_rides} | AvailableBikes={available_count}")


def admin_menu():
    """Main menu for Administrator role"""
    while True:
        print("\n" + "="*60)
        print("ADMINISTRATOR MENU")
        print("="*60)
        print("--- BIKE MANAGEMENT ---")
        print("1. Add new bike")
        print("2. Update bike")
        print("3. Remove bike")
        print("--- STATION MANAGEMENT ---")
        print("4. Add new station")
        print("5. Update station")
        print("6. Remove station")
        print("--- SYSTEM DATA ---")
        print("7. View all system data")
        print("8. Generate overall system report")
        print("0. Return to main menu")
        print("-"*60)
        
        choice = input("Select option (0-8): ").strip()
        
        if choice == '1':
            add_new_bike()
        elif choice == '2':
            update_existing_bike()
        elif choice == '3':
            remove_existing_bike()
        elif choice == '4':
            add_new_station()
        elif choice == '5':
            update_existing_station()
        elif choice == '6':
            remove_existing_station()
        elif choice == '7':
            view_all_system_data()
        elif choice == '8':
            generate_overall_system_report()
        elif choice == '0':
            break
        else:
            print("ERROR: Invalid option. Please select 0-8.")
            input("Press Enter to continue...")


# ============================================================================
# MAIN MENU - Role selection and program entry point
# ============================================================================

def main_menu():
    """
    Main entry point for the CityCycle Bike Sharing Management System.
    Displays role options and routes to appropriate menu.
    """
    while True:
        print("\n" + "="*60)
        print("CITYCYCLE - BIKE SHARING MANAGEMENT SYSTEM")
        print("="*60)
        print("\nSelect your role:")
        print("1. Studio Administrator")
        print("2. Ride Officer")
        print("3. User / Member")
        print("4. Maintenance Staff")
        print("5. Station Manager")
        print("0. Exit system")
        print("-"*60)
        
        role_choice = input("Select role (0-5): ").strip()
        
        if role_choice == '1':
            admin_menu()
        elif role_choice == '2':
            ride_officer_menu()
        elif role_choice == '3':
            user_menu()
        elif role_choice == '4':
            maintenance_menu()
        elif role_choice == '5':
            station_manager_menu()
        elif role_choice == '0':
            print("\n" + "="*60)
            print("Thank you for using CityCycle!")
            print("Goodbye!")
            print("="*60 + "\n")
            log_activity("SYSTEM_SHUTDOWN")
            break
        else:
            print("ERROR: Invalid option. Please select 0-5.")
            input("Press Enter to continue...")


# ============================================================================
# PROGRAM ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("CITYCYCLE - URBAN BIKE SHARING MANAGEMENT SYSTEM")
    print("Initializing system...")
    print("="*60)
    
    log_activity("SYSTEM_STARTUP")
    main_menu()
