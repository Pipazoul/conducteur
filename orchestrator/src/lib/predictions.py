from enum import Enum
from threading import Lock
import sqlite3
import json
con = sqlite3.connect("/app/data/conducteur.db", check_same_thread=False)
cur = con.cursor()

class PredictionStatus(Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"

class PredictionRequest(Enum):
    asynchronous = "asynchronous"
    synchronous = "synchronous"
        
class Predictions:
    _lock = Lock()
    def __init__(
                self, user:str,
                image:str,
                input:dict,
                started:str,
                id: int = None,
                node: str=None,
                finished:str = None,
                duration:float = None,
                co2=None,
                status:PredictionStatus = PredictionStatus.pending,
                request:PredictionRequest = PredictionRequest.synchronous.value,
                webhook:str = None,
            ):
            self.id = id  # will be set by the database when inserting a new row.
            self.user = user
            self.image = image
            self.input = input  # the actual data that will be predicted.
            self.status = PredictionStatus.pending.value
            self.started = started
            self.node = node
            self.finished = finished
            self.duration = duration
            self.request = request  # asynchronous or synchronous.
            self.logs = ""
            self.co2 = co2
            self.webhook = webhook   # the url to POST results back to.
            cur.execute('''
                CREATE TABLE IF NOT EXISTS prediction(
                id INTEGER PRIMARY KEY,
                user TEXT NOT NULL,
                image TEXT NOT NULL,
                input  JSON,
                status TEXT NOT NULL,
                started DATETIME NOT NULL,
                node TEXT,
                finished DATETIME,
                duration FLOAT,
                co2 FLOAT,
                request TEXT NOT NULL DEFAULT 'synchronous',
                logs TEXT DEFAULT '',
                webhook TEXT
                );
            ''')
            
    def create(self):
        print('Creating new Prediction')
        print('self.request', self.request)
        cur.execute("INSERT INTO prediction (user, image, input, status, started, node, finished, duration, request, logs, webhook) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (self.user, self.image, json.dumps(self.input), self.status, self.started, self.node, self.finished, self.duration, self.request, self.logs, self.webhook))
        con.commit()
        self.id = cur.lastrowid
        
         
    def update(self):
        with self._lock:
            if self.status == PredictionStatus.completed.value or self.status == PredictionStatus.failed.value:
                self.input = {}
            cur.execute(
                "UPDATE prediction SET node= ?, status = ? , finished = ? , duration = ? ,co2 = ? ,input = ? WHERE id = ?",
                (self.node, self.status, self.finished, self.duration, self.co2, json.dumps(self.input), self.id))
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
            data.append(return_object(row))
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
            data.append(return_object(row))

        return data
    @staticmethod
    def get_pending_async():
        cur.execute("SELECT * FROM prediction WHERE status = 'pending' AND request = 'asynchronous' ORDER BY started ASC LIMIT 1")
        response = cur.fetchone()

        if response is None:
            return None

        return return_object(response)


    # get one prediction by id
    @staticmethod
    def get(id: int):
        cur.execute("SELECT * FROM prediction WHERE id = ?", (id,))
        row = cur.fetchone()
        if not row:
            return None
        return return_object(row)
    # delete one prediction by id
    @staticmethod
    def delete(id: int):
        cur.execute("DELETE FROM prediction WHERE id = ?", (id,))
        con.commit()

    # delete all predictions pending with request async
    @staticmethod
    def delete_sync_pending():
        cur.execute("DELETE FROM prediction WHERE status = 'pending' AND request = 'synchronous'")
        con.commit()
    
    # delete all running predictions
    @staticmethod
    def delete_running():
        cur.execute("DELETE FROM prediction WHERE status = 'running'")
        con.commit()

def return_object(row: tuple):
    if not row:
        return None
    return {
        'id': int(row[0]),
            'user': row[1],
            'image': row[2],
            'input': json.loads(row[3]),
            'status': row[4],
            'started': str(row[5]),
            'node': str(row[6]),
            'finished': str(row[7]),
            'duration': float(row[8]) if row[8] else None,
            'co2': float(row[9]) if row[9] else None,
            'request': row[10],
            'logs': row[11],
            'webhook': row[12],
    }    