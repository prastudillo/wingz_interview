# Setup Instructions

1. **Create and Activate a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   *(Adjust the above commands for your OS if necessary.)*

2. **Install Dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Apply Migrations**
   ```bash
   python manage.py migrate
   ```

4. **Populate the Database (SQLite)**
   ```bash
   python manage.py populate_rides
   ```
   This command creates sample users, rides and ride events.
   Note: current directory must be in (`wingz_interview/api/`) before running script

5. **Create a Superuser**
   ```bash
   python manage.py createsuperuser
   ```
   After you create the superuser, either via the admin site (`/admin/`) or the Django shell, **edit the user’s `role` to `'admin'`** so this user can access the secured endpoints.  
   - **Admin Site**: Log in at `http://127.0.0.1:8000/admin/`, find the user, and set the role to `'admin'`.  

6. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

7. **Access the API**
   - Open your browser to hit the endpoints (e.g. `http://127.0.0.1:8000/api/rides/`).
   - Use the credentials of the superuser (who now has an `admin` role) to authenticate and access protected endpoints.

With these steps, you’ll have an admin-capable user in your local environment who can access and manage the rides data via the protected API endpoints.

# Bonus: SQL Statement

returns the count of Trips that took more than 1 hour from Pickup to Dropoff and we want this by Month and Driver

## PostgreSQL / MySQL

```sql
SELECT
    TO_CHAR(dropoff_event.created_at, 'YYYY-MM') AS "Month",
    CONCAT(driver.first_name, ' ', driver.last_name) AS "Driver",
    COUNT(*) AS "Count of Trips > 1 hr"
FROM rides_ride AS ride
JOIN rides_user AS driver
  ON ride.id_driver = driver.id
JOIN rides_rideevent AS pickup_event
  ON pickup_event.id_ride = ride.id_ride
 AND pickup_event.description = 'Status changed to pickup'
JOIN rides_rideevent AS dropoff_event
  ON dropoff_event.id_ride = ride.id_ride
 AND dropoff_event.description = 'Status changed to dropoff'
WHERE dropoff_event.created_at - pickup_event.created_at > INTERVAL '1 hour'
GROUP BY 1, 2
ORDER BY 1, 2;
```

## SQLite

```sql
SELECT
    strftime('%Y-%m', dropoff_event.created_at) AS "Month",
    (driver.first_name || ' ' || driver.last_name) AS "Driver",
    COUNT(*) AS "Count of Trips > 1 hr"
FROM rides_ride AS ride
JOIN rides_user AS driver
  ON ride.id_driver = driver.id
JOIN rides_rideevent AS pickup_event
  ON pickup_event.id_ride = ride.id_ride
 AND pickup_event.description = 'Status changed to pickup'
JOIN rides_rideevent AS dropoff_event
  ON dropoff_event.id_ride = ride.id_ride
 AND dropoff_event.description = 'Status changed to dropoff'
WHERE (
    julianday(dropoff_event.created_at) - julianday(pickup_event.created_at)
) * 24 > 1
GROUP BY 1, 2
ORDER BY 1, 2;
```
