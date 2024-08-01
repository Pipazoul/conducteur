from enum import Enum
import sqlite3
con = sqlite3.connect("conducteur.db")
cur = con.cursor()

class PredictionStatus(Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
        
class Predictions:
    def __init__(self, user:str, image:str, started:str, finished:str = None, duration:float = None):
            self.id = None  # will be set by the database when inserting a new row.
            self.user = user
            self.image = image
            self.status = PredictionStatus.pending.value
            self.started = started
            self.finished = finished
            self.duration = duration
            cur.execute('''
                CREATE TABLE IF NOT EXISTS prediction(
                id INTEGER PRIMARY KEY,
                user TEXT NOT NULL,
                image TEXT NOT NULL,
                status TEXT NOT NULL,
                started DATETIME NOT NULL,
                finished DATETIME,
                duration FLOAT);
            ''')
            cur.execute("INSERT INTO prediction (user,image,status,started,finished,duration) VALUES (?, ?, ?, ?, ?, ?)", 
                    (self.user, self.image, self.status, self.started, self.finished, self.duration))
            con.commit()
            self.id = cur.lastrowid
            

            
        
    def filter_by_user(self, user: str):
        cur.execute("SELECT * FROM prediction WHERE user = ?", (user, ))
        return cur.fetchall()
    
    def get(self):
        cur.execute('''SELECT * FROM prediction ''')
        return cur.fetchall()
        


