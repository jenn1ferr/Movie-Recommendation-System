# Movie Recommendation System

## Project Overview
The Movie Recommendation System is a Python-based application that helps users discover movies based on their preferred genres. The system integrates with The Movie Database (TMDB) API to retrieve movie information and generate automatic movie recommendations.

## Features
- User account registration and login
- Password hashing for account security
- Movie searching and importing through TMDB
- Genre-based automatic movie recommendations
- Movie ratings
- Personal movie lists
- Movie reviews
- User profile management
- JSON-based data storage

## Technologies Used
- Python 3.13
- Python IDLE
- TMDB API
- Requests library
- JSON

## Requirements
- Python 3.13
- Requests library
- TMDB API key

## Setup Instructions
1. Install Python 3.13.
2. Install the Requests library using `py -3.13 -m pip install requests`.
3. Obtain a TMDB API key.
4. Set the API key as a Windows environment variable named `TMDB_API_KEY`.
5. Open the Python source file in IDLE.
6. Run the program.

## Movie Recommendations
The system uses the user's selected movie genres to retrieve matching movies from TMDB. Recommendations are sorted by TMDB user ratings and display movie titles, genres, release years, ratings, and descriptions.

## Data Storage
The application uses JSON files to store user accounts, movie catalog information, and movie reviews.

## Attribution
This product uses the TMDB API but is not endorsed or certified by TMDB.
