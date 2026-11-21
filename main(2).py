
import os
import json
import re
import hmac
import hashlib
import secrets
import requests
from datetime import datetime


class MovieRecommendation:

    def __init__(self):

        self.userName = ""
        self.email = ""
        self.currentUserKey = None

        self.moviePreferences = []
        self.movieList = []
        self.movieRating = {}

        self.apiKey = os.getenv("TMDB_API_KEY")
        self.baseURL = "https://api.themoviedb.org/3"

        self.catalogFile = "movie_catalog.json"
        self.usersFile = "users.json"
        self.reviewsFile = "reviews.json"
        self.reviews = self.loadReviews()

        self.movies = self.loadCatalog()
        self.users = self.loadUsers()

        self.genreOptions = {
            1: "Action",
            2: "Adventure",
            3: "Animation",
            4: "Comedy",
            5: "Crime",
            6: "Documentary",
            7: "Drama",
            8: "Family",
            9: "Fantasy",
            10: "Horror",
            11: "Mystery",
            12: "Romance",
            13: "Science Fiction",
            14: "Thriller"
        }

    # -----------------------------------------
    # LOAD AND SAVE MOVIE REVIEWS
    # -----------------------------------------

    def loadReviews(self):

        try:
            with open(self.reviewsFile, "r", encoding="utf-8") as file:
                reviews = json.load(file)

            if isinstance(reviews, list):
                return reviews

            return []

        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def saveReviews(self):

        with open(self.reviewsFile, "w", encoding="utf-8") as file:
            json.dump(self.reviews, file, indent=4)

    # -----------------------------------------
    # LOAD AND SAVE USERS
    # -----------------------------------------

    def loadUsers(self):

        try:
            with open(self.usersFile, "r", encoding="utf-8") as file:
                users = json.load(file)

            if isinstance(users, dict):
                return users

            return {}

        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def saveUsers(self):

        with open(self.usersFile, "w", encoding="utf-8") as file:
            json.dump(self.users, file, indent=4)

    # -----------------------------------------
    # PASSWORD SECURITY
    # -----------------------------------------

    def hashPassword(self, password, salt):

        passwordHash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            200000
        )

        return passwordHash.hex()

    # -----------------------------------------
    # CREATE ACCOUNT
    # -----------------------------------------

    def createAccount(self):

        print("\n========== CREATE ACCOUNT ==========")

        username = input("Create a username: ").strip()
        email = input("Enter your email: ").strip().lower()
        password = input("Create a password: ")

        if not username:
            print("\nUsername cannot be empty.")
            return False

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            print("\nPlease enter a valid email address.")
            return False

        if len(password) < 8:
            print("\nPassword must contain at least 8 characters.")
            return False

        usernameKey = username.lower()

        if usernameKey in self.users:
            print("\nThat username is already registered.")
            return False

        for account in self.users.values():

            if account["email"].lower() == email:
                print("\nThat email is already registered.")
                return False

        salt = secrets.token_hex(16)
        passwordHash = self.hashPassword(password, salt)

        self.users[usernameKey] = {
            "username": username,
            "email": email,
            "salt": salt,
            "password_hash": passwordHash,
            "preferences": [],
            "movie_list": [],
            "ratings": {}
        }

        self.saveUsers()

        print("\nAccount created successfully!")
        print("You can now log in.")

        return True

    # -----------------------------------------
    # LOGIN
    # -----------------------------------------

    def login(self):

        print("\n========== USER LOGIN ==========")

        username = input("Username: ").strip()
        password = input("Password: ")

        usernameKey = username.lower()

        if usernameKey not in self.users:
            print("\nAccount not found.")
            return False

        account = self.users[usernameKey]

        enteredHash = self.hashPassword(
            password,
            account["salt"]
        )

        if not hmac.compare_digest(
            enteredHash,
            account["password_hash"]
        ):
            print("\nIncorrect password.")
            return False

        self.currentUserKey = usernameKey
        self.userName = account["username"]
        self.email = account["email"]

        self.moviePreferences = account.get("preferences", [])
        self.movieList = account.get("movie_list", [])
        self.movieRating = account.get("ratings", {})

        print(f"\nWelcome back, {self.userName}!")

        return True

    # -----------------------------------------
    # SAVE CURRENT USER DATA
    # -----------------------------------------

    def saveUserData(self):

        if self.currentUserKey is None:
            return

        account = self.users[self.currentUserKey]

        account["email"] = self.email
        account["preferences"] = self.moviePreferences
        account["movie_list"] = self.movieList
        account["ratings"] = self.movieRating

        self.saveUsers()

    # -----------------------------------------
    # LOGOUT
    # -----------------------------------------

    def logout(self):

        self.saveUserData()

        print(f"\nGoodbye, {self.userName}!")

        self.userName = ""
        self.email = ""
        self.currentUserKey = None

        self.moviePreferences = []
        self.movieList = []
        self.movieRating = {}
#checked section

    # -----------------------------------------
    # VIEW PROFILE
    # -----------------------------------------

    def viewProfile(self):

        print("\n========== MY PROFILE ==========")

        print("Username:", self.userName)
        print("Email:", self.email)
        print("Preferred Genres:",
              ", ".join(self.moviePreferences) if self.moviePreferences else "None")

        print("Saved Movies:", len(self.movieList))
        print("Rated Movies:", len(self.movieRating))

    # -----------------------------------------
    # UPDATE PROFILE
    # -----------------------------------------

    def updateProfile(self):

        print("\n========== UPDATE PROFILE ==========")
        print("Current email:", self.email)

        newEmail = input(
            "Enter your new email (or press Enter to cancel): "
        ).strip().lower()

        if not newEmail:
            print("\nNo changes made.")
            return

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", newEmail):
            print("\nPlease enter a valid email address.")
            return

        for key, account in self.users.items():

            if key != self.currentUserKey:
                if account["email"].lower() == newEmail:
                    print("\nThat email is already in use.")
                    return

        self.email = newEmail
        self.saveUserData()

        print("\nYour email has been updated!")

    # -----------------------------------------
    # LOAD AND SAVE MOVIE CATALOG
    # -----------------------------------------

    def loadCatalog(self):

        try:
            with open(self.catalogFile, "r", encoding="utf-8") as file:
                return json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def saveCatalog(self):

        with open(self.catalogFile, "w", encoding="utf-8") as file:
            json.dump(self.movies, file, indent=4)

    # -----------------------------------------
    # USERNAME METHODS
    # -----------------------------------------

    def getUserName(self):

        return self.userName

    def setUserName(self, n):

        self.userName = n

    # -----------------------------------------
    # SEARCH TMDB
    # -----------------------------------------

    def searchTMDB(self):

        if not self.apiKey:
            print("\nTMDB API key was not found.")
            return

        searchQuery = input("\nEnter a movie title: ").strip()

        if not searchQuery:
            print("Please enter a movie title.")
            return

        url = f"{self.baseURL}/search/movie"

        parameters = {
            "api_key": self.apiKey,
            "query": searchQuery
        }

        try:
            response = requests.get(
                url,
                params=parameters,
                timeout=15
            )

            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])

            if not results:
                print("\nNo movies found.")
                return

            print("\n========== SEARCH RESULTS ==========")

            for index, movie in enumerate(results[:10], start=1):

                print(f"\n{index}. {movie.get('title', 'Unknown')}")
                print("Release Date:", movie.get("release_date", "Unknown"))
                print("Rating:", movie.get("vote_average", "N/A"))

            choice = input(
                "\nEnter the movie number to import (0 to cancel): "
            )

            if not choice.isdigit():
                print("Invalid selection.")
                return

            choice = int(choice)

            if choice == 0:
                return

            if choice < 1 or choice > min(len(results), 10):
                print("Invalid movie number.")
                return

            tmdbID = results[choice - 1]["id"]

            self.importMovie(tmdbID) ##keep this one in mind it might change next section 

        except requests.RequestException as error:
            print("\nUnable to connect to TMDB.")
            print("Error:", error)

#checked section
            
    # -----------------------------------------
    # GET MOVIE DETAILS
    # -----------------------------------------

    def getDetails(self, tmdbID):

        url = f"{self.baseURL}/movie/{tmdbID}"

        parameters = {
            "api_key": self.apiKey
        }

        response = requests.get(
            url,
            params=parameters,
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    # -----------------------------------------
    # IMPORT MOVIE
    # -----------------------------------------

    def importMovie(self, tmdbID):

        for movie in self.movies:

            if movie["tmdb_id"] == tmdbID:
                print("\nThis movie is already in your catalog.")
                return

        try:
            details = self.getDetails(tmdbID)

            genres = [
                genre["name"]
                for genre in details.get("genres", [])
            ]

            releaseDate = details.get("release_date", "")

            if releaseDate:
                releaseYear = releaseDate[:4]
            else:
                releaseYear = "Unknown"

            movie = {
                "tmdb_id": tmdbID,
                "title": details.get("title", "Unknown"),
                "release_date": releaseDate,
                "year": releaseYear,
                "genres": genres,
                "tmdb_rating": details.get("vote_average", 0),
                "description": details.get(
                    "overview",
                    "No description available."
                ),
                "runtime": details.get("runtime"),
                "poster_path": details.get("poster_path"),
                "user_rating": None
            }

            self.movies.append(movie)
            self.saveCatalog()

            print(f"\n{movie['title']} successfully imported!")

        except requests.RequestException as error:
            print("\nUnable to import movie.")
            print("Error:", error)

    # -----------------------------------------
    # DISPLAY MOVIE
    # -----------------------------------------

    def displayMovie(self, movie):

        print("\nTitle:", movie["title"])
        print("Release Year:", movie["year"])
        print("Genres:", ", ".join(movie["genres"]))
        print("TMDB Rating:", movie["tmdb_rating"])
        print("Runtime:", movie["runtime"], "minutes")
        print("Description:", movie["description"])

        if movie.get("user_rating") is not None:
            print("Your Rating:", movie["user_rating"], "/ 5")

    # -----------------------------------------
    # VIEW MOVIE CATALOG
    # -----------------------------------------

    def viewCatalog(self):

        if not self.movies:
            print("\nYour catalog is empty.")
            return

        print("\n========== MOVIE CATALOG ==========")

        for index, movie in enumerate(self.movies, start=1):
            print(f"\n{index}. {movie['title']}")

    # -----------------------------------------
    # SEARCH EXISTING CATALOG
    # -----------------------------------------

    def searchCatalog(self):

        if not self.movies:
            print("\nYour catalog is empty.")
            return

        searchQuery = input(
            "\nEnter a movie title to search: "
        ).lower()

        foundMovies = [
            movie for movie in self.movies
            if searchQuery in movie["title"].lower()
        ]

        if not foundMovies:
            print("\nNo matching movies found.")
            return

        print("\n========== SEARCH RESULTS ==========")

        for movie in foundMovies:
            self.displayMovie(movie)

    # -----------------------------------------
    # UPDATE MOVIE PREFERENCES
    # -----------------------------------------

    def updatePreferences(self):

        print("\n========== MOVIE GENRES ==========")

        for number, genre in self.genreOptions.items():
            print(f"{number}. {genre}")

        print("\nEnter genre numbers separated by commas.")
        print("Example: 1, 4, 12")

        choices = input("\nYour preferences: ")

        try:
            selectedNumbers = [
                int(number.strip())
                for number in choices.split(",")
            ]

            selectedGenres = []

            for number in selectedNumbers:

                if number in self.genreOptions:
                    selectedGenres.append(self.genreOptions[number])

            self.moviePreferences = list(dict.fromkeys(selectedGenres))

            if self.moviePreferences:
                print("\nYour preferences have been updated!")
                print("Selected genres:",
                      ", ".join(self.moviePreferences))
            else:
                print("\nNo valid genres selected.")

            self.saveUserData()

        except ValueError:
            print("\nPlease enter valid numbers.")

    # -----------------------------------------
    # SAVE MOVIE RATING
    # -----------------------------------------

    def saveRating(self):

        if not self.movies:
            print("\nYour catalog is empty.")
            return

        self.viewCatalog()

        choice = input("\nEnter the movie number to rate: ")

        if not choice.isdigit():
            print("Invalid selection.")
            return

        index = int(choice) - 1

        if index < 0 or index >= len(self.movies):
            print("Invalid movie number.")
            return

        rating = input("Enter your rating (1-5 stars): ")

        if not rating.isdigit():
            print("Please enter a number from 1 to 5.")
            return

        rating = int(rating)

        if rating < 1 or rating > 5:
            print("Rating must be between 1 and 5.")
            return

        movie = self.movies[index]

        self.movieRating[str(movie["tmdb_id"])] = rating

        self.saveUserData()

        print(f"\nYou rated {movie['title']} {rating}/5 stars!")

#CHECKED SECTION #####

    # -----------------------------------------
    # ADD MOVIE TO PERSONAL LIST
    # -----------------------------------------

    def addMovie(self):

        if not self.movies:
            print("\nYour catalog is empty.")
            return

        self.viewCatalog()

        choice = input("\nEnter the movie number to save: ")

        if not choice.isdigit():
            print("Invalid selection.")
            return

        index = int(choice) - 1

        if index < 0 or index >= len(self.movies):
            print("Invalid movie number.")
            return

        movie = self.movies[index]
        tmdbID = movie["tmdb_id"]

        if tmdbID in self.movieList:
            print("\nThis movie is already in your list.")
            return

        self.movieList.append(tmdbID)
        self.saveUserData()

        print(f"\n{movie['title']} added to your movie list!")

    # -----------------------------------------
    # REMOVE MOVIE FROM PERSONAL LIST
    # -----------------------------------------

    def removeMovie(self):

        if not self.movieList:
            print("\nYour movie list is empty.")
            return

        self.viewMovieList()

        choice = input("\nEnter the list number to remove: ")

        if not choice.isdigit():
            print("Invalid selection.")
            return

        index = int(choice) - 1

        if index < 0 or index >= len(self.movieList):
            print("Invalid selection.")
            return

        self.movieList.pop(index)
        self.saveUserData()

        print("\nMovie removed from your list.")

    # -----------------------------------------
    # VIEW PERSONAL MOVIE LIST
    # -----------------------------------------

    def viewMovieList(self):

        if not self.movieList:
            print("\nYour movie list is empty.")
            return

        print("\n========== MY MOVIE LIST ==========")

        for index, tmdbID in enumerate(self.movieList, start=1):

            for movie in self.movies:

                if movie["tmdb_id"] == tmdbID:
                    print(f"{index}. {movie['title']}")
                    break

    # -----------------------------------------
    # GET TMDB GENRE IDs
    # -----------------------------------------

    def getTMDBGenreMap(self):

        if not self.apiKey:
            print("\nTMDB API key was not found.")
            return {}

        url = f"{self.baseURL}/genre/movie/list"

        parameters = {
            "api_key": self.apiKey
        }

        try:
            response = requests.get(
                url,
                params=parameters,
                timeout=15
            )

            response.raise_for_status()

            data = response.json()

            return {
                genre["name"].lower(): genre["id"]
                for genre in data.get("genres", [])
            }

        except (requests.RequestException, ValueError, KeyError) as error:
            print("\nUnable to retrieve TMDB genres.")
            print("Error:", error)
            return {}

    # -----------------------------------------
    # CONVERT TMDB MOVIE INTO LOCAL MOVIE FORMAT
    # -----------------------------------------

    def movieFromTMDBResult(self, result, genreMap):

        genreNames = []

        for genreID in result.get("genre_ids", []):

            for genreName, mappedID in genreMap.items():

                if mappedID == genreID:
                    genreNames.append(genreName.title())
                    break

        releaseDate = result.get("release_date", "")

        if releaseDate:
            releaseYear = releaseDate[:4]
        else:
            releaseYear = "Unknown"

        return {
            "tmdb_id": result["id"],
            "title": result.get("title", "Unknown"),
            "release_date": releaseDate,
            "year": releaseYear,
            "genres": genreNames,
            "tmdb_rating": result.get("vote_average", 0),
            "description": result.get(
                "overview",
                "No description available."
            ),
            "runtime": None,
            "poster_path": result.get("poster_path"),
            "user_rating": None
        }
    
       # -----------------------------------------
    # GET AUTOMATIC MOVIE RECOMMENDATIONS
    # -----------------------------------------

    def getRecommendations(self):

        if not self.moviePreferences:
            print("\nPlease select your movie preferences first.")
            return []

        if not self.apiKey:
            print("\nTMDB API key was not found.")
            return []

        genreMap = self.getTMDBGenreMap()

        if not genreMap:
            return []

        selectedGenreIDs = []

        for genre in self.moviePreferences:

            genreID = genreMap.get(genre.lower())

            if genreID:
                selectedGenreIDs.append(str(genreID))

        if not selectedGenreIDs:
            print("\nNo matching TMDB genres were found.")
            return []

        url = f"{self.baseURL}/discover/movie"

        parameters = {
            "api_key": self.apiKey,
            "with_genres": "|".join(selectedGenreIDs),
            "sort_by": "vote_average.desc",
            "vote_count.gte": 50,
            "include_adult": "false",
            "page": 1
        }

        try:

            response = requests.get(
                url,
                params=parameters,
                timeout=15
            )

            response.raise_for_status()

            data = response.json()

            results = data.get("results", [])

            recommendations = []

            for result in results:

                movieID = result.get("id")

                if not movieID:
                    continue

                existingMovie = None

                for movie in self.movies:

                    if movie.get("tmdb_id") == movieID:
                        existingMovie = movie
                        break

                if existingMovie:

                    recommendations.append(existingMovie)

                else:

                    newMovie = self.movieFromTMDBResult(
                        result,
                        genreMap
                    )

                    self.movies.append(newMovie)
                    recommendations.append(newMovie)

            self.saveCatalog()

            return recommendations[:10]

        except (requests.RequestException, ValueError, KeyError) as error:

            print("\nUnable to retrieve movie recommendations.")
            print("Error:", error)

            return []

    # -----------------------------------------
    # DISPLAY RECOMMENDATIONS
    # -----------------------------------------

    def displayRecommendations(self):

        print("\n========== YOUR RECOMMENDATIONS ==========")

        recommendations = self.getRecommendations()

        if not recommendations:
            print("\nNo matching movies found.")
            print("Try importing more movies or changing your preferences.")
            return

        print(f"\nWe found {len(recommendations)} matching movie(s)!")

        for index, movie in enumerate(recommendations, start=1):

            print(f"\n{index}. {movie['title']}")
            print("Genres:", ", ".join(movie["genres"]))
            print("TMDB Rating:", movie["tmdb_rating"])
            print("Release Year:", movie["year"])
            print("Description:", movie["description"])


    # -----------------------------------------
    # WRITE A MOVIE REVIEW
    # -----------------------------------------

    def writeReview(self):

        if not self.movies:
            print("\nYour movie catalog is empty.")
            return

        self.viewCatalog()

        choice = input("\nEnter the movie number to review: ")

        if not choice.isdigit():
            print("\nInvalid selection.")
            return

        index = int(choice) - 1

        if index < 0 or index >= len(self.movies):
            print("\nInvalid movie number.")
            return

        movie = self.movies[index]

        print(f"\nWriting a review for: {movie['title']}")

        reviewText = input("\nWrite your review: ").strip()

        if not reviewText:
            print("\nYour review cannot be empty.")
            return

        existingReview = None

        for review in self.reviews:

            if (
                review["tmdb_id"] == movie["tmdb_id"]
                and review["username"] == self.userName
            ):
                existingReview = review
                break

        if existingReview:

            existingReview["review"] = reviewText
            existingReview["date"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )

            print("\nYour previous review has been updated!")

        else:

            newReview = {
                "tmdb_id": movie["tmdb_id"],
                "movie_title": movie["title"],
                "username": self.userName,
                "review": reviewText,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

            self.reviews.append(newReview)

            print("\nYour review has been saved!")

        self.saveReviews()

#CHECKED SECTION
        
    # -----------------------------------------
    # VIEW MOVIE REVIEWS
    # -----------------------------------------

    def viewReviews(self):

        if not self.movies:
            print("\nYour movie catalog is empty.")
            return

        self.viewCatalog()

        choice = input("\nEnter the movie number to view reviews: ")

        if not choice.isdigit():
            print("\nInvalid selection.")
            return

        index = int(choice) - 1

        if index < 0 or index >= len(self.movies):
            print("\nInvalid movie number.")
            return

        movie = self.movies[index]

        print("\n========== MOVIE REVIEWS ==========")
        print("Movie:", movie["title"])

        movieReviews = [
            review for review in self.reviews
            if review.get("tmdb_id") == movie.get("tmdb_id")  #changed section from review to review.get
        ]

        if not movieReviews:
            print("\nNo reviews have been written for this movie yet.")
            return

        for number, review in enumerate(movieReviews, start=1):

            print(f"\nReview #{number}")
            print("User:", review["username"])
            print("Date:", review["date"])
            print("Review:", review["review"])
            print("-----------------------------------")

    
    # -----------------------------------------
    # MAIN MENU
    # -----------------------------------------

    def mainMenu(self):

        while self.currentUserKey is not None:

            print("\n========== MAIN MENU ==========")
            print("Logged in as:", self.userName)
            print("--------------------------------")
            print("1. Search and Import Movies from TMDB")
            print("2. View Movie Catalog")
            print("3. Search Existing Catalog")
            print("4. Update Movie Preferences")
            print("5. Rate a Movie")
            print("6. Add Movie to My List")
            print("7. View My Movie List")
            print("8. Remove Movie from My List")
            print("9. Get Movie Recommendations")
            print("10. View My Profile")
            print("11. Update My Profile")
            print("12. Write a Movie Review")
            print("13. View Movie Reviews")
            print("14. Logout")

            choice = input("\nSelect an option: ")

            if choice == "1":
                self.searchTMDB()

            elif choice == "2":
                self.viewCatalog()

            elif choice == "3":
                self.searchCatalog()

            elif choice == "4":
                self.updatePreferences()

            elif choice == "5":
                self.saveRating()

            elif choice == "6":
                self.addMovie()

            elif choice == "7":
                self.viewMovieList()

            elif choice == "8":
                self.removeMovie()

            elif choice == "9":
                self.displayRecommendations()

            elif choice == "10":
                self.viewProfile()

            elif choice == "11":
                self.updateProfile()

            elif choice == "12":
                self.writeReview()

            elif choice == "13":
                self.viewReviews()

            elif choice == "14":
                self.logout()

            else:
                print("\nInvalid option. Please try again.")

    # -----------------------------------------
    # ACCOUNT MENU
    # -----------------------------------------

    def accountMenu(self):

        while True:

            print("\n======================================")
            print("     MOVIE RECOMMENDATION SYSTEM")
            print("======================================")
            print("1. Create Account")
            print("2. Login")
            print("3. Exit")

            choice = input("\nSelect an option: ")

            if choice == "1":
                self.createAccount()

            elif choice == "2":

                if self.login():
                    self.mainMenu()

            elif choice == "3":
                print("\nThank you for using the Movie Recommendation System!")
                break

            else:
                print("\nInvalid option. Please try again.")


# -----------------------------------------
# RUN APPLICATION
# -----------------------------------------

if __name__ == "__main__":

    application = MovieRecommendation()
    application.accountMenu()
