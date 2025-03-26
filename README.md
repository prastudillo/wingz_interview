# Setup Instructions

---

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
