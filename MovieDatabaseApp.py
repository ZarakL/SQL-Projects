# main.py
# Presentation Tier for the Movie Database App (N-Tier)
# Zarak Khan
# This application allows you to analyze various aspects of the MovieLens database.
# All database queries are made through the object mapping tier (objecttier).

import sqlite3
import objecttier


# Function to display the main menu options.
def display_menu():
    print("Select a menu option: ")
    print("  1. Print general statistics about the database")
    print("  2. Find movies matching a pattern for the name")
    print("  3. Find details of a movie by movie ID")
    print("  4. Top N movies by average rating, with a minimum number of reviews")
    print("  5. Add a new review for a movie")
    print("  6. Set the tagline of a movie")
    print("or x to exit the program.")


# Command 1: Print general statistics about the database.
def command_print_stats(dbConn):
    num_movies = objecttier.num_movies(dbConn)
    num_reviews = objecttier.num_reviews(dbConn)
    print("General Statistics:")
    print(" Number of Movies: {}".format(format(num_movies, ",")))
    print(" Number of Reviews: {}".format(format(num_reviews, ",")))


# Command 2: Find movies matching a pattern.
def command_find_movies(dbConn):
    pattern = input("Enter the name of the movie to find (wildcards _ and % allowed): ")
    movies = objecttier.get_movies(dbConn, pattern)
    count = len(movies)
    print()
    print("Number of Movies Found: {}".format(count))
    
    if count > 100:
        print()
        print("There are too many movies to display (more than 100). Please narrow your search and try again.")
        
    elif count > 0:
        print()
        # Display each movie in the format: ID : Title (Release_Year)
        for movie in movies:
            print("{} : {} ({})".format(movie.Movie_ID, movie.Title, movie.Release_Year))


# Command 3: Find detailed information for a given movie.
def command_movie_details(dbConn):
    movie_id_input = input("Enter a movie ID: ")
    print()
    try:
        movie_id = int(movie_id_input)
    except ValueError:
        print("No movie matching that ID was found in the database.")
        return

    details = objecttier.get_movie_details(dbConn, movie_id)
    if details is None:
        print("No movie matching that ID was found in the database.")
    else:
        # Format numbers and strings for display.
        budget_str = "${:,}".format(details.Budget)
        revenue_str = "${:,}".format(details.Revenue)
        avg_rating_str = "{:.2f}".format(details.Avg_Rating)
        genres_str = ", ".join(details.Genres)
        if genres_str:
            genres_str += ", "
        companies_str = ", ".join(details.Production_Companies)
        if companies_str:
            companies_str += ", "
        print("{} : {}".format(details.Movie_ID, details.Title))
        print("  Release date: {}".format(details.Release_Date))
        print("  Runtime: {} (minutes)".format(details.Runtime))
        print("  Original language: {}".format(details.Original_Language))
        print("  Budget: {} (USD)".format(budget_str))
        print("  Revenue: {} (USD)".format(revenue_str))
        print("  Number of reviews: {}".format(details.Num_Reviews))
        print("  Average rating: {} (0-10)".format(avg_rating_str))
        print("  Genres: {}".format(genres_str))
        print("  Production companies: {}".format(companies_str))
        print("  Tagline: {}".format(details.Tagline))


# Command 4: Display top N movies by average rating.
def command_top_movies(dbConn):
    try:
        N = int(input("Enter a value for N: "))
    except ValueError:
        print("Please enter a positive value for N.")
        return
    if N <= 0:
        print("Please enter a positive value for N.")
        return

    try:
        min_reviews = int(input("Enter a value for the minimum number of reviews: "))
    except ValueError:
        print("Please enter a positive value for the minimum number of reviews.")
        return
    if min_reviews <= 0:
        print("Please enter a positive value for the minimum number of reviews.")
        return

    print()  # Added extra newline before displaying results.
    
    top_movies = objecttier.get_top_N_movies(dbConn, N, min_reviews)
    if not top_movies:
        print("No movies were found that fit the criteria.")
    else:
        for movie in top_movies:
            print("{} : {} ({}), Average rating = {:.2f} ({} reviews)".format(
                movie.Movie_ID, movie.Title, movie.Release_Year, movie.Avg_Rating, movie.Num_Reviews))


# Command 5: Add a new review for a movie.
def command_add_review(dbConn):
    try:
        rating = int(input("Enter a value for the new rating (0-10): "))
    except ValueError:
        print("Invalid rating. Please enter a value between 0 and 10 (inclusive).")
        return
    if rating < 0 or rating > 10:
        print("Invalid rating. Please enter a value between 0 and 10 (inclusive).")
        return

    try:
        movie_id = int(input("Enter a movie ID: "))
        print()
    except ValueError:
        print("No movie matching that ID was found in the database.")
        return

    result = objecttier.add_review(dbConn, movie_id, rating)
    if result == 1:
        print("Rating was successfully inserted into the database.")
    else:
        print("No movie matching that ID was found in the database.")


# Command 6: Set the tagline for a movie.
def command_set_tagline(dbConn):
    tagline = input("Enter a tagline: ")
    try:
        movie_id = int(input("Enter a movie ID: "))
        print()
    except ValueError:
        print("No movie matching that ID was found in the database.")
        return

    result = objecttier.set_tagline(dbConn, movie_id, tagline)
    if result == 1:
        print("Tagline was successfully set in the database.")
    else:
        print("No movie matching that ID was found in the database.")


# Main Program Execution
print("Project 2: Movie Database App (N-Tier)")
print("CS 341, Spring 2025")
print()
print("This application allows you to analyze various")
print("aspects of the MovieLens database.")
print()

# Get the database name from the user.
dbName = input("Enter the name of the database you would like to use: ")

# Connect to the SQLite database.
try:
    dbConn = sqlite3.connect(dbName)
except Exception as e:
    print("Failed to connect to the database:", e)
    exit()

print()
print("Successfully connected to the database!")
print()

# Main command loop.
while True:
    display_menu()
    cmd = input("Your choice --> ").strip()
    print()
    if cmd == 'x':
        print("Exiting program.")
        break
    elif cmd == '1':
        command_print_stats(dbConn)
    elif cmd == '2':
        command_find_movies(dbConn)
    elif cmd == '3':
        command_movie_details(dbConn)
    elif cmd == '4':
        command_top_movies(dbConn)
    elif cmd == '5':
        command_add_review(dbConn)
    elif cmd == '6':
        command_set_tagline(dbConn)
    else:
        print("Error, unknown command, try again...")
    print()

# Close the database connection.
dbConn.close()
