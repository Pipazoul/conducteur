from enum import Enum
from threading import Lock
import sqlite3
con = sqlite3.connect("/app/data/conducteur.db", check_same_thread=False)
cur = con.cursor()

class PredictionStatus(Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
        
class Predictions:
    _lock = Lock()
    def __init__(self, user:str, image:str, input:str ,started:str, node: str, finished:str = None, duration:float = None, co2=None, status:PredictionStatus = PredictionStatus.pending):
            self.id = None  # will be set by the database when inserting a new row.
            self.user = user
            self.image = image
            self.input = input  # the actual data that will be predicted.
            self.status = PredictionStatus.pending.value
            self.started = started
            self.node = node
            self.finished = finished
            self.duration = duration
            self.co2 = co2
            
    def create(self):
        cur.execute('''
                CREATE TABLE IF NOT EXISTS prediction(
                id INTEGER PRIMARY KEY,
                user TEXT NOT NULL,
                image TEXT NOT NULL,
                status TEXT NOT NULL,
                started DATETIME NOT NULL,
                node TEXT NOT NULL,
                finished DATETIME,
                duration FLOAT,
                co2 FLOAT);
            ''')
        cur.execute("INSERT INTO prediction (user,image,status,started,finished,duration) VALUES (?, ?, ?, ?, ?, ?)", 
                (self.user, self.image, self.status, self.started, self.finished, self.duration))
        con.commit()
        self.id = cur.lastrowid
        
         
    def update(self):
        with self._lock:
            cur.execute("UPDATE prediction SET node= ?, status = ? , finished = ? , duration = ?, co2 = ? WHERE id = ?", (self.node, self.status, self.finished, self.duration, self.co2, self.id))
            con.commit()

    @staticmethod
    def filter_by_user(user: str):
        cur.execute("SELECT * FROM prediction WHERE user = ?", (user, ))
        response = cur.fetchall()
        data = []
        # return obj {'user': '...', 'image': '...', 'status': '...'} for each row in the db
        for row in response:
            data.append({
                'id': int(row[0]),
                'user': row[1],
                'image': row[2],
                'status': row[3],
                'started': str(row[4]),
                'finished': str(row[5]),
                'duration': float(row[6]) if row[6] else None,
                'co2': float(row[7]) if row[7] else None,
            })

        return data

    
    def get_one(self, id: int):
        cur.execute("SELECT * FROM prediction WHERE id = ?", (id,))
    
    @staticmethod
    def get_all():
        cur.execute('''SELECT * FROM prediction ''')
        response = cur.fetchall()
        data = []
        # return obj {'user': '...', 'image': '...', 'status': '...'} for each row in the db
        for row in response:
            data.append({
                'id': int(row[0]),
                'user': row[1],
                'image': row[2],
                'status': row[3],
                'started': str(row[4]),
                'finished': str(row[5]),
                'duration': float(row[6]) if row[6] else None,
            })

        return data

    

        


