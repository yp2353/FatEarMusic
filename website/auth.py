######### TEAMMATE'S WORK ######

import pymysql
import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user, LoginManager, UserMixin

auth = Blueprint('auth', __name__)

# config the database
conn = pymysql.Connect(
    host="localhost",
    port=8889,
    user="root",
    password="root",
    db="FatEar",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)

# define login_manager to manager user authentication
login_manager = LoginManager()


# define your User class
class User(UserMixin):
    def __init__(self, username):
        self.id = username

    def __repr__(self):
        return f'<User {self.id}>'


@login_manager.user_loader
def load_user(user_id):
    # return an instance of the User class for the given user_id
    return User(user_id)


#Log in
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # get a post request
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # cursor used to send queries
        cursor = conn.cursor()
        # select the username
        query = 'SELECT username, pwd FROM user WHERE username = %s'
        cursor.execute(query, (username))
        # stores the results in a variable
        data = cursor.fetchone()

        if data:
            if check_password_hash(data['pwd'], password):
                flash('Logged in successfully!', category='success')
                # track who is logging in now
                session['username'] = username
                cursor.close()

                # member the user
                user = User(username)
                login_user(user, remember=True)

                return redirect(url_for('views.home'))

            else:
                flash('Invalid password, try again!', category='error')
        else:
            flash('Username does not exist!', category='error')
    return render_template("login.html", user=current_user)


# log out
@auth.route('/logout')
@login_required
def logout():
    username = current_user.id
    cursor = conn.cursor()
    # update the last-time-login in database
    # so feed shows new content from the time you logged out to now
    now = datetime.datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    query = 'UPDATE user SET lastlogin = %s WHERE user.username = %s'
    cursor.execute(query, (formatted_date, username))
    conn.commit()
    cursor.close()
    flash('Logged out successfully!')
    # pop the user in session
    session.pop('user_id', None)
    # logout
    logout_user()
    return redirect(url_for('views.home'))


# sign up
@auth.route('/sign-up', methods=['GET', 'POST'])
def signup():
    # get a post request
    if request.method == 'POST':
        # get all the info of the new user
        username = request.form.get('username')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        nickname = request.form.get('nickname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # check if input is valid
        if (len(username) < 2) or ((len(username) > 10)):
            flash('Username must be 2-10 characters long.', category='error')
        elif (len(firstName) < 1) or ((len(firstName) > 20)):
            flash('First name must be 1-20 characters long.', category='error')
        elif (len(lastName) < 1) or ((len(lastName) > 20)):
            flash('Last name must be 1-20 characters long.', category='error')
        elif len(password1) <= 4:
            flash('Password must be greater than 4 characters.', category='error')
        elif password1 != password2:
            flash('Passwords do not match!', category='error')
        elif (len(nickname) < 1) or ((len(nickname) > 20)):
            flash('Nickname must be 1-20 characters long.', category='error')
        else:
            # cursor used to send queries
            cursor = conn.cursor()
            # select the username
            query = 'SELECT * FROM user WHERE username = %s'
            cursor.execute(query, (username))
            # stores the results in a variable
            data = cursor.fetchone()
            if data:
                flash('Username already exists! Try again!', category='error')
                return render_template("sign_up.html")
            else:
                # hash the password with sha256
                password = generate_password_hash(password1, method='sha256')
                session['username'] = username

                # the current day is the last time login for new user
                now = datetime.datetime.now()
                formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

                # add user to database
                ins = 'INSERT INTO user VALUES(%s, %s, %s, %s, %s, %s)'
                cursor.execute(ins, (username, password, firstName, lastName, formatted_date, nickname))
                conn.commit()
                cursor.close()

                # member the user
                user = User(username)
                login_user(user, remember=True)

                # flash successful message
                flash('Account created!', category='success')
                return redirect(url_for('views.home'))
    return render_template("sign_up.html", user=current_user)


######### END OF TEAMMATE'S WORK ######

######### START OF MY WORK ######


#Playlist.html
@auth.route('/playlist', methods=['POST', 'GET'])
@login_required
def playlist():
    username = current_user.id

    if request.method == 'POST':
        #Delete a whole playlist
        cursor = conn.cursor()
        playlist_id = request.form.get('playlist_id')
        query = 'DELETE FROM playlist WHERE listID = %s'
        cursor.execute(query, (playlist_id))
        conn.commit()

        flash('Successfully deleted playlist!', category='success')

        cursor.close()

    cursor = conn.cursor()

    query = "SELECT playlist.listID, playlist.listName, playlist.playlistDescription, COUNT(songInPlaylist.songID) AS count " \
        "FROM playlist LEFT JOIN songInPlaylist ON playlist.listID = songInPlaylist.listID " \
        "WHERE playlist.createdBy = %s " \
        "GROUP BY playlist.listID, playlist.listName, playlist.playlistDescription ORDER BY playlist.createdAt DESC"
    cursor.execute(query, (username))
    my_playlists = cursor.fetchall()

    return render_template('playlist.html', user=current_user, playlists=my_playlists)


#Playlist.html -> "+" button
@auth.route('/createplaylist', methods=['POST', 'GET'])
@login_required
def createplaylist():
    # get a post request
    if request.method == 'POST':
        username = current_user.id
        # get all the info of the new user
        playlistname = request.form.get('playlistname')
        playlistdescription = request.form.get('playlistdescription')

        # check if input is valid
        if (len(playlistname) < 1) or (len(playlistname) > 50):
            flash('Playlist name must be 1-50 characters long.', category='error')
        elif len(playlistdescription) > 100:
            flash('Description too long. Under 100 characters.', category='error')
        else:
            # cursor used to send queries
            cursor = conn.cursor()
            # select the username
            query = 'SELECT * FROM playlist WHERE createdBy = %s && listName = %s'
            cursor.execute(query, (username, playlistname))
            # stores the results in a variable
            data = cursor.fetchone()
            if data:
                flash('You already have a playlist with this name! Try again!', category='error')
                return render_template("createplaylist.html", user=current_user)
            else:
                checkempty = 'SELECT * FROM playlist'
                cursor.execute(checkempty)
                empt = len(cursor.fetchall())
                if empt == 0:
                    listID = 0
                else:
                    checkmax = 'SELECT MAX(listID) FROM playlist'
                    cursor.execute(checkmax)
                    maxPlaylistId = cursor.fetchone()
                    max = maxPlaylistId['MAX(listID)']
                    listID = int(max) + 1
                
                now = datetime.datetime.now()
                formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

                if len(playlistdescription) == 0:
                    # add new playlist to database with playlistdescription set to NULL
                    ins = 'INSERT INTO playlist VALUES(%s, %s, %s, %s, NULL)'
                    cursor.execute(ins, (listID, playlistname, formatted_date, current_user.id))
                    conn.commit()
                else:
                    # add new playlist to database
                    ins = 'INSERT INTO playlist VALUES(%s, %s, %s, %s, %s)'
                    cursor.execute(ins, (listID, playlistname, formatted_date, current_user.id, playlistdescription))
                    conn.commit()
                
                cursor.close()
                flash('Successfully created new playlist!', category='success')
                return render_template('playlistpage.html', user=current_user, playlist_name = playlistname, playlist_id = listID, playlist_description = playlistdescription)
    return render_template('createplaylist.html', user=current_user)


@auth.route('/playlistpage', methods=['POST', 'GET'])
def playlistpage():
    if request.method == 'POST':
        post_id = request.form['post_id']
        if post_id == '1':
            #Search song button
            cursor = conn.cursor()
            playlist_id = request.form.get('playlist_id')

            #Get name and description from ID
            query = "SELECT listName, playlistDescription FROM playlist WHERE listID = %s"
            cursor.execute(query, (playlist_id))
            listName_and_playlistDescription = cursor.fetchone()
            playlist_name = listName_and_playlistDescription['listName']
            playlist_description = listName_and_playlistDescription['playlistDescription']

            song_title = request.form.get('title')

            #To list all songs in current playlist:
                #LEFT JOIN so songs with no album or genre or rating will still show up
                #GROUP_CONCAT so multiple artists that performed the same song, multiple albums of the same song,
                #and multiple genres of the same song will be in the same row
            query = "SELECT song.title, song.songID, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "JOIN songInPlaylist ON song.songID = songInPlaylist.songID " \
                        "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                        "WHERE songInPlaylist.listID = %s " \
                        "GROUP BY song.title, song.songID"
            
            cursor.execute(query, (playlist_id))
            song_in_playlist = cursor.fetchall()

            if not song_title:
                flash('Song title cannot be blank!', category='error')
                if(playlist_description == None):
                    return render_template('playlistpage.html', user=current_user, playlist_name = playlist_name, playlist_id = playlist_id, song_in_playlist = song_in_playlist) 
                else:
                    return render_template('playlistpage.html', user=current_user, playlist_name = playlist_name, playlist_id = playlist_id, playlist_description = playlist_description, song_in_playlist = song_in_playlist) 


            #Search for songs:
                #would not show songs already in current playlist
                #LEFT JOIN so songs with no album or genre or rating will still show up
                #GROUP_CONCAT so multiple artists that performed the same song, multiple albums of the same song,
                #and multiple genres of the same song will be in the same row
            query = "SELECT song.title, song.songID, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                        "WHERE song.title = %s AND (song.songID, %s) NOT IN " \
                        "(SELECT songID, listID FROM songInPlaylist) " \
                        "GROUP BY song.title, song.songID"
            
            cursor.execute(query, (song_title, playlist_id))
            songs = cursor.fetchall()
            cursor.close()

            if songs:
                #Dont display playlist_description if empty
                if(playlist_description == None):
                    return render_template('playlistpage.html', user=current_user, playlist_name = playlist_name, playlist_id = playlist_id, song_in_playlist = song_in_playlist, songs = songs)
                else:
                    return render_template('playlistpage.html', user=current_user, playlist_name = playlist_name, playlist_id = playlist_id, playlist_description = playlist_description, song_in_playlist = song_in_playlist, songs = songs)
            else:
                flash('No songs found! Please change the title!', category='error')
                if(playlist_description == None):
                    return render_template('playlistpage.html', user=current_user, playlist_name = playlist_name, playlist_id = playlist_id, song_in_playlist = song_in_playlist) 
                else:
                    return render_template('playlistpage.html', user=current_user, playlist_name = playlist_name, playlist_id = playlist_id, playlist_description = playlist_description, song_in_playlist = song_in_playlist) 
            
        elif post_id == '2':
            #Add song to playlist button
            cursor = conn.cursor()
            playlist_id = request.form.get('playlist_id')

            #Get name and description from ID
            query = "SELECT listName, playlistDescription FROM playlist WHERE listID = %s"
            cursor.execute(query, (playlist_id))
            listName_and_playlistDescription = cursor.fetchone()
            playlist_name = listName_and_playlistDescription['listName']
            playlist_description = listName_and_playlistDescription['playlistDescription']

            song_id = request.form.get('song_id')

            query = 'INSERT INTO songInPlaylist (listID, songID) VALUES(%s, %s)'
            cursor.execute(query, (playlist_id, song_id))
            conn.commit()

            flash('Successfully added to playlist!', category='success')
            
            #To list all songs in current playlist:
                #LEFT JOIN so songs with no album or genre or rating will still show up
                #GROUP_CONCAT so multiple artists that performed the same song, multiple albums of the same song,
                #and multiple genres of the same song will be in the same row
            query = "SELECT song.title, song.songID, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "JOIN songInPlaylist ON song.songID = songInPlaylist.songID " \
                        "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                        "WHERE songInPlaylist.listID = %s " \
                        "GROUP BY song.title, song.songID"

            cursor.execute(query, (playlist_id))
            song_in_playlist = cursor.fetchall()

            cursor.close()
            
            if(playlist_description == None):
                return render_template('playlistpage.html', user=current_user, playlist_name = playlist_name, playlist_id = playlist_id, song_in_playlist = song_in_playlist) 
            else:
                return render_template('playlistpage.html', user=current_user, playlist_name = playlist_name, playlist_id = playlist_id,  playlist_description = playlist_description, song_in_playlist = song_in_playlist) 
        
        elif post_id == '3':
            #Navigating to playlistpage from playlist
            cursor = conn.cursor()
            playlist_id = request.form.get('playlist_id')

            #Get name and description from ID
            query = "SELECT listName, playlistDescription FROM playlist WHERE listID = %s"
            cursor.execute(query, (playlist_id))
            listName_and_playlistDescription = cursor.fetchone()
            playlist_name = listName_and_playlistDescription['listName']
            playlist_description = listName_and_playlistDescription['playlistDescription']

            #To list all songs in current playlist:
                #LEFT JOIN so songs with no album or genre or rating will still show up
                #GROUP_CONCAT so multiple artists that performed the same song, multiple albums of the same song,
                #and multiple genres of the same song will be in the same row
            query = "SELECT song.title, song.songID, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "JOIN songInPlaylist ON song.songID = songInPlaylist.songID " \
                        "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                        "WHERE songInPlaylist.listID = %s " \
                        "GROUP BY song.title, song.songID"
            cursor.execute(query, (playlist_id))
            song_in_playlist = cursor.fetchall()

            cursor.close()

            if(playlist_description == None):
                return render_template('playlistpage.html', user=current_user, playlist_name = playlist_name, playlist_id = playlist_id, song_in_playlist = song_in_playlist)
            else:
                return render_template('playlistpage.html', user=current_user, playlist_name = playlist_name, playlist_id = playlist_id, playlist_description = playlist_description, song_in_playlist = song_in_playlist)

        elif post_id == '4':
            #Delete a song in a playlist 
            cursor = conn.cursor()
            playlist_id = request.form.get('playlist_id')

            #Get name and description from ID
            query = "SELECT listName, playlistDescription FROM playlist WHERE listID = %s"
            cursor.execute(query, (playlist_id))
            listName_and_playlistDescription = cursor.fetchone()
            playlist_name = listName_and_playlistDescription['listName']
            playlist_description = listName_and_playlistDescription['playlistDescription']

            song_id = request.form.get('song_id')

            query = 'DELETE FROM songInPlaylist WHERE listID = %s AND songID = %s'
            cursor.execute(query, (playlist_id, song_id))
            conn.commit()

            flash('Successfully deleted from playlist!', category='success')
            
            #To list all songs in current playlist:
                #LEFT JOIN so songs with no album or genre or rating will still show up
                #GROUP_CONCAT so multiple artists that performed the same song, multiple albums of the same song,
                #and multiple genres of the same song will be in the same row
            query = "SELECT song.title, song.songID, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "JOIN songInPlaylist ON song.songID = songInPlaylist.songID " \
                        "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                        "WHERE songInPlaylist.listID = %s " \
                        "GROUP BY song.title, song.songID"
            cursor.execute(query, (playlist_id))
            song_in_playlist = cursor.fetchall()

            cursor.close()
            
            if(playlist_description == None):
                return render_template('playlistpage.html', user=current_user, playlist_name = playlist_name, playlist_id = playlist_id, song_in_playlist = song_in_playlist) 
            else:
                return render_template('playlistpage.html', user=current_user, playlist_name = playlist_name, playlist_id = playlist_id,  playlist_description = playlist_description, song_in_playlist = song_in_playlist) 
        
        elif post_id == '5':
            #Got to playlist page from searchall.html

            cursor = conn.cursor()
            playlist_id = request.form.get('playlist_id')

            #Get name and description from ID
            query = "SELECT listName, playlistDescription FROM playlist WHERE listID = %s"
            cursor.execute(query, (playlist_id))
            listName_and_playlistDescription = cursor.fetchone()
            playlist_name = listName_and_playlistDescription['listName']
            playlist_description = listName_and_playlistDescription['playlistDescription']

            #To list all songs in current playlist:
                #LEFT JOIN so songs with no album or genre or rating will still show up
                #GROUP_CONCAT so multiple artists that performed the same song, multiple albums of the same song,
                #and multiple genres of the same song will be in the same row
            query = "SELECT song.title, song.songID, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "JOIN songInPlaylist ON song.songID = songInPlaylist.songID " \
                        "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                        "WHERE songInPlaylist.listID = %s " \
                        "GROUP BY song.title, song.songID"
            cursor.execute(query, (playlist_id))
            song_in_playlist = cursor.fetchall()

            #Needs to check if current user viewing this playlistpage is the same person who created it!
            query = "SELECT createdBy FROM playlist WHERE listID = %s"
            cursor.execute(query, (playlist_id))
            playlistCreator = cursor.fetchone()
            playlistCreatorName = playlistCreator['createdBy']
            cursor.close()

            #Set myself as userid or none if not logged in
            try:
                myself = current_user.id
            except AttributeError:
                myself = None

            if(playlist_description == None):
                if playlistCreatorName == myself:
                    #Viewing a playlist page created by themselves
                    return render_template('playlistpage.html', user=current_user, playlist_name = playlist_name, playlist_id = playlist_id, song_in_playlist = song_in_playlist)
                else:
                    #Not created by themselves
                    return render_template('playlistpage.html', user=current_user, playlist_name = playlist_name, playlist_id = playlist_id, song_in_playlist = song_in_playlist, viewOnly = 1)
            else:
                if playlistCreatorName == myself:
                    return render_template('playlistpage.html', user=current_user, playlist_name = playlist_name, playlist_id = playlist_id, playlist_description = playlist_description, song_in_playlist = song_in_playlist)
                else:
                    return render_template('playlistpage.html', user=current_user, playlist_name = playlist_name, playlist_id = playlist_id, playlist_description = playlist_description, song_in_playlist = song_in_playlist, viewOnly = 1)
                

# float function for /Home. Checks if input is a number or not
def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

# Discover songs
@auth.route('/', methods=['GET', 'POST'])
def searchSong():
    if request.method == 'POST':
        genre = request.form.get('genre')
        avgRating = request.form.get('avgRating')
        artistName = request.form.get('artistName')

        #avgRating needs to be between 0 and 5
        if avgRating and (is_float(avgRating) == False):
            flash('Enter rating between 0 and 5', category='error')
            return render_template("home.html", user=current_user)     
        if avgRating and (float(avgRating) > 5.0 or float(avgRating) < 0):
            flash('Enter rating between 0 and 5', category='error')
            return render_template("home.html", user=current_user)
        
        # cursor used to send queries
        cursor = conn.cursor()

        # check if all exists and valid type

        if genre and not avgRating and not artistName:  # only genre
            #LEFT JOIN so songs with no album or genre or rating will still show up
            #GROUP_CONCAT so multiple artists that performed the same song, multiple albums of the same song,
            #and multiple genres of the same song will be in the same row
            query = "SELECT song.title, song.songID, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                        "WHERE songGenre.genre = %s " \
                        "GROUP BY song.title, song.songID"
            cursor.execute(query, (genre))

            #Fetch data and show search results
            songs = cursor.fetchall()
            if songs:
                return render_template("home.html", user=current_user, songs=songs, genre=genre)
            else:
                flash('No songs found, please try again!', category='error')
                return redirect(url_for('views.home'))
        
        elif not genre and avgRating and not artistName:  # only avgRating
            #If input avgRating is 0, it's treated as if it wasnt entered and all songs are shown
            if float(avgRating) == 0:
                query = "SELECT song.title, song.songID, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                        "GROUP BY song.title, song.songID"
                cursor.execute(query)

            else:
                query = "SELECT song.title, song.songID, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                            "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                            "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                            "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                            "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                            "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                            "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                            "GROUP BY song.title, song.songID " \
                            "HAVING AVG(rate.stars) >= %s"
                cursor.execute(query, (avgRating))
            
            #Fetch data and show search results
            songs = cursor.fetchall()
            if songs:
                return render_template("home.html", user=current_user, songs=songs, avgRating=avgRating)
            else:
                flash('No songs found, please try again!', category='error')
                return redirect(url_for('views.home'))
            
        
        elif not genre and not avgRating and artistName:  # only artistName
            query = "SELECT song.title, song.songID, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                        "GROUP BY song.title, song.songID " \
                        "HAVING artists LIKE %s "
            artistName_as_parameter = "%" + artistName + "%"
            cursor.execute(query, (artistName_as_parameter))

            #Fetch data and show search results
            songs = cursor.fetchall()
            if songs:
                return render_template("home.html", user=current_user, songs=songs, artistName=artistName)
            else:
                flash('No songs found, please try again!', category='error')
                return redirect(url_for('views.home'))


        elif genre and avgRating and not artistName:  # genre + avgRating
            #If input avgRating is 0, it's treated as if it wasnt entered and all songs matching genre are shown
            if float(avgRating) == 0:
                query = "SELECT song.title, song.songID, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                        "WHERE songGenre.genre = %s " \
                        "GROUP BY song.title, song.songID"
                cursor.execute(query, (genre))
                
            else:
                query = "SELECT song.title, song.songID, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                            "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                            "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                            "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                            "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                            "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                            "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                            "WHERE songGenre.genre = %s " \
                            "GROUP BY song.title, song.songID " \
                            "HAVING AVG(rate.stars) >= %s"
                cursor.execute(query, (genre, avgRating))
            
            #Fetch data and show search results
            songs = cursor.fetchall()
            if songs:
                return render_template("home.html", user=current_user, songs=songs, genre=genre, avgRating=avgRating)
            else:
                flash('No songs found, please try again!', category='error')
                return redirect(url_for('views.home'))
            

        elif genre and not avgRating and artistName:  # genre + artistName
            query = "SELECT song.title, song.songID, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                        "WHERE songGenre.genre = %s " \
                        "GROUP BY song.title, song.songID " \
                        "HAVING artists LIKE %s "
            artistName_as_parameter = "%" + artistName + "%"
            cursor.execute(query, (genre, artistName_as_parameter))
        
        #Fetch data and show search results
            songs = cursor.fetchall()
            if songs:
                return render_template("home.html", user=current_user, songs=songs, genre=genre, artistName=artistName)
            else:
                flash('No songs found, please try again!', category='error')
                return redirect(url_for('views.home'))

        

        elif not genre and avgRating and artistName:  # avgRating + artistName
            #If input avgRating is 0, it's treated as if it wasnt entered and all songs matching artistName are shown
            if float(avgRating) == 0:
                query = "SELECT song.title, song.songID, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                        "GROUP BY song.title, song.songID " \
                        "HAVING artists LIKE %s "
                artistName_as_parameter = "%" + artistName + "%"
                cursor.execute(query, (artistName_as_parameter))

            else:
                query = "SELECT song.title, song.songID, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                        "GROUP BY song.title, song.songID " \
                        "HAVING AVG(rate.stars) >= %s AND artists LIKE %s "
                artistName_as_parameter = "%" + artistName + "%"
                cursor.execute(query, (avgRating, artistName_as_parameter))
            
            #Fetch data and show search results
            songs = cursor.fetchall()
            if songs:
                return render_template("home.html", user=current_user, songs=songs, avgRating=avgRating, artistName=artistName)
            else:
                flash('No songs found, please try again!', category='error')
                return redirect(url_for('views.home'))

        

        elif genre and avgRating and artistName:  # genre + avgRating + artistName
            query = "SELECT song.title, song.songID, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                        "WHERE songGenre.genre = %s " \
                        "GROUP BY song.title, song.songID " \
                        "HAVING AVG(rate.stars) >= %s AND artists LIKE %s"
            artistName_as_parameter = "%" + artistName + "%"
            cursor.execute(query, (genre, avgRating, artistName_as_parameter))

            #Fetch data and show search results
            songs = cursor.fetchall()
            if songs:
                return render_template("home.html", user=current_user, songs=songs, genre=genre, avgRating=avgRating, artistName=artistName)
            else:
                flash('No songs found, please try again!', category='error')
                return redirect(url_for('views.home'))


        else:
            #no genre + no avgRating + no artistName
            flash("Enter genre, rating, and/or name to search", category='error')
            return render_template("home.html", user=current_user)

    return render_template("home.html", user=current_user)



#specific song's page
@auth.route('/songpage', methods=['GET', 'POST'])
def songpage():
    if request.method == 'POST':
        post_id = request.form['post_id']
        if post_id == '1':
            #Here from discover or search or userprofile or playlistpage or feed

            song_id = request.form.get('song_id')
            cursor = conn.cursor()

            query = "SELECT song.title, song.songID, song.releaseDate, song.songURL, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                            "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                            "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                            "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                            "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                            "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                            "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                            "GROUP BY song.title, song.songID, song.releaseDate, song.songURL " \
                            "HAVING song.songID = %s"
            cursor.execute(query, (song_id))
            songs = cursor.fetchone()

            query = "SELECT username, stars, ratingDate FROM rateSong WHERE songID = %s ORDER BY ratingDate DESC"
            cursor.execute(query, (song_id))
            ratings = cursor.fetchall()

            query = "SELECT username, reviewText, reviewDate FROM reviewSong WHERE songID = %s ORDER BY reviewDate DESC"
            cursor.execute(query, (song_id))
            reviews = cursor.fetchall()

            cursor.close()

            if ratings and reviews:
                return render_template("songpage.html", user=current_user, songs=songs, ratings=ratings, reviews=reviews)
            elif ratings:
                return render_template("songpage.html", user=current_user, songs=songs, ratings=ratings)
            elif reviews:
                return render_template("songpage.html", user=current_user, songs=songs, reviews=reviews)
            else:
                return render_template("songpage.html", user=current_user, songs=songs)
        
        elif post_id == '2':
            #Here from submitting a rating

            song_id = request.form.get('song_id')
            star = request.form.get('rating_stars')
            cursor = conn.cursor()
            now = datetime.datetime.now()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

            #check if user already posted a rating for this song
            query = "SELECT * FROM rateSong WHERE username = %s AND songid = %s"
            cursor.execute(query, (current_user.id, song_id))
            rate = cursor.fetchone()
            if rate:
                flash('Your previous rating was overwritten.', category="warning")
                query = "UPDATE rateSong SET stars= %s, ratingDate= %s WHERE username = %s AND songID = %s"
                cursor.execute(query, (star, formatted_date, current_user.id, song_id))
                conn.commit()
            else:
                flash('Rating successfully added!', category='success')
                query = "INSERT INTO rateSong(username, songID, stars, ratingDate) VALUES (%s,%s,%s,%s)"
                cursor.execute(query, (current_user.id, song_id, star, formatted_date))
                conn.commit()
            
            #query to show all ratings and reviews of this song
            query = "SELECT song.title, song.songID, song.releaseDate, song.songURL, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                            "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                            "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                            "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                            "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                            "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                            "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                            "GROUP BY song.title, song.songID, song.releaseDate, song.songURL " \
                            "HAVING song.songID = %s"
            cursor.execute(query, (song_id))
            songs = cursor.fetchone()

            query = "SELECT username, stars, ratingDate FROM rateSong WHERE songID = %s ORDER BY ratingDate DESC"
            cursor.execute(query, (song_id))
            ratings = cursor.fetchall()

            query = "SELECT username, reviewText, reviewDate FROM reviewSong WHERE songID = %s ORDER BY reviewDate DESC"
            cursor.execute(query, (song_id))
            reviews = cursor.fetchall()

            cursor.close()

            if ratings and reviews:
                return render_template("songpage.html", user=current_user, songs=songs, ratings=ratings, reviews=reviews)
            elif ratings:
                return render_template("songpage.html", user=current_user, songs=songs, ratings=ratings)
            elif reviews:
                return render_template("songpage.html", user=current_user, songs=songs, reviews=reviews)
            else:
                return render_template("songpage.html", user=current_user, songs=songs)
        

        elif post_id == '3':
            #Here from submitting a review

            song_id = request.form.get('song_id')
            review_text = request.form.get('review_text')
            cursor = conn.cursor()
            now = datetime.datetime.now()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

            #query to show all ratings and reviews of this song
            query = "SELECT song.title, song.songID, song.releaseDate, song.songURL, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                            "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                            "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                            "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                            "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                            "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                            "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                            "GROUP BY song.title, song.songID, song.releaseDate, song.songURL " \
                            "HAVING song.songID = %s"
            cursor.execute(query, (song_id))
            songs = cursor.fetchone()

            query = "SELECT username, stars, ratingDate FROM rateSong WHERE songID = %s ORDER BY ratingDate DESC"
            cursor.execute(query, (song_id))
            ratings = cursor.fetchall()

            query = "SELECT username, reviewText, reviewDate FROM reviewSong WHERE songID = %s ORDER BY reviewDate DESC"
            cursor.execute(query, (song_id))
            reviews = cursor.fetchall()

            if not review_text:
                flash('Review cannot be empty!', category='error')
                if ratings and reviews:
                    return render_template("songpage.html", user=current_user, songs=songs, ratings=ratings, reviews=reviews)
                elif ratings:
                    return render_template("songpage.html", user=current_user, songs=songs, ratings=ratings)
                elif reviews:
                    return render_template("songpage.html", user=current_user, songs=songs, reviews=reviews)
                else:
                    return render_template("songpage.html", user=current_user, songs=songs)

            if len(review_text) > 100:
                flash('Review too long. Under 100 characters.', category='error')
                if ratings and reviews:
                    return render_template("songpage.html", user=current_user, songs=songs, ratings=ratings, reviews=reviews)
                elif ratings:
                    return render_template("songpage.html", user=current_user, songs=songs, ratings=ratings)
                elif reviews:
                    return render_template("songpage.html", user=current_user, songs=songs, reviews=reviews)
                else:
                    return render_template("songpage.html", user=current_user, songs=songs)
            
            #check if user already posted a review for this song
            query = "SELECT * FROM reviewSong WHERE username = %s AND songid = %s"
            cursor.execute(query, (current_user.id, song_id))
            checkreview = cursor.fetchone()
            if checkreview:
                flash('Your previous review was overwritten.', category="warning")
                query = "UPDATE reviewSong SET reviewText= %s, reviewDate= %s WHERE username = %s AND songID = %s"
                cursor.execute(query, (review_text, formatted_date, current_user.id, song_id))
                conn.commit()
            else:
                flash('Review successfully added!', category='success')
                query = "INSERT INTO reviewSong(username, songID, reviewText, reviewDate) VALUES (%s,%s,%s,%s)"
                cursor.execute(query, (current_user.id, song_id, review_text, formatted_date))
                conn.commit()
            
            #Need to do this again to update the new review!
            #query to show all ratings and reviews of this song
            query = "SELECT song.title, song.songID, song.releaseDate, song.songURL, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                            "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                            "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                            "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                            "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                            "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                            "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                            "GROUP BY song.title, song.songID, song.releaseDate, song.songURL " \
                            "HAVING song.songID = %s"
            cursor.execute(query, (song_id))
            songs = cursor.fetchone()

            query = "SELECT username, stars, ratingDate FROM rateSong WHERE songID = %s ORDER BY ratingDate DESC"
            cursor.execute(query, (song_id))
            ratings = cursor.fetchall()

            query = "SELECT username, reviewText, reviewDate FROM reviewSong WHERE songID = %s ORDER BY reviewDate DESC"
            cursor.execute(query, (song_id))
            reviews = cursor.fetchall()
            
            cursor.close()

            if ratings and reviews:
                return render_template("songpage.html", user=current_user, songs=songs, ratings=ratings, reviews=reviews)
            elif ratings:
                return render_template("songpage.html", user=current_user, songs=songs, ratings=ratings)
            elif reviews:
                return render_template("songpage.html", user=current_user, songs=songs, reviews=reviews)
            else:
                return render_template("songpage.html", user=current_user, songs=songs)



# Search songs, artists, playlists, users
@auth.route('/searchall', methods=['GET', 'POST'])
def searchAll():

    if request.method == 'POST':
        post_id = request.form['post_id']
        if post_id == '1':
            searchTitle = request.form.get('searchTitle')
            cursor = conn.cursor()
            searchTitleParameter = "%" + searchTitle + "%"

            #Search for songs:
                #LEFT JOIN so songs with no album or genre or rating will still show up
                #GROUP_CONCAT so multiple artists that performed the same song, multiple albums of the same song,
                #and multiple genres of the same song will be in the same row
            query = "SELECT song.title, song.songID, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                        "WHERE song.title LIKE %s " \
                        "GROUP BY song.title, song.songID"
            cursor.execute(query, (searchTitleParameter))
            songs = cursor.fetchall()

            #Search for artists
            query = "SELECT * FROM artist WHERE fname LIKE %s OR lname LIKE %s"
            cursor.execute(query, (searchTitleParameter, searchTitleParameter))
            artists = cursor.fetchall()

            #Search for playlists
            query = "SELECT playlist.listID, playlist.listName, playlist.playlistDescription, COUNT(songInPlaylist.songID) AS count, playlist.createdAt, playlist.createdBy " \
                "FROM playlist LEFT JOIN songInPlaylist ON playlist.listID = songInPlaylist.listID " \
                "WHERE playlist.listName LIKE %s " \
                "GROUP BY playlist.listID, playlist.listName, playlist.playlistDescription, playlist.createdAt, playlist.createdBy ORDER BY playlist.createdAt DESC"
            cursor.execute(query, (searchTitleParameter))
            playlists = cursor.fetchall()

            #Search for users
            query = "SELECT username, fname, lname, lastlogin, nickname FROM user WHERE username LIKE %s"
            cursor.execute(query, (searchTitleParameter))
            usernames = cursor.fetchall()

            cursor.close()

            return render_template("searchall.html", user=current_user, searchTitle=searchTitle, songs=songs, artists=artists, playlists=playlists, usernames=usernames)


    return render_template("searchall.html", user=current_user)


# User profile page
@auth.route('/userprofile', methods=['GET', 'POST'])
def userprofile():
    if request.method == 'POST':
        post_id = request.form['post_id']
        if post_id == '1':
            #Here from searchall OR here from my profile->friendsfollowerfollowing OR songpage OR friend requests
            target_username = request.form.get('target_username')
            cursor = conn.cursor()

            #Gets info from user
            query = "SELECT username, fname, lname, lastlogin, nickname FROM user WHERE username = %s"
            cursor.execute(query, (target_username))
            target_user_info = cursor.fetchone()

            #Set myself as userid or none if not logged in
            try:
                myself = current_user.id
            except AttributeError:
                myself = None

            #Get target_user's friend, follower, following count
            query = "SELECT COUNT(*) FROM " \
                    "(SELECT user1 FROM friend WHERE user2 = %s AND acceptStatus = 'Accepted' UNION SELECT user2 FROM friend WHERE user1 = %s AND acceptStatus = 'Accepted') AS friendcount "
            cursor.execute(query, (target_username, target_username))
            friendcount = cursor.fetchone()
            target_user_friend_count = friendcount['COUNT(*)']

            query = "SELECT COUNT(*) FROM (SELECT follower FROM follows WHERE follows = %s) AS followercount "
            cursor.execute(query, (target_username))
            followercount = cursor.fetchone()
            target_user_follower_count = followercount['COUNT(*)']

            query = "SELECT COUNT(*) FROM (SELECT follows FROM follows WHERE follower = %s) AS followingcount "
            cursor.execute(query, (target_username))
            followingcount = cursor.fetchone()
            target_user_following_count = followingcount['COUNT(*)']
            ###

            #Get target user's ratings given to songs and all songs info
            query = "SELECT song_info.title, song_info.songID, song_info.artists, song_info.genres, song_info.albumIDs, rateSong.stars, rateSong.ratingDate FROM " \
                        "(SELECT song.title, song.songID, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "GROUP BY song.title, song.songID) AS song_info " \
                        "JOIN rateSong ON song_info.songID = rateSong.songID WHERE rateSong.username = %s ORDER BY rateSong.ratingDate DESC "
            cursor.execute(query, (target_username))
            ratings = cursor.fetchall()

            #Get target user's reviews given to songs and all songs info
            query = "SELECT song_info.title, song_info.songID, song_info.artists, song_info.genres, song_info.albumIDs, reviewSong.reviewText, reviewSong.reviewDate FROM " \
                        "(SELECT song.title, song.songID, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "GROUP BY song.title, song.songID) AS song_info " \
                        "JOIN reviewSong ON song_info.songID = reviewSong.songID WHERE reviewSong.username = %s ORDER BY reviewSong.reviewDate DESC "
            cursor.execute(query, (target_username))
            reviews = cursor.fetchall()

            if (myself == None) or (myself == target_username):
                #if not logged in or viewing my own profile
                return render_template("userprofile.html", user=current_user, target_user_info=target_user_info, target_user_friend_count=target_user_friend_count, target_user_follower_count=target_user_follower_count, target_user_following_count=target_user_following_count, ratings=ratings, reviews=reviews)
            else:
                #if viewing someone else's profile

                #check if already friends
                query = "SELECT * FROM friend WHERE user1 = %s AND user2 = %s AND acceptStatus = 'Accepted' " \
                    "UNION SELECT * FROM friend WHERE user1 = %s AND user2 = %s AND acceptStatus = 'Accepted' "
                cursor.execute(query, (target_username, myself, myself, target_username))
                alreadyfriends = cursor.fetchone()

                #check if already pending friend request
                query = "SELECT * FROM friend WHERE user1 = %s AND user2 = %s AND acceptStatus = 'Pending' " \
                    "UNION SELECT * FROM friend WHERE user1 = %s AND user2 = %s AND acceptStatus = 'Pending' "
                cursor.execute(query, (target_username, myself, myself, target_username))
                alreadyfriendspending = cursor.fetchone()

                #check if already followed them
                query = "SELECT * FROM follows WHERE follower = %s AND follows = %s "
                cursor.execute(query, (myself, target_username))
                alreadyfollow = cursor.fetchone()

                if alreadyfriends:
                    if alreadyfollow:
                        return render_template("userprofile.html", user=current_user, target_user_info=target_user_info, target_user_friend_count=target_user_friend_count, target_user_follower_count=target_user_follower_count, target_user_following_count=target_user_following_count, ratings=ratings, reviews=reviews, viewing=1, alrfriends=1, alrfollow=1)
                    else:
                        return render_template("userprofile.html", user=current_user, target_user_info=target_user_info, target_user_friend_count=target_user_friend_count, target_user_follower_count=target_user_follower_count, target_user_following_count=target_user_following_count, ratings=ratings, reviews=reviews, viewing=1, alrfriends=1)
                else:
                    #not friends - so either pending or not added
                    if alreadyfriendspending:
                        if alreadyfollow:
                            return render_template("userprofile.html", user=current_user, target_user_info=target_user_info, target_user_friend_count=target_user_friend_count, target_user_follower_count=target_user_follower_count, target_user_following_count=target_user_following_count, ratings=ratings, reviews=reviews, viewing=1, alrpending=1, alrfollow=1)
                        else:
                            return render_template("userprofile.html", user=current_user, target_user_info=target_user_info, target_user_friend_count=target_user_friend_count, target_user_follower_count=target_user_follower_count, target_user_following_count=target_user_following_count, ratings=ratings, reviews=reviews, viewing=1, alrpending=1)
                    else:
                        if alreadyfollow:
                            return render_template("userprofile.html", user=current_user, target_user_info=target_user_info, target_user_friend_count=target_user_friend_count, target_user_follower_count=target_user_follower_count, target_user_following_count=target_user_following_count, ratings=ratings, reviews=reviews, viewing=1, alrfollow=1)
                        else:
                            return render_template("userprofile.html", user=current_user, target_user_info=target_user_info, target_user_friend_count=target_user_friend_count, target_user_follower_count=target_user_follower_count, target_user_following_count=target_user_following_count, ratings=ratings, reviews=reviews, viewing=1)
            

        elif post_id == '2':
            #Here from userprofile->add
            target_username = request.form.get('target_username')
            cursor = conn.cursor()

            query = "INSERT INTO friend VALUES(%s, %s, 'Pending', %s, %s, NULL)"
            now = datetime.datetime.now()
            formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')

            #assuming that whenever a request comes in, we can sort the usernames alphabetically,
            #assign the lower value in user1 column, higher value in user2 column
            myself = current_user.id
            if min(myself, target_username) == myself:
                cursor.execute(query, (myself, target_username, myself, formatted_time))
            else:
                cursor.execute(query, (target_username, myself, myself, formatted_time))
            conn.commit()
            flash('Friend request sent successfully', 'success')

            #To load userprofile again!!
            #Gets info from user
            query = "SELECT username, fname, lname, lastlogin, nickname FROM user WHERE username = %s"
            cursor.execute(query, (target_username))
            target_user_info = cursor.fetchone()

            #Get target_user's friend, follower, following count
            query = "SELECT COUNT(*) FROM " \
                    "(SELECT user1 FROM friend WHERE user2 = %s AND acceptStatus = 'Accepted' UNION SELECT user2 FROM friend WHERE user1 = %s AND acceptStatus = 'Accepted') AS friendcount "
            cursor.execute(query, (target_username, target_username))
            friendcount = cursor.fetchone()
            target_user_friend_count = friendcount['COUNT(*)']

            query = "SELECT COUNT(*) FROM (SELECT follower FROM follows WHERE follows = %s) AS followercount "
            cursor.execute(query, (target_username))
            followercount = cursor.fetchone()
            target_user_follower_count = followercount['COUNT(*)']

            query = "SELECT COUNT(*) FROM (SELECT follows FROM follows WHERE follower = %s) AS followingcount "
            cursor.execute(query, (target_username))
            followingcount = cursor.fetchone()
            target_user_following_count = followingcount['COUNT(*)']
            ###

            #Get target user's ratings given to songs and all songs info
            query = "SELECT song_info.title, song_info.songID, song_info.artists, song_info.genres, song_info.albumIDs, rateSong.stars, rateSong.ratingDate FROM " \
                        "(SELECT song.title, song.songID, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "GROUP BY song.title, song.songID) AS song_info " \
                        "JOIN rateSong ON song_info.songID = rateSong.songID WHERE rateSong.username = %s ORDER BY rateSong.ratingDate DESC "
            cursor.execute(query, (target_username))
            ratings = cursor.fetchall()

            #Get target user's reviews given to songs and all songs info
            query = "SELECT song_info.title, song_info.songID, song_info.artists, song_info.genres, song_info.albumIDs, reviewSong.reviewText, reviewSong.reviewDate FROM " \
                        "(SELECT song.title, song.songID, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "GROUP BY song.title, song.songID) AS song_info " \
                        "JOIN reviewSong ON song_info.songID = reviewSong.songID WHERE reviewSong.username = %s ORDER BY reviewSong.reviewDate DESC "
            cursor.execute(query, (target_username))
            reviews = cursor.fetchall()

            #check if already followed them
            query = "SELECT * FROM follows WHERE follower = %s AND follows = %s "
            cursor.execute(query, (myself, target_username))
            alreadyfollow = cursor.fetchone()

            if alreadyfollow:
                return render_template("userprofile.html", user=current_user, target_user_info=target_user_info, target_user_friend_count=target_user_friend_count, target_user_follower_count=target_user_follower_count, target_user_following_count=target_user_following_count, ratings=ratings, reviews=reviews, viewing=1, alrpending=1, alrfollow=1)
            else:
                return render_template("userprofile.html", user=current_user, target_user_info=target_user_info, target_user_friend_count=target_user_friend_count, target_user_follower_count=target_user_follower_count, target_user_following_count=target_user_following_count, ratings=ratings, reviews=reviews, viewing=1, alrpending=1)
                    
        
        elif post_id == '3':
            #Here from userprofile->follow
            target_username = request.form.get('target_username')
            cursor = conn.cursor()

            query = "INSERT INTO follows VALUES(%s, %s, %s)"
            now = datetime.datetime.now()
            formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
            myself = current_user.id
            cursor.execute(query, (myself, target_username, formatted_time))
            conn.commit()
            flash('Followed successfully', 'success')

            #To load userprofile again!!
            #Gets info from user
            query = "SELECT username, fname, lname, lastlogin, nickname FROM user WHERE username = %s"
            cursor.execute(query, (target_username))
            target_user_info = cursor.fetchone()

            #Get target_user's friend, follower, following count
            query = "SELECT COUNT(*) FROM " \
                    "(SELECT user1 FROM friend WHERE user2 = %s AND acceptStatus = 'Accepted' UNION SELECT user2 FROM friend WHERE user1 = %s AND acceptStatus = 'Accepted') AS friendcount "
            cursor.execute(query, (target_username, target_username))
            friendcount = cursor.fetchone()
            target_user_friend_count = friendcount['COUNT(*)']

            query = "SELECT COUNT(*) FROM (SELECT follower FROM follows WHERE follows = %s) AS followercount "
            cursor.execute(query, (target_username))
            followercount = cursor.fetchone()
            target_user_follower_count = followercount['COUNT(*)']

            query = "SELECT COUNT(*) FROM (SELECT follows FROM follows WHERE follower = %s) AS followingcount "
            cursor.execute(query, (target_username))
            followingcount = cursor.fetchone()
            target_user_following_count = followingcount['COUNT(*)']
            ###

            #Get target user's ratings given to songs and all songs info
            query = "SELECT song_info.title, song_info.songID, song_info.artists, song_info.genres, song_info.albumIDs, rateSong.stars, rateSong.ratingDate FROM " \
                        "(SELECT song.title, song.songID, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "GROUP BY song.title, song.songID) AS song_info " \
                        "JOIN rateSong ON song_info.songID = rateSong.songID WHERE rateSong.username = %s ORDER BY rateSong.ratingDate DESC "
            cursor.execute(query, (target_username))
            ratings = cursor.fetchall()

            #Get target user's reviews given to songs and all songs info
            query = "SELECT song_info.title, song_info.songID, song_info.artists, song_info.genres, song_info.albumIDs, reviewSong.reviewText, reviewSong.reviewDate FROM " \
                        "(SELECT song.title, song.songID, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                        "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                        "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                        "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                        "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                        "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                        "GROUP BY song.title, song.songID) AS song_info " \
                        "JOIN reviewSong ON song_info.songID = reviewSong.songID WHERE reviewSong.username = %s ORDER BY reviewSong.reviewDate DESC "
            cursor.execute(query, (target_username))
            reviews = cursor.fetchall()

            #check if already friends
            query = "SELECT * FROM friend WHERE user1 = %s AND user2 = %s AND acceptStatus = 'Accepted' " \
                    "UNION SELECT * FROM friend WHERE user1 = %s AND user2 = %s AND acceptStatus = 'Accepted' "
            cursor.execute(query, (target_username, myself, myself, target_username))
            alreadyfriends = cursor.fetchone()

            #check if already pending friend request
            query = "SELECT * FROM friend WHERE user1 = %s AND user2 = %s AND acceptStatus = 'Pending' " \
                    "UNION SELECT * FROM friend WHERE user1 = %s AND user2 = %s AND acceptStatus = 'Pending' "
            cursor.execute(query, (target_username, myself, myself, target_username))
            alreadyfriendspending = cursor.fetchone()


            if alreadyfriends:
                return render_template("userprofile.html", user=current_user, target_user_info=target_user_info, target_user_friend_count=target_user_friend_count, target_user_follower_count=target_user_follower_count, target_user_following_count=target_user_following_count, ratings=ratings, reviews=reviews, viewing=1, alrfriends=1, alrfollow=1)
            else:
                #not friends - so either pending or not added
                if alreadyfriendspending:
                    return render_template("userprofile.html", user=current_user, target_user_info=target_user_info, target_user_friend_count=target_user_friend_count, target_user_follower_count=target_user_follower_count, target_user_following_count=target_user_following_count, ratings=ratings, reviews=reviews, viewing=1, alrpending=1, alrfollow=1)
                else:
                    return render_template("userprofile.html", user=current_user, target_user_info=target_user_info, target_user_friend_count=target_user_friend_count, target_user_follower_count=target_user_follower_count, target_user_following_count=target_user_following_count, ratings=ratings, reviews=reviews, viewing=1, alrfollow=1)
    
    else:
        #Here from Profile navigation
        target_username = request.args.get('user_id')
        cursor = conn.cursor()

        #Gets info from user
        query = "SELECT username, fname, lname, lastlogin, nickname FROM user WHERE username = %s"
        cursor.execute(query, (target_username))
        target_user_info = cursor.fetchone()

        #Get target_user's friend, follower, following count
        query = "SELECT COUNT(*) FROM " \
                "(SELECT user1 FROM friend WHERE user2 = %s AND acceptStatus = 'Accepted' UNION SELECT user2 FROM friend WHERE user1 = %s AND acceptStatus = 'Accepted') AS friendcount "
        cursor.execute(query, (target_username, target_username))
        friendcount = cursor.fetchone()
        target_user_friend_count = friendcount['COUNT(*)']

        query = "SELECT COUNT(*) FROM (SELECT follower FROM follows WHERE follows = %s) AS followercount "
        cursor.execute(query, (target_username))
        followercount = cursor.fetchone()
        target_user_follower_count = followercount['COUNT(*)']

        query = "SELECT COUNT(*) FROM (SELECT follows FROM follows WHERE follower = %s) AS followingcount "
        cursor.execute(query, (target_username))
        followingcount = cursor.fetchone()
        target_user_following_count = followingcount['COUNT(*)']
        ###

        #Get target user's ratings given to songs and all songs info
        query = "SELECT song_info.title, song_info.songID, song_info.artists, song_info.genres, song_info.albumIDs, rateSong.stars, rateSong.ratingDate FROM " \
                    "(SELECT song.title, song.songID, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                    "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                    "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                    "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                    "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                    "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                    "GROUP BY song.title, song.songID) AS song_info " \
                    "JOIN rateSong ON song_info.songID = rateSong.songID WHERE rateSong.username = %s ORDER BY rateSong.ratingDate DESC "
        cursor.execute(query, (target_username))
        ratings = cursor.fetchall()

        #Get target user's reviews given to songs and all songs info
        query = "SELECT song_info.title, song_info.songID, song_info.artists, song_info.genres, song_info.albumIDs, reviewSong.reviewText, reviewSong.reviewDate FROM " \
                    "(SELECT song.title, song.songID, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                    "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                    "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                    "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                    "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                    "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                    "GROUP BY song.title, song.songID) AS song_info " \
                    "JOIN reviewSong ON song_info.songID = reviewSong.songID WHERE reviewSong.username = %s ORDER BY reviewSong.reviewDate DESC "
        cursor.execute(query, (target_username))
        reviews = cursor.fetchall()
        return render_template("userprofile.html", user=current_user, target_user_info=target_user_info, target_user_friend_count=target_user_friend_count, target_user_follower_count=target_user_follower_count, target_user_following_count=target_user_following_count, ratings=ratings, reviews=reviews)




@auth.route('/friendsfollowerfollowing', methods=['GET', 'POST'])
def friendsfollowerfollowing():
    if request.method == 'POST':
        post_id = request.form['post_id']
        if post_id == '1':
            #Friend list
            username = request.form.get('username')
            cursor = conn.cursor()

            query = "SELECT user2 AS user FROM friend WHERE user1 = %s AND acceptStatus = 'Accepted' " \
                    "UNION SELECT user1 AS user FROM friend WHERE user2 = %s AND acceptStatus = 'Accepted' "
            cursor.execute(query, (username, username))
            friends = cursor.fetchall()

            return render_template("friendsfollowerfollowing.html", user=current_user, friends=friends)
        
        elif post_id == '2':
            #Followers list
            username = request.form.get('username')
            cursor = conn.cursor()

            query = "SELECT follower FROM follows WHERE follows = %s"
            cursor.execute(query, (username))
            followers = cursor.fetchall()

            return render_template("friendsfollowerfollowing.html", user=current_user, followers=followers)
        
        elif post_id == '3':
            #Following list
            username = request.form.get('username')
            cursor = conn.cursor()

            query = "SELECT follows FROM follows WHERE follower = %s"
            cursor.execute(query, (username))
            following = cursor.fetchall()

            return render_template("friendsfollowerfollowing.html", user=current_user, following=following)



@auth.route('/feed', methods=['GET', 'POST'])
@login_required
def feed():
    username = current_user.id
    cursor = conn.cursor()

    if request.method == 'POST':
        post_id = request.form['post_id']
        target_username = request.form.get('target_username')
        now = datetime.datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        if post_id == '1':
            #Accepted friend request
            query = "UPDATE friend SET acceptStatus='Accepted', updatedAt= %s WHERE user1 = %s AND user2 = %s "
            if min(username, target_username) == username:
                cursor.execute(query, (formatted_date, username, target_username))
            else:
                cursor.execute(query, (formatted_date, target_username, username))
            conn.commit()

            flash('Successfully added!', category='success')
        
        elif post_id == '2':
            #Denied friend request
            query = "DELETE FROM friend WHERE user1 = %s AND user2 = %s"
            if min(username, target_username) == username:
                cursor.execute(query, (username, target_username))
            else:
                cursor.execute(query, (target_username, username))
            conn.commit()

            flash('Successfully deleted!', category='success')


    query = "SELECT user2 AS user FROM friend WHERE user1 = %s AND acceptStatus = 'Pending' AND requestSentBy != %s " \
            "UNION SELECT user1 AS user FROM friend WHERE user2 = %s AND acceptStatus = 'Pending' AND requestSentBy != %s "
    cursor.execute(query, (username, username, username, username))
    friendrequests = cursor.fetchall()

    query = "SELECT lastlogin FROM user WHERE username = %s"
    cursor.execute(query, (username))
    lastlogin = cursor.fetchone()
    lastlogindatetime = lastlogin['lastlogin']

    #New songs from artists you follow
    query = "SELECT song.title, song.songID, song.releaseDate, song.songURL, rate.stars, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
                            "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
                            "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
                            "JOIN userFanOfArtist ON artistPerformsSong.artistID = userFanOfArtist.artistID " \
                            "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
                            "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
                            "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
                            "LEFT JOIN (SELECT songID, AVG(stars) AS stars FROM rateSong GROUP BY songID) AS rate ON song.songID = rate.songID " \
                            "WHERE userFanOfArtist.username = %s " \
                            "GROUP BY song.title, song.songID, song.releaseDate, song.songURL " \
                            "HAVING song.releaseDate >= %s"
    cursor.execute(query, (username, lastlogindatetime))
    newsongs = cursor.fetchall()


    #New song ratings from people you're friends with or you follow
    query = "SELECT song_info.title, song_info.songID, song_info.artists, song_info.genres, song_info.albumIDs, " \
            "rateSong.stars, rateSong.ratingDate, rateSong.username FROM " \
            "(SELECT song.title, song.songID, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
            "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
            "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
            "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
            "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
            "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
            "GROUP BY song.title, song.songID) AS song_info " \
            "JOIN rateSong ON song_info.songID = rateSong.songID WHERE rateSong.ratingDate >= %s AND " \
            "rateSong.username IN " \
            "(SELECT user2 AS user FROM friend WHERE user1 = %s AND acceptStatus = 'Accepted' " \
            "UNION SELECT user1 AS user FROM friend WHERE user2 = %s AND acceptStatus = 'Accepted' "\
            "UNION SELECT follows AS user FROM follows WHERE follower = %s ) " \
            "ORDER BY rateSong.ratingDate DESC "
    cursor.execute(query, (lastlogindatetime, username, username, username))
    newratings = cursor.fetchall()


    #New song reviews from people you're friends with or you follow
    query = "SELECT song_info.title, song_info.songID, song_info.artists, song_info.genres, song_info.albumIDs, " \
            "reviewSong.reviewText, reviewSong.reviewDate, reviewSong.username FROM " \
            "(SELECT song.title, song.songID, GROUP_CONCAT(DISTINCT artist.fname,' ',artist.lname) AS artists, " \
            "GROUP_CONCAT(DISTINCT songGenre.genre) AS genres, GROUP_CONCAT(DISTINCT songInAlbum.albumID) AS albumIDs " \
            "FROM song JOIN artistPerformsSong ON song.songID = artistPerformsSong.songID " \
            "JOIN artist ON artist.artistID = artistPerformsSong.artistID " \
            "LEFT JOIN songInAlbum on song.songID = songInAlbum.songID " \
            "LEFT JOIN songGenre ON songGenre.songID = song.songID " \
            "GROUP BY song.title, song.songID) AS song_info " \
            "JOIN reviewSong ON song_info.songID = reviewSong.songID WHERE reviewSong.reviewDate >= %s AND " \
            "reviewSong.username IN " \
            "(SELECT user2 AS user FROM friend WHERE user1 = %s AND acceptStatus = 'Accepted' " \
            "UNION SELECT user1 AS user FROM friend WHERE user2 = %s AND acceptStatus = 'Accepted' "\
            "UNION SELECT follows AS user FROM follows WHERE follower = %s ) " \
            "ORDER BY reviewSong.reviewDate DESC "
    cursor.execute(query, (lastlogindatetime, username, username, username))
    newreviews = cursor.fetchall()


    return render_template("feed.html", user=current_user, friendrequests=friendrequests, newsongs=newsongs, newratings=newratings, newreviews=newreviews)



