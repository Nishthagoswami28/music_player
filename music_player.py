# -*- coding: utf-8 -*-
"""
Created on Tue May 27 10:16:36 2025

@author: asus
"""
import os
import pymysql as sql

"""DATABASE CLASS"""

class DatabaseManager:
    def __init__(self):
        try:
            self.con = sql.connect(
                host="127.0.0.1",
                user="root",
                password="sql",
                database="music_player",
                charset="utf8",
                cursorclass=sql.cursors.DictCursor
            )
            self.cursor = self.con.cursor()
            print("Database connected successfully.")
        except Exception as e:
            print("Connection failed:", e)

    def fetch_all_songs(self):
        try:
            self.cursor.execute("SELECT * FROM songs")
            return self.cursor.fetchall()
        except Exception as e:
            print("Error fetching songs:", e)
            return []

    def insert_song(self, song):
        try:
            query = "INSERT INTO songs (title, duration, file_path) VALUES (%s, %s, %s)"
            values = (song.title, song.duration, song.file_path) 
            self.cursor.execute(query, values)
            self.con.commit()
            print(f"Song '{song.title}' added.")
        except Exception as e:
            print("Error inserting song:", e)

    def delete_song_by_id(self, song_id):
        try:
            self.cursor.execute("DELETE FROM songs WHERE id = %s", (song_id,))
            self.con.commit()
            print(f"Song with ID {song_id} deleted.")
        except Exception as e:
            print("Error deleting song:", e)

    def close_connection(self):
        try:
            self.cursor.close()
            self.con.close()
            print("Database connection closed.")
        except Exception as e:
            print("Error closing connection:", e)
            
""" SONG CLASS """

class Song:
    supported_formats = ['.mp3']

    def __init__(self, song_id, title, duration, file_path):
        self.song_id = song_id
        self.title = title
        self.duration = duration
        self.file_path = file_path

    def play(self):
        print(f"Playing: {self.title}")

    def stop(self):
        print(f"Stopped: {self.title}")

    def set_file_path(self, path):
        if os.path.splitext(path)[1].lower() in Song.supported_formats:
            self.file_path = path
        else:
            raise ValueError("Unsupported format")


    def __str__(self):
        return f"{self.title} [{self.duration}]"
    
"""PLAYLIST CLASS"""
    
class Playlist:
    def __init__(self, name):
        self.name = name
        self.songs = []
        self.current_index = 0
        self.is_playing = False

    def add_song(self, song):
        self.songs.append(song)
        print(f"Added: {song.title}")

    def remove_song(self, song):
        if song in self.songs:
            self.songs.remove(song)
            print(f"Removed: {song.title}")
        else:
            print("Song not found in playlist.")

    def play(self):
        if not self.songs:
            print("Playlist is empty.")
            return
        if not self.is_playing:
            self.is_playing = True
            self.songs[self.current_index].play()
        else:
            print(f"Already playing: {self.songs[self.current_index].title}")

    def pause(self):
        if self.is_playing:
            self.is_playing = False
            print(f"Paused: {self.songs[self.current_index].title}")
        else:
            print("Music is already paused.")

    def next_song(self):
        if not self.songs:
            print("Playlist is empty.")
            return
        self.current_index = (self.current_index + 1) % len(self.songs)
        self.is_playing = True
        self.songs[self.current_index].play()

    def previous_song(self):
        if not self.songs:
            print("Playlist is empty.")
            return
        self.current_index = (self.current_index - 1) % len(self.songs)
        self.is_playing = True
        self.songs[self.current_index].play()

    def show_queue(self):
        if not self.songs:
            print("Playlist is empty.")
            return
        print(f"Playlist: {self.name}")
        for i, song in enumerate(self.songs):
            marker = "->" if i == self.current_index and self.is_playing else "  "
            print(f"{marker} {i+1}. {song}")

    def show_current_song(self):
        if not self.songs:
            print("Playlist is empty.")
        else:
            current = self.songs[self.current_index]
            print(f"Current song: {current}")

    def delete_song_by_id(self, song_id):
        for song in self.songs:
            if song.song_id == song_id:
                self.songs.remove(song)
                print(f"Deleted from playlist: {song.title}")
                return
        print("Song with given ID not found in playlist.")
  

    def toggle_play_pause(self):
        if not self.songs:
            print("Playlist is empty.")
            return
        if self.is_playing:
            self.pause()
        else:
            self.play()


def main():
    print("""
    ================================
          WELCOME TO MUSIC PLAYER
    ================================
    
    Choose an option:
        1. Play/Pause Music
        2. Previous Song
        3. Next Song
        4. Show Song Queue
        5. Add Song
        6. Show Current Song
        7. Delete Song from Playlist
        8. Exit
    """)

    db = DatabaseManager()
    playlist = Playlist("My Playlist")

    songs_data = db.fetch_all_songs()
    for row in songs_data:
        song = Song(row['id'], row['title'], row['duration'], row['file_path'])
        playlist.add_song(song)

    while True:
        choice = input("Enter your choice (1-8): ")

        if choice == '1':
            playlist.toggle_play_pause()
        elif choice == '2':
            playlist.previous_song()
        elif choice == '3':
            playlist.next_song()
        elif choice == '4':
            playlist.show_queue()
        elif choice == '5':
            try:
                title = input("Enter Song Title: ")
                duration = input("Enter Duration (e.g., 00:00:00): ")
                file_path = input("Enter File Path: ")
                new_song = Song(None, title, duration, file_path) 
                db.insert_song(new_song)
                playlist.add_song(new_song)
                print("Song added to playlist and database.")
            except Exception as e:
                print("Error adding song:", e)
        elif choice == '6':
            playlist.show_current_song()
        elif choice == '7':
            try:
                song_id = int(input("Enter Song ID to delete: "))
                playlist.delete_song_by_id(song_id)
                db.delete_song_by_id(song_id)
            except Exception as e:
                print("Error deleting song:", e)
        elif choice == '8':
            print("Exiting Music Player...")
            db.close_connection()
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()