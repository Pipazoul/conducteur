from lib.cog import Cog
from threading import Thread
import time
import json
import re 
import logging

class Co2:
    def __init__(self, cog: Cog, carbon_intensity):
        logging.debug("🔥 Initializing CO2 monitoring")
        self.cog = cog
        self.carbon_intensity = carbon_intensity
        self.duration = 0
        self.watts = 0
        self.running = False  # shared variable to control the thread
        self.grams_emitted = 0
    def start(self):
        logging.debug("🔥 Starting CO2 monitoring thread")
        self.running = True
        self.thread = Thread(target=self._run)
        self.thread.start()

    def _run(self):
        logging.debug("🔥 Running CO2 monitoring")
        while self.running:
            # reset values
            self.grams_emitted = 0
            self.watts= 0
            self.duration = 0
            power = 0
            result = self.cog.run()
            result = json.loads(result["output"])
            power = result["power"] # get the power consumption from the output of cog run() function
            match = re.search(r"\d+\.?\d*", power)  # use regex to extract the number
            power = float(match.group()) if match else 0  # convert it to float if there is a number, otherwise return 0
            self.watts += power  
            self.duration += 1
            time.sleep(1)

    def stop(self):
        logging.debug("🔥 Stopping CO2 monitoring")
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()  # wait for the thread to finish
            # Assuming self.watts is accumulated power consumption in watts and self.duration is in seconds.
            # Convert power usage to kWh then multiply by carbon intensity.
            energy_consumed = (self.watts * self.duration) / (3600 * 1000)  # from watt-seconds to kilowatt-hours
            # return 3 digits after the decimal point
            self.grams_emitted = round((energy_consumed * self.carbon_intensity), 3)   # in grams of CO2e (equivalent to carbon dioxide equivalent)
    def calculate(self, energy_consumed):
        logging.debug("🔥 Calculating CO2 ")
        return (energy_consumed * self.carbon_intensity)