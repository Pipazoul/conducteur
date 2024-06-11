import json
import datetime 

class Prediction:
    user: str
    image: str
    status: str
    started: str
    finished: str
    duration: float

def load():
    with open("../data/predictions.json", "r") as file:
        return json.load(file)

def save(predictions):
    with open("../data/predictions.json", "w") as file:
        json.dump(predictions, file, indent=4)

def filter_by_user(user, start, end):
    predictions = load()

    filtered = []
    totalDuration = 0
    # chekc if start and end are None
    if not start and not end:
        for prediction in predictions:
            if prediction['user'] == user:
                filtered.append(prediction)
                totalDuration += prediction['duration']
        return {
            "predictions": filtered,
            "totalDuration": totalDuration
        }
    # check if start and end are DD-MM-YYYY
    try:
        start = datetime.datetime.strptime(start, "%d-%m-%Y")
        end = datetime.datetime.strptime(end, "%d-%m-%Y")
        # Adjust end date to the end of the day
        end = end.replace(hour=23, minute=59, second=59)
    except ValueError:
        return "Invalid date format DD-MM-YYYY"
    
    for prediction in predictions:
        if prediction['user'] == user:
            #"2024-06-11 11:58:37.471815",
            started = datetime.datetime.strptime(prediction['started'], "%Y-%m-%d %H:%M:%S.%f")
            if started >= start and started <= end:
                try:
                    filtered.append(prediction)
                    totalDuration += prediction['duration']
                except KeyError:
                    # remove the prediction from the list
                    predictions.remove(prediction)
    save(predictions)
                

    


    return {
        "predictions": filtered,
        "totalDuration": totalDuration
    }