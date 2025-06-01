# Zarak Khan
# This application allows you to analyze various
# aspects of the Chicago traffic camera database.


import sqlite3
import matplotlib.pyplot as plt
import datetime

##################################################################
#
# Helper function: formatInt
#
# Returns a string for the given integer with comma separators,
# or "0" if None.
#
def formatInt(val):
    if val is None:
        return "0"
    else:
        return f"{val:,}"


##################################################################
#
# print_stats
#
# Executes SQL queries to retrieve and display the initial stats.
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    
    # 1) Number of Red Light Cameras:
    dbCursor.execute("SELECT COUNT(*) FROM RedCameras;")
    redCamCount = dbCursor.fetchone()[0]

    # 2) Number of Speed Cameras:
    dbCursor.execute("SELECT COUNT(*) FROM SpeedCameras;")
    speedCamCount = dbCursor.fetchone()[0]
    
    # 3) Number of Red Light Camera Violation Entries:
    dbCursor.execute("SELECT COUNT(*) FROM RedViolations;")
    redViolationsCount = dbCursor.fetchone()[0]
    
    # 4) Number of Speed Camera Violation Entries:
    dbCursor.execute("SELECT COUNT(*) FROM SpeedViolations;")
    speedViolationsCount = dbCursor.fetchone()[0]

    # 5) Find min & max date across both RedViolations and SpeedViolations:
    dbCursor.execute("SELECT MIN(Violation_Date), MAX(Violation_Date) FROM RedViolations;")
    rminmax = dbCursor.fetchone()
    dbCursor.execute("SELECT MIN(Violation_Date), MAX(Violation_Date) FROM SpeedViolations;")
    sminmax = dbCursor.fetchone()
    # Handle possible None values (if any table is empty).
    minDates = []
    maxDates = []
    if rminmax[0] is not None: 
        minDates.append(rminmax[0])
    if rminmax[1] is not None:
        maxDates.append(rminmax[1])
    if sminmax[0] is not None:
        minDates.append(sminmax[0])
    if sminmax[1] is not None:
        maxDates.append(sminmax[1])
    
    if len(minDates) > 0:
        overallMinDate = min(minDates)
    else:
        overallMinDate = "----"
    if len(maxDates) > 0:
        overallMaxDate = max(maxDates)
    else:
        overallMaxDate = "----"
    
    # 6) Total Number of Red Light Camera Violations:
    dbCursor.execute("SELECT SUM(Num_Violations) FROM RedViolations;")
    totalRedV = dbCursor.fetchone()[0]
    
    # 7) Total Number of Speed Camera Violations:
    dbCursor.execute("SELECT SUM(Num_Violations) FROM SpeedViolations;")
    totalSpeedV = dbCursor.fetchone()[0]
    
    print("General Statistics:")
    print("  Number of Red Light Cameras:", formatInt(redCamCount))
    print("  Number of Speed Cameras:", formatInt(speedCamCount))
    print("  Number of Red Light Camera Violation Entries:", formatInt(redViolationsCount))
    print("  Number of Speed Camera Violation Entries:", formatInt(speedViolationsCount))
    print("  Range of Dates in the Database:", f"{overallMinDate} - {overallMaxDate}")
    print("  Total Number of Red Light Camera Violations:", formatInt(totalRedV))
    print("  Total Number of Speed Camera Violations:", formatInt(totalSpeedV))


##################################################################
#
# Command 1
#
# Find an intersection by name (user may include _ or % wildcards).
# Print them in alphabetical order by intersection name.
#
def command1_find_intersection(dbConn):
    userInput = input("Enter the name of the intersection to find (wildcards _ and % allowed): ")
    
    dbCursor = dbConn.cursor()
    # Use LIKE since wildcards are allowed:
    sql = """
    SELECT Intersection_ID, Intersection
    FROM Intersections
    WHERE Intersection LIKE ?
    ORDER BY Intersection ASC;
    """
    dbCursor.execute(sql, [userInput])
    rows = dbCursor.fetchall()
    
    if len(rows) == 0:
        print("No intersections matching that name were found.")
    else:
        for row in rows:
            intersectionID = row[0]
            intersectionName = row[1]
            print(f"{intersectionID} : {intersectionName}")


##################################################################
#
# Command 2
#
# Given an intersection name (exact match), find and list all cameras.
# If none found in red or speed, print messages accordingly.
#
def command2_find_all_cameras(dbConn):
    print("Enter the name of the intersection (no wildcards allowed): ")
    userInput = input()
    dbCursor = dbConn.cursor()
    
    # First, find the Intersection_ID from Intersections table with exact match:
    sql = """
    SELECT Intersection_ID
    FROM Intersections
    WHERE Intersection = ?
    """
    dbCursor.execute(sql, [userInput])
    row = dbCursor.fetchone()
    
    if row is None:
        # Intersection does not exist in DB at all -> no cameras of either type
        print("No red light cameras found at that intersection.")
        print()
        print("No speed cameras found at that intersection.")
        return
    
    intersectionID = row[0]
    
    # Query red cameras:
    sql_red = """
    SELECT Camera_ID, Address
    FROM RedCameras
    WHERE Intersection_ID = ?
    ORDER BY Camera_ID ASC;
    """
    dbCursor.execute(sql_red, [intersectionID])
    redRows = dbCursor.fetchall()
    
    # Query speed cameras:
    sql_speed = """
    SELECT Camera_ID, Address
    FROM SpeedCameras
    WHERE Intersection_ID = ?
    ORDER BY Camera_ID ASC;
    """
    dbCursor.execute(sql_speed, [intersectionID])
    speedRows = dbCursor.fetchall()
    
    # Print results:
    if len(redRows) == 0:
        print("No red light cameras found at that intersection.")
        print()
    else:
        print("Red Light Cameras:")
        for row in redRows:
            print(f"   {row[0]} : {row[1]}")
        print()

    if len(speedRows) == 0:
        print("No speed cameras found at that intersection.")
    else:
        print("Speed Cameras:")
        for row in speedRows:
            print(f"   {row[0]} : {row[1]}")


##################################################################
#
# Command 3
#
# For a given date, output # of red light violations, # of speed violations,
# plus percentages of each out of total. If total is 0 -> "No violations on record".
#
def command3_percentage_by_date(dbConn):
    userInput = input("Enter the date that you would like to look at (format should be YYYY-MM-DD): ")
    dbCursor = dbConn.cursor()
    
    # Query total # red violations for that date:
    sql_red = """
    SELECT SUM(Num_Violations)
    FROM RedViolations
    WHERE Violation_Date = ?
    """
    dbCursor.execute(sql_red, [userInput])
    redCount = dbCursor.fetchone()[0]
    if redCount is None:
        redCount = 0
    
    # Query total # speed violations for that date:
    sql_speed = """
    SELECT SUM(Num_Violations)
    FROM SpeedViolations
    WHERE Violation_Date = ?
    """
    dbCursor.execute(sql_speed, [userInput])
    speedCount = dbCursor.fetchone()[0]
    if speedCount is None:
        speedCount = 0
    
    total = redCount + speedCount
    if total == 0:
        print("No violations on record for that date.")
        return
    
    pctRed = (redCount / total) * 100
    pctSpeed = (speedCount / total) * 100
    
    print("Number of Red Light Violations:", f"{redCount:,}", f"({pctRed:.3f}%)")
    print("Number of Speed Violations:", f"{speedCount:,}", f"({pctSpeed:.3f}%)")
    print("Total Number of Violations:", f"{total:,}")


##################################################################
#
# Command 4
#
# Output the number of red light cameras at each intersection (descending),
# plus % of total red cameras in the city; then speed cameras similarly.
#
def command4_cameras_per_intersection(dbConn):
    dbCursor = dbConn.cursor()
    
    # Number of red cameras at each intersection:
    # plus total # of red cameras:
    dbCursor.execute("SELECT COUNT(*) FROM RedCameras;")
    totalRedCams = dbCursor.fetchone()[0]
    
    sql_red = """
    SELECT Intersections.Intersection, Intersections.Intersection_ID,
           COUNT(RedCameras.Camera_ID) as RedCount
    FROM Intersections
    JOIN RedCameras
      ON Intersections.Intersection_ID = RedCameras.Intersection_ID
    GROUP BY Intersections.Intersection_ID
    ORDER BY RedCount DESC, Intersections.Intersection_ID DESC;
    """
    dbCursor.execute(sql_red)
    redRows = dbCursor.fetchall()
    
    print("Number of Red Light Cameras at Each Intersection")
    if totalRedCams <= 0:
        # If there are no red cameras at all:
        pass
    else:
        for row in redRows:
            name = row[0]
            iid = row[1]
            count = row[2]
            pct = (count / totalRedCams) * 100
            print(f"  {name} ({iid}) : {count} ({pct:.3f}%)")
    print()
    # Speed cameras:
    dbCursor.execute("SELECT COUNT(*) FROM SpeedCameras;")
    totalSpeedCams = dbCursor.fetchone()[0]
    
    sql_speed = """
    SELECT Intersections.Intersection, Intersections.Intersection_ID,
           COUNT(SpeedCameras.Camera_ID) as SpeedCount
    FROM Intersections
    JOIN SpeedCameras
      ON Intersections.Intersection_ID = SpeedCameras.Intersection_ID
    GROUP BY Intersections.Intersection_ID
    ORDER BY SpeedCount DESC, Intersections.Intersection_ID DESC;
    """
    dbCursor.execute(sql_speed)
    speedRows = dbCursor.fetchall()
    
    print("Number of Speed Cameras at Each Intersection")
    if totalSpeedCams <= 0:
        pass
    else:
        for row in speedRows:
            name = row[0]
            iid = row[1]
            count = row[2]
            pct = (count / totalSpeedCams) * 100
            print(f"  {name} ({iid}) : {count} ({pct:.3f}%)")


##################################################################
#
# Command 5
#
# Given a year, output # of red violations at each intersection that year,
# ordered descending by count, plus the percentage out of the total for that year.
# Then the same for speed. If none -> "No red light violations..." etc.
#
def command5_violations_per_intersection(dbConn):
    userYear = input("Enter the year that you would like to analyze: ")
    print()
    dbCursor = dbConn.cursor()
    
    # Red Light:
    sql_red = """
    SELECT I.Intersection, I.Intersection_ID,
           SUM(R.Num_Violations) as TotalRed
    FROM RedViolations R
    JOIN RedCameras RC
      ON R.Camera_ID = RC.Camera_ID
    JOIN Intersections I
      ON RC.Intersection_ID = I.Intersection_ID
    WHERE strftime('%Y', R.Violation_Date) = ?
    GROUP BY I.Intersection_ID
    ORDER BY TotalRed DESC, I.Intersection_ID DESC;
    """
    dbCursor.execute(sql_red, [userYear])
    redRows = dbCursor.fetchall()
    
    # Sum of all red violations for that year:
    sql_red_sum = """
    SELECT SUM(R.Num_Violations)
    FROM RedViolations R
    WHERE strftime('%Y', R.Violation_Date) = ?
    """
    dbCursor.execute(sql_red_sum, [userYear])
    totalRed = dbCursor.fetchone()[0]
    if totalRed is None:
        totalRed = 0
    
    print(f"Number of Red Light Violations at Each Intersection for {userYear}")
    if len(redRows) == 0:
        print("No red light violations on record for that year.")
        print()
    else:
        for row in redRows:
            interName = row[0]
            interID = row[1]
            count = row[2]
            pct = 0.0
            if totalRed > 0:
                pct = (count / totalRed) * 100
            print(f"  {interName} ({interID}) : {count:,} ({pct:.3f}%)")
        print(f"Total Red Light Violations in {userYear} : {formatInt(totalRed)}")
        print()
    
    # Speed:
    sql_speed = """
    SELECT I.Intersection, I.Intersection_ID,
           SUM(S.Num_Violations) as TotalSpeed
    FROM SpeedViolations S
    JOIN SpeedCameras SC
      ON S.Camera_ID = SC.Camera_ID
    JOIN Intersections I
      ON SC.Intersection_ID = I.Intersection_ID
    WHERE strftime('%Y', S.Violation_Date) = ?
    GROUP BY I.Intersection_ID
    ORDER BY TotalSpeed DESC, I.Intersection_ID DESC;
    """
    dbCursor.execute(sql_speed, [userYear])
    speedRows = dbCursor.fetchall()
    
    # Sum of all speed violations for that year:
    sql_speed_sum = """
    SELECT SUM(S.Num_Violations)
    FROM SpeedViolations S
    WHERE strftime('%Y', S.Violation_Date) = ?
    """
    dbCursor.execute(sql_speed_sum, [userYear])
    totalSpeed = dbCursor.fetchone()[0]
    if totalSpeed is None:
        totalSpeed = 0
    
    print(f"Number of Speed Violations at Each Intersection for {userYear}")
    if len(speedRows) == 0:
        print("No speed violations on record for that year.")
    else:
        for row in speedRows:
            interName = row[0]
            interID = row[1]
            count = row[2]
            pct = 0.0
            if totalSpeed > 0:
                pct = (count / totalSpeed) * 100
            print(f"  {interName} ({interID}) : {count:,} ({pct:.3f}%)")
        print(f"Total Speed Violations in {userYear} : {formatInt(totalSpeed)}")


##################################################################
#
# Command 6
#
# Given a camera ID, output # of violations by year (ascending).
# Then optionally plot. If ID not found -> error message.
#
def command6_violations_by_year(dbConn):
    userCamID = input("Enter a camera ID: ")
    dbCursor = dbConn.cursor()
    
    # Check if camera ID is in RedCameras or SpeedCameras:
    sql_check = """
    SELECT 'red' as Type FROM RedCameras WHERE Camera_ID = ?
    UNION
    SELECT 'speed' as Type FROM SpeedCameras WHERE Camera_ID = ?;
    """
    dbCursor.execute(sql_check, [userCamID, userCamID])
    typeRows = dbCursor.fetchall()
    if len(typeRows) == 0:
        print("No cameras matching that ID were found in the database.")
        return
    
    # We do one query for red, one for speed
    isRed = any(tr[0] == 'red' for tr in typeRows)
    isSpeed = any(tr[0] == 'speed' for tr in typeRows)
    
    # We can union the results if the camera appears in both tables.
    # Then we group by year
    
    # We'll gather year -> total violations from whichever table is relevant.
    yearlyData = {}
    
    if isRed:
        sql_red = """
        SELECT strftime('%Y', Violation_Date) as YY,
               SUM(Num_Violations)
        FROM RedViolations
        WHERE Camera_ID = ?
        GROUP BY YY
        ORDER BY YY ASC;
        """
        dbCursor.execute(sql_red, [userCamID])
        rows = dbCursor.fetchall()
        for r in rows:
            year = r[0]
            count = r[1]
            yearlyData[year] = yearlyData.get(year, 0) + count
    
    if isSpeed:
        sql_speed = """
        SELECT strftime('%Y', Violation_Date) as YY,
               SUM(Num_Violations)
        FROM SpeedViolations
        WHERE Camera_ID = ?
        GROUP BY YY
        ORDER BY YY ASC;
        """
        dbCursor.execute(sql_speed, [userCamID])
        rows = dbCursor.fetchall()
        for r in rows:
            year = r[0]
            count = r[1]
            yearlyData[year] = yearlyData.get(year, 0) + count
    
    # Sort by year ascending (as strings)

    sortedYears = sorted(yearlyData.keys())

    if len(sortedYears) == 0:
        # camera was found, but no violations
        print(f"Yearly Violations for Camera {userCamID}")
        # just print nothing
    else:
        print(f"Yearly Violations for Camera {userCamID}")
        for y in sortedYears:
            print(f"{y} : {yearlyData[y]:,}")

    print()

    # Ask user if they want to plot:
    doPlot = input("Plot? (y/n) ")
    if doPlot.lower() == 'y':
        if len(sortedYears) > 0:
            # Determine the range of years to plot (from earliest to latest in data)
            startYear = int(sortedYears[0])
            endYear   = int(sortedYears[-1])

            x_vals = []
            y_vals = []
            # Fill in 0 for any missing years in that continuous range
            for year in range(startYear, endYear+1):
                strYear = str(year)
                count   = yearlyData.get(strYear, 0)  # default to 0 if missing
                x_vals.append(year)
                y_vals.append(count)

            plt.figure(figsize=(8, 5))
            # line plot
            plt.plot(x_vals, y_vals, color='blue', marker='o')
            plt.xlabel("Year")
            plt.ylabel("Number of Violations")
            plt.title(f"Yearly Violations for Camera {userCamID}")
            plt.xticks(x_vals)
            plt.show()


##################################################################
#
# Command 7
#
# Given a camera ID and a year, output # of violations for each month in ascending order by month.
# Then optionally plot. If ID not found -> error message.
#
def command7_violations_by_month(dbConn):
    userCamID = input("Enter a camera ID: ")
    dbCursor = dbConn.cursor()
    
    # Check if camera ID is in RedCameras or SpeedCameras:
    sql_check = """
    SELECT 'red' as Type FROM RedCameras WHERE Camera_ID = ?
    UNION
    SELECT 'speed' as Type FROM SpeedCameras WHERE Camera_ID = ?;
    """
    dbCursor.execute(sql_check, [userCamID, userCamID])
    typeRows = dbCursor.fetchall()
    if len(typeRows) == 0:
        print("No cameras matching that ID were found in the database.")
        return
    
    userYear = input("Enter a year: ")
    
    isRed = any(tr[0] == 'red' for tr in typeRows)
    isSpeed = any(tr[0] == 'speed' for tr in typeRows)
    
    # We'll gather month -> total violations. We’ll store in monthlyData["MM"] = sum
    monthlyData = {}
    
    if isRed:
        sql_red = """
        SELECT strftime('%m', Violation_Date) as MM,
               SUM(Num_Violations)
        FROM RedViolations
        WHERE Camera_ID = ?
          AND strftime('%Y', Violation_Date) = ?
        GROUP BY MM
        ORDER BY MM ASC;
        """
        dbCursor.execute(sql_red, [userCamID, userYear])
        rows = dbCursor.fetchall()
        for r in rows:
            mm = r[0] 
            count = r[1]
            monthlyData[mm] = monthlyData.get(mm, 0) + count
    
    if isSpeed:
        sql_speed = """
        SELECT strftime('%m', Violation_Date) as MM,
               SUM(Num_Violations)
        FROM SpeedViolations
        WHERE Camera_ID = ?
          AND strftime('%Y', Violation_Date) = ?
        GROUP BY MM
        ORDER BY MM ASC;
        """
        dbCursor.execute(sql_speed, [userCamID, userYear])
        rows = dbCursor.fetchall()
        for r in rows:
            mm = r[0]
            count = r[1]
            monthlyData[mm] = monthlyData.get(mm, 0) + count
    
    print(f"Monthly Violations for Camera {userCamID} in {userYear}")
    # We want to list months 1-12 in ascending order. If no data = no lines.
    for monthNum in range(1, 13):
        mm = f"{monthNum:02d}"  # '01'...'12'
        if mm in monthlyData:
            print(f"{mm}/{userYear} : {monthlyData[mm]:,}")
    print()
    # Optionally plot:
    doPlot = input("Plot? (y/n) ")
    if doPlot.lower() == 'y':
        # Build data for months 1-12:
        x_vals = []
        y_vals = []
        for mm in sorted(monthlyData.keys()):
            x_vals.append(int(mm))
            y_vals.append(monthlyData[mm])
        
        plt.figure(figsize=(8, 5))
        plt.plot(x_vals, y_vals, color='blue')
        month_labels = [f"{m:02d}" for m in x_vals]
        plt.xticks(x_vals, month_labels)
        plt.xlabel("Month")
        plt.ylabel("Number of Violations")
        plt.title(f"Monthly Violations for Camera {userCamID} ({userYear})")
        plt.xticks(x_vals)
        plt.show()


##################################################################
#
# Command 8
#
# Given a year, output # of red violations (across all cameras) & # of speed violations (across all cameras)
# for each day in that year (ascending by date).
# Only print first 5 lines and last 5 lines for each. Optionally plot the entire year (Jan 1 - Dec 31),
# with 0 for days not in the DB.
#
def command8_compare_by_day(dbConn):
    userYear = input("Enter a year: ")
    dbCursor = dbConn.cursor()
    
    # We’ll gather a dict: dateStr -> (#red, #speed)
    # dateStr in 'YYYY-MM-DD' format
    dailyData = {}
    
    # Red query:
    sql_red = """
    SELECT Violation_Date, SUM(Num_Violations)
    FROM RedViolations
    WHERE strftime('%Y', Violation_Date) = ?
    GROUP BY Violation_Date
    ORDER BY Violation_Date;
    """
    dbCursor.execute(sql_red, [userYear])
    rows = dbCursor.fetchall()
    for r in rows:
        d = r[0]
        cnt = r[1]
        if d not in dailyData:
            dailyData[d] = [0, 0]
        dailyData[d][0] = cnt
    
    # Speed query:
    sql_speed = """
    SELECT Violation_Date, SUM(Num_Violations)
    FROM SpeedViolations
    WHERE strftime('%Y', Violation_Date) = ?
    GROUP BY Violation_Date
    ORDER BY Violation_Date;
    """
    dbCursor.execute(sql_speed, [userYear])
    rows = dbCursor.fetchall()
    for r in rows:
        d = r[0]
        cnt = r[1]
        if d not in dailyData:
            dailyData[d] = [0, 0]
        dailyData[d][1] = cnt
    
    # Sort the dictionary by date:
    # The keys are 'YYYY-MM-DD' so we can sort them or use datetime.
    sortedDates = sorted(dailyData.keys())
    
    print("Red Light Violations:")
    if len(sortedDates) == 0:
        # just print nothing
        pass
    else:
        # Print the first 5 and last 5
        # dailyData[date] = [redCount, speedCount]
        first5 = sortedDates[:5]
        last5 = sortedDates[-5:]
        
        for d in first5:
            print(d, dailyData[d][0])
        if len(sortedDates) > 5:
            for d in last5:
                print(d, dailyData[d][0])
    
    print("Speed Violations:")
    if len(sortedDates) == 0:
        pass
    else:
        first5 = sortedDates[:5]
        last5 = sortedDates[-5:]
        
        for d in first5:
            print(d, dailyData[d][1])
        if len(sortedDates) > 5:
            for d in last5:
                print(d, dailyData[d][1])
    print()
    # Option to plot:
    doPlot = input("Plot? (y/n) ")
    if doPlot.lower() == 'y':
        # For each day from Jan 1 to Dec 31 of userYear, we might have data or zero.
        # Make x array of datetime.date objects, plus y arrays for red & speed.
        try:
            yInt = int(userYear)
        except:
            # invalid int means no plot
            return
        
        # Start date, end date:
        startD = datetime.date(yInt, 1, 1)
        endD = datetime.date(yInt, 12, 31)
        delta = datetime.timedelta(days=1)
        
        dayList = []

        redList = []
        speedList = []

        # We'll keep an integer i that increments for each day.
        i = 0
        currD = startD
        while currD <= endD:
            i += 1  # Day counter in the year
            dStr = currD.isoformat()
            
            if dStr in dailyData:
                rVal = dailyData[dStr][0]
                sVal = dailyData[dStr][1]
            else:
                rVal = 0
                sVal = 0
            
            dayList.append(i)
            redList.append(rVal)
            speedList.append(sVal)
            
            currD += delta

        #plots
        plt.figure(figsize=(8, 5))
        plt.plot(dayList, redList, color='red', label='Red Light')
        plt.plot(dayList, speedList, color='orange', label='Speed')
        plt.title(f"Violations Each Day of {userYear}")
        plt.xlabel("Day")
        plt.ylabel("Number of Violations")
        plt.legend()
        plt.show()


##################################################################
#
# Command 9
#
# Given a street name, find all cameras whose address is on that street.
# Then optionally plot them on the map of Chicago (chicago.png).
#
def command9_cameras_on_street(dbConn):
    userStreet = input("Enter a street name: ")
    # "Address LIKE '%street%'" for both RedCameras, SpeedCameras.
    # Then combine results. 
    # differentiate red vs speed so that we can color them differently on the plot.
    
    dbCursor = dbConn.cursor()
    
    # Red cameras:
    sql_red = """
    SELECT Camera_ID, Address, Latitude, Longitude
    FROM RedCameras
    WHERE Address LIKE ?
    ORDER BY Camera_ID ASC
    """
    dbCursor.execute(sql_red, [f"%{userStreet}%"])
    redRows = dbCursor.fetchall()
    
    # Speed cameras:
    sql_speed = """
    SELECT Camera_ID, Address, Latitude, Longitude
    FROM SpeedCameras
    WHERE Address LIKE ?
    ORDER BY Camera_ID ASC
    """
    dbCursor.execute(sql_speed, [f"%{userStreet}%"])
    speedRows = dbCursor.fetchall()
    
    totalFound = len(redRows) + len(speedRows)
    if totalFound == 0:
        print(f"There are no cameras located on that street.")
        return

    print()
    print(f"List of Cameras Located on Street: {userStreet}")
    
    # Print red cameras:
    print("  Red Light Cameras:")
    if len(redRows) == 0:
        pass
    else:
        for row in redRows:
            cid = row[0]
            addr = row[1]
            lat = row[2]
            lng = row[3]
            print(f"     {cid} : {addr} ({lat}, {lng})")
    
    # Print speed cameras:
    print("  Speed Cameras:")
    if len(speedRows) == 0:
        pass
    else:
        for row in speedRows:
            cid = row[0]
            addr = row[1]
            lat = row[2]
            lng = row[3]
            print(f"     {cid} : {addr} ({lat}, {lng})")
    print()
    # Option to plot:

    doPlot = input("Plot? (y/n) ")

    if doPlot.lower() == 'y':
        try:
            cityMap = plt.imread("chicago.png")
        except:
            print("Error: cannot find 'chicago.png' file for plotting the map.")
            return
        
        plt.figure(figsize=(8, 8))
        xydims = [-87.9277, -87.5569, 41.7012, 42.0868]
        plt.imshow(cityMap, extent=xydims)
        plt.title(f"Cameras on Street: {userStreet}")

        # SORT the rows if you want them connected in a geographic order (e.g. by longitude):
        redRows.sort(key=lambda row: row[3])    # sort by longitude, row[3]
        speedRows.sort(key=lambda row: row[3])  # for speed
        
        # Build x_red, y_red:
        x_red = [row[3] for row in redRows]   # row[3] is longitude
        y_red = [row[2] for row in redRows]   # row[2] is latitude
        
        # Build x_speed, y_speed:
        x_speed = [row[3] for row in speedRows]
        y_speed = [row[2] for row in speedRows]
        
        # Plot lines first, so they connect points in sorted order
        plt.plot(x_red, y_red, color='red')       # no label -> won't appear in legend
        plt.plot(x_speed, y_speed, color='orange')
        
        # Now scatter the points themselves:
        plt.scatter(x_red, y_red, color='red')
        plt.scatter(x_speed, y_speed, color='orange')
        
        # Annotate each camera ID:
        for row in redRows:
            cid = row[0]
            lat = row[2]
            lng = row[3]
            plt.annotate(str(cid), (lng, lat), color='black', fontsize=8)
        for row in speedRows:
            cid = row[0]
            lat = row[2]
            lng = row[3]
            plt.annotate(str(cid), (lng, lat), color='black', fontsize=8)
        
        plt.xlim([-87.9277, -87.5569])
        plt.ylim([41.7012, 42.0868])
        plt.show()


##################################################################
#
# main
#
def main():
    dbConn = sqlite3.connect('chicago-traffic-cameras.db')
    
    print("Project 1: Chicago Traffic Camera Analysis")
    print("CS 341, Spring 2025")
    print()
    print("This application allows you to analyze various")
    print("aspects of the Chicago traffic camera database.")
    print()
    
    # Print initial statistics:
    print_stats(dbConn)
    print()
    
    while True:
        print("Select a menu option: ")
        print("  1. Find an intersection by name")
        print("  2. Find all cameras at an intersection")
        print("  3. Percentage of violations for a specific date")
        print("  4. Number of cameras at each intersection")
        print("  5. Number of violations at each intersection, given a year")
        print("  6. Number of violations by year, given a camera ID")
        print("  7. Number of violations by month, given a camera ID and year")
        print("  8. Compare the number of red light and speed violations, given a year")
        print("  9. Find cameras located on a street")
        print("or x to exit the program.")
        
        choice = input("Your choice --> ")
        if choice == 'x':
            print("Exiting program.")
            break
        elif choice == '1':
            print()
            command1_find_intersection(dbConn)
        elif choice == '2':
            print()
            command2_find_all_cameras(dbConn)
        elif choice == '3':
            print()
            command3_percentage_by_date(dbConn)
        elif choice == '4':
            print()
            command4_cameras_per_intersection(dbConn)
        elif choice == '5':
            print()
            command5_violations_per_intersection(dbConn)
        elif choice == '6':
            print()
            command6_violations_by_year(dbConn)
        elif choice == '7':
            print()
            command7_violations_by_month(dbConn)
        elif choice == '8':
            print()
            command8_compare_by_day(dbConn)
        elif choice == '9':
            print()
            command9_cameras_on_street(dbConn)
        else:
            print("Error, unknown command, try again...")
        print()
    
    dbConn.close()


if __name__ == "__main__":
    main()
