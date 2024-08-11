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
    def __init__(self, user:str, image:str, input:str ,started:str, node: str=None, finished:str = None, duration:float = None, co2=None, status:PredictionStatus = PredictionStatus.pending):
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
            cur.execute('''
                CREATE TABLE IF NOT EXISTS prediction(
                id INTEGER PRIMARY KEY,
                user TEXT NOT NULL,
                image TEXT NOT NULL,
                status TEXT NOT NULL,
                started DATETIME NOT NULL,
                node TEXT,
                finished DATETIME,
                duration FLOAT,
                co2 FLOAT);
            ''')
            
    def create(self):
        cur.execute("INSERT INTO prediction (user,image,status,started,node,finished,duration) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                (self.user, self.image, self.status, self.started, self.node, self.finished, self.duration))
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
        total_co2 = 0
        total_duration = 0
        # return obj {'user': '...', 'image': '...', 'status': '...'} for each row in the db
        for row in response:
            data.append({
                'id': int(row[0]),
                'user': row[1],
                'image': row[2],
                'status': row[3],
                'started': str(row[4]),
                'node': str(row[5]),
                'finished': str(row[6]),
                'duration': float(row[7]) if row[7] else None,
                'co2': float(row[8]) if row[8] else None,
            })
            total_co2 += float(row[8]) if row[8] else 0
            total_duration += float(row[7]) if row[7] else 0
        return ({"total_co2": total_co2, "total_duration":total_duration, "predictions":data})

    
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
                'node': str(row[5]),
                'finished': str(row[6]),
                'duration': float(row[7]) if row[7] else None,
                'co2': float(row[8]) if row[8] else None,
            })

        return data

    

        


