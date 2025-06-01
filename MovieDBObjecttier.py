# objecttier.py
# Builds Movie-related objects from data retrieved through  
# the data tier.
# Zarak Khan

import datatier

##################################################################
#
# Movie class:
#
# Constructor(...)
# Properties (read-only):
#   Movie_ID: int
#   Title: string
#   Release_Year: string
#
class Movie:
    def __init__(self, movie_id, title, release_year):
        # Store values in private attributes.
        self._movie_id = movie_id
        self._title = title
        self._release_year = release_year

    @property
    def Movie_ID(self):
        return self._movie_id

    @property
    def Title(self):
        return self._title

    @property
    def Release_Year(self):
        return self._release_year

##################################################################
#
# MovieRating class:
#
# Constructor(...)
# Properties (read-only):
#   Movie_ID: int
#   Title: string
#   Release_Year: string
#   Num_Reviews: int
#   Avg_Rating: float
#
class MovieRating:
    def __init__(self, movie_id, title, release_year, num_reviews, avg_rating):
        # Store values in private attributes.
        self._movie_id = movie_id
        self._title = title
        self._release_year = release_year
        self._num_reviews = num_reviews
        self._avg_rating = avg_rating

    @property
    def Movie_ID(self):
        return self._movie_id

    @property
    def Title(self):
        return self._title

    @property
    def Release_Year(self):
        return self._release_year

    @property
    def Num_Reviews(self):
        return self._num_reviews

    @property
    def Avg_Rating(self):
        return self._avg_rating

##################################################################
#
# MovieDetails class:
#
# Constructor(...)
# Properties (read-only):
#   Movie_ID: int
#   Title: string
#   Release_Date: string
#   Runtime: int (minutes)
#   Original_Language: string
#   Budget: int (USD)
#   Revenue: int (USD)
#   Num_Reviews: int
#   Avg_Rating: float
#   Tagline: string
#   Genres: list
#   Production_Companies: list
#
class MovieDetails:
    def __init__(self, movie_id, title, release_date, runtime, original_language,
                 budget, revenue, num_reviews, avg_rating, tagline, genres, production_companies):
        # Store detailed movie info in private attributes.
        self._movie_id = movie_id
        self._title = title
        self._release_date = release_date
        self._runtime = runtime
        self._original_language = original_language
        self._budget = budget
        self._revenue = revenue
        self._num_reviews = num_reviews
        self._avg_rating = avg_rating
        self._tagline = tagline
        self._genres = genres
        self._production_companies = production_companies

    @property
    def Movie_ID(self):
        return self._movie_id

    @property
    def Title(self):
        return self._title

    @property
    def Release_Date(self):
        return self._release_date

    @property
    def Runtime(self):
        return self._runtime

    @property
    def Original_Language(self):
        return self._original_language

    @property
    def Budget(self):
        return self._budget

    @property
    def Revenue(self):
        return self._revenue

    @property
    def Num_Reviews(self):
        return self._num_reviews

    @property
    def Avg_Rating(self):
        return self._avg_rating

    @property
    def Tagline(self):
        return self._tagline

    @property
    def Genres(self):
        return self._genres

    @property
    def Production_Companies(self):
        return self._production_companies

##################################################################
#
# num_movies:
#
# Returns: the number of movies in the database, or
#          -1 if an error occurs
#
def num_movies(dbConn):
    # Execute a COUNT query on the Movies table.
    result = datatier.select_one_row(dbConn, "SELECT COUNT(*) FROM Movies")
    if result is None:
        return -1
    return result[0]

##################################################################
#
# num_reviews:
#
# Returns: the number of reviews in the database, or
#          -1 if an error occurs
#
def num_reviews(dbConn):
    # Execute a COUNT query on the Ratings table.
    result = datatier.select_one_row(dbConn, "SELECT COUNT(*) FROM Ratings")
    if result is None:
        return -1
    return result[0]

##################################################################
#
# get_movies:
#
# Finds and returns all movies whose names are "like"
# the pattern. Patterns are based on SQL wildcards (_ and %).
# Pass "%" to get all movies.
#
# Returns: list of Movie objects in ascending order by ID, or
#          an empty list if no data is retrieved or an error occurs.
#
def get_movies(dbConn, pattern):
    # SQL query: extract movie ID, title, and release year from Release_Date.
    sql = ("SELECT Movie_ID, Title, substr(Release_Date, 1, 4) as Release_Year " 
           "FROM Movies WHERE Title LIKE ? ORDER BY Movie_ID ASC")
    rows = datatier.select_n_rows(dbConn, sql, [pattern])
    movies = []
    if rows is None:
        return []
    # Create a Movie object for each row returned.
    for row in rows:
        movie = Movie(row[0], row[1], row[2])
        movies.append(movie)
    return movies

##################################################################
#
# get_movie_details:
#
# Finds and returns detailed information about the given movie.
# The movie ID is passed as a parameter and the function returns
# a MovieDetails object. If no movie is found, returns None.
#
def get_movie_details(dbConn, movie_id):
    # Get basic movie info.
    sql_movie = ("SELECT Movie_ID, Title, Release_Date, Runtime, Original_Language, "
                 "Budget, Revenue FROM Movies WHERE Movie_ID = ?")
    movie_row = datatier.select_one_row(dbConn, sql_movie, [movie_id])
    if movie_row is None or movie_row == ():
        return None
    movie_id_val, title, release_date, runtime, original_language, budget, revenue = movie_row

    # Trim the release date to remove any time component.
    # For example, "1966-09-15 00:00:00.000" becomes "1966-09-15".
    if isinstance(release_date, str) and " " in release_date:
        release_date = release_date.split()[0]

    # Get review statistics.
    sql_reviews = "SELECT COUNT(*), AVG(Rating) FROM Ratings WHERE Movie_ID = ?"
    review_row = datatier.select_one_row(dbConn, sql_reviews, [movie_id])
    if review_row is None:
        num_reviews_val = 0
        avg_rating_val = 0.0
    else:
        num_reviews_val = review_row[0] if review_row[0] is not None else 0
        avg_rating_val = review_row[1] if review_row[1] is not None else 0.0

    # Get tagline.
    sql_tagline = "SELECT Tagline FROM Movie_Taglines WHERE Movie_ID = ?"
    tagline_row = datatier.select_one_row(dbConn, sql_tagline, [movie_id])
    tagline_val = tagline_row[0] if tagline_row and tagline_row != () else ""

    # Get genres.
    sql_genres = ("SELECT G.Genre_Name FROM Movie_Genres MG "
                  "JOIN Genres G ON MG.Genre_ID = G.Genre_ID "
                  "WHERE MG.Movie_ID = ? ORDER BY G.Genre_Name ASC")
    genre_rows = datatier.select_n_rows(dbConn, sql_genres, [movie_id])
    genres = [row[0] for row in genre_rows] if genre_rows is not None else []

    # Get production companies.
    sql_companies = ("SELECT C.Company_Name FROM Movie_Production_Companies MPC "
                     "JOIN Companies C ON MPC.Company_ID = C.Company_ID "
                     "WHERE MPC.Movie_ID = ? ORDER BY C.Company_Name ASC")
    company_rows = datatier.select_n_rows(dbConn, sql_companies, [movie_id])
    production_companies = [row[0] for row in company_rows] if company_rows is not None else []

    # Construct and return a MovieDetails object.
    return MovieDetails(movie_id_val, title, release_date, runtime, original_language,
                        budget, revenue, num_reviews_val, avg_rating_val, tagline_val,
                        genres, production_companies)


##################################################################
#
# get_top_N_movies:
#
# Finds and returns the top N movies based on their average
# rating, where each movie has at least the specified number of reviews.
#
def get_top_N_movies(dbConn, N, min_num_reviews):
    # SQL: join Movies and Ratings, group by movie, and filter by minimum reviews.
    sql = ("""
        SELECT m.Movie_ID, m.Title, substr(m.Release_Date, 1, 4) as Release_Year,
               COUNT(r.Rating) as Num_Reviews, AVG(r.Rating) as Avg_Rating
        FROM Movies m
        JOIN Ratings r ON m.Movie_ID = r.Movie_ID
        GROUP BY m.Movie_ID
        HAVING COUNT(r.Rating) >= ?
        ORDER BY Avg_Rating DESC, m.Title ASC
        LIMIT ?
    """)
    rows = datatier.select_n_rows(dbConn, sql, [min_num_reviews, N])
    movies = []
    if rows is None:
        return []
    # Create a MovieRating object for each row.
    for row in rows:
        movie_rating = MovieRating(row[0], row[1], row[2], row[3], row[4])
        movies.append(movie_rating)
    return movies

##################################################################
#
# add_review:
#
# Inserts the given review (a rating between 0 and 10) into
# the database for the given movie.
#
def add_review(dbConn, movie_id, rating):
    # Verify movie exists.
    sql_check = "SELECT Movie_ID FROM Movies WHERE Movie_ID = ?"
    movie_row = datatier.select_one_row(dbConn, sql_check, [movie_id])
    if movie_row is None or movie_row == ():
        return 0
    # Insert the review.
    sql_insert = "INSERT INTO Ratings (Movie_ID, Rating) VALUES (?, ?)"
    result = datatier.perform_action(dbConn, sql_insert, [movie_id, rating])
    return 1 if result and result > 0 else 0

##################################################################
#
# set_tagline:
#
# Sets (or deletes) the tagline for the given movie.
#
def set_tagline(dbConn, movie_id, tagline):
    # Verify movie exists.
    sql_check = "SELECT Movie_ID FROM Movies WHERE Movie_ID = ?"
    movie_row = datatier.select_one_row(dbConn, sql_check, [movie_id])
    if movie_row is None or movie_row == ():
        return 0
    # Check for an existing tagline.
    sql_existing = "SELECT Tagline FROM Movie_Taglines WHERE Movie_ID = ?"
    existing_row = datatier.select_one_row(dbConn, sql_existing, [movie_id])
    if existing_row and existing_row != ():
        # If a tagline exists, update it if non-empty, or delete if empty.
        if tagline != "":
            sql_update = "UPDATE Movie_Taglines SET Tagline = ? WHERE Movie_ID = ?"
            result = datatier.perform_action(dbConn, sql_update, [tagline, movie_id])
        else:
            sql_delete = "DELETE FROM Movie_Taglines WHERE Movie_ID = ?"
            result = datatier.perform_action(dbConn, sql_delete, [movie_id])
    else:
        # If no tagline exists, insert one if non-empty.
        if tagline != "":
            sql_insert = "INSERT INTO Movie_Taglines (Movie_ID, Tagline) VALUES (?, ?)"
            result = datatier.perform_action(dbConn, sql_insert, [movie_id, tagline])
        else:
            result = 1  # Nothing to do if tagline is empty and none exists.
    return 1 if result and result > 0 else 0
