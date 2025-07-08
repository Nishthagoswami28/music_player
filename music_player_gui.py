import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from music_player import DatabaseManager, Playlist, Song
import pygame
import os

class MusicPlayerApp:
    def __init__(self, root):
        self.root = root
        self.db = DatabaseManager()
        self.playlist = Playlist("My Playlist")

        self.current_song_index = None

        # Init pygame mixer
        pygame.mixer.init()

        # Setup UI
        self.create_widgets()
        self.load_songs_from_db()

    def create_widgets(self):
        self.root.title("🎵 Tkinter Music Player")
        self.root.geometry("540x480")
        self.root.configure(bg="#f0f2f5")

        title = tk.Label(self.root, text="🎶 My Music Playlist", font=("Helvetica", 18, "bold"), bg="#f0f2f5", fg="#333")
        title.pack(pady=10)

        self.listbox = tk.Listbox(self.root, font=("Helvetica", 12), width=45, height=12, bd=2, relief="groove")
        self.listbox.pack(pady=10)

        self.status_label = tk.Label(self.root, text="No song playing", font=("Helvetica", 10), fg="#666", bg="#f0f2f5")
        self.status_label.pack(pady=5)

        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 10), padding=6)

        # --- Buttons Frame ---
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=10)

        add_button = tk.Button(button_frame, text="Add Song", command=self.add_song, width=12)
        prev_button = tk.Button(button_frame, text="Previous", command=self.play_previous, width=12)
        play_button = tk.Button(button_frame, text="Play/Pause", command=self.toggle_play_pause, width=12)
        next_button = tk.Button(button_frame, text="Next", command=self.play_next, width=12)
        delete_button = tk.Button(button_frame, text="Delete Song", command=self.delete_song, width=12)

        add_button.grid(row=0, column=0, padx=5, pady=5)
        prev_button.grid(row=0, column=1, padx=5, pady=5)
        play_button.grid(row=0, column=2, padx=5, pady=5)
        next_button.grid(row=0, column=3, padx=5, pady=5)
        delete_button.grid(row=0, column=4, padx=5, pady=5)

    def load_songs_from_db(self):
        songs_data = self.db.fetch_all_songs()
        for row in songs_data:
            song = Song(row['id'], row['title'], row['duration'], row['file_path'])
            self.playlist.add_song(song)
            self.listbox.insert(tk.END, song.title)

    def toggle_play_pause(self):
        if self.playlist.is_playing:
            self.pause_song()
        else:
            self.play_song(from_listbox=True)
    
    def play_song(self, from_listbox=False):
        if not self.playlist.songs:
            messagebox.showinfo("Info", "No songs in playlist.")
            return

        if from_listbox and self.listbox.curselection():
            self.current_song_index = self.listbox.curselection()[0]
        elif self.current_song_index is None:
            self.current_song_index = 0

        # Make sure index is within valid range
        if self.current_song_index >= len(self.playlist.songs):
            self.current_song_index = 0

        song = self.playlist.songs[self.current_song_index]
        try:
            pygame.mixer.music.load(song.file_path)
            pygame.mixer.music.play()
            self.status_label.config(text=f"Now Playing: {song.title}", fg="green")
            self.playlist.is_playing = True

            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.current_song_index)
            self.listbox.activate(self.current_song_index)
            self.listbox.see(self.current_song_index)
        except Exception as e:
            messagebox.showerror("Playback Error", str(e))



    def pause_song(self):
        pygame.mixer.music.pause()
        self.status_label.config(text="Paused", fg="blue")
        self.playlist.is_playing = False

    def play_next(self):
        if not self.playlist.songs:
            messagebox.showinfo("Info", "No songs in playlist.")
            return

        if self.current_song_index is None:
            self.current_song_index = 0
        else:
            self.current_song_index = (self.current_song_index + 1) % len(self.playlist.songs)

        self.play_song()

    def play_previous(self):
        if not self.playlist.songs:
            messagebox.showinfo("Info", "No songs in playlist.")
            return

        if self.current_song_index is None:
            self.current_song_index = 0
        else:
            self.current_song_index = (self.current_song_index - 1) % len(self.playlist.songs)

        self.play_song()

    def add_song(self):
        path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
        if path:
            title = os.path.splitext(os.path.basename(path))[0]
            duration = "00:00:00"  # optional: use mutagen for real duration
            song = Song(None, title, duration, path)
            self.db.insert_song(song)
            self.playlist.add_song(song)
            self.listbox.insert(tk.END, title)
            messagebox.showinfo("Success", "Song added!")

    def delete_song(self):
        if not self.listbox.curselection():
            messagebox.showwarning("Warning", "Select a song to delete.")
            return

        index = self.listbox.curselection()[0]
        song = self.playlist.songs[index]

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{song.title}'?")
        if not confirm:
            return

        # Remove from playlist and database using song_id
        self.playlist.delete_song_by_id(song.song_id)
        self.db.delete_song_by_id(song.song_id)

        # Remove from listbox
        self.listbox.delete(index)

        # Update current index
        if self.current_song_index == index:
            self.current_song_index = None
            self.status_label.config(text="No song playing", fg="#666")

        messagebox.showinfo("Deleted", f"Deleted: {song.title}")


    def on_close(self):
        self.db.close_connection()
        pygame.mixer.quit()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
