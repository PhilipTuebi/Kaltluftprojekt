#!/usr/bin/python

import time
import smbus2
import bme280
import csv
import datetime
import socket
import requests
from datetime import date

# BME280 sensor address (default address)
address = 0x77

# Initialize I2C bus
bus = smbus2.SMBus(1)

# Load calibration parameters
calibration_params = bme280.load_calibration_params(bus, address)

def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def check_internet_connection():
    try:
        # Check if we can resolve the host and connect to Google's DNS server
        socket.setdefaulttimeout(5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except socket.error:
        return False

def send_discord_message(message):
    webhook_url = "https://discordapp.com/api/webhooks/1277709649688264744/0BYwgpYL6agvT82oSt5uVv6JiRABXv5WURbGxbvRHoaPqqJjr5WWi43Nn9q2d-VW71BX"
    data = {"content": message}
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print("Discord message sent successfully!")
        else:
            print(f"Failed to send Discord message. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while sending Discord message: {str(e)}")

def send_discord_file(file_path, message):
    webhook_url = "https://discordapp.com/api/webhooks/1277709649688264744/0BYwgpYL6agvT82oSt5uVv6JiRABXv5WURbGxbvRHoaPqqJjr5WWi43Nn9q2d-VW71BX"
    with open(file_path, 'rb') as file:
        data = {"content": message}
        files = {'file': file}
        try:
            response = requests.post(webhook_url, data=data, files=files)
            if response.status_code == 204:
                print("CSV file sent successfully to Discord!")
            else:
                print(f"Failed to send CSV file to Discord. Status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred while sending CSV file to Discord: {str(e)}")

# Wait for an active internet connection
while not check_internet_connection():
    print("Waiting for internet connection...")
    time.sleep(5)

# Internet connection is established, send a Discord message and CSV file
send_discord_message("Internet connection established on Raspberry Pi. Starting data logging.")
send_discord_file("BME280_data.csv", "Here is the BME280_data.csv file after establishing internet connection.")

# Flag to track the first data write
first_data_written = False

with open('/home/felix/BME280_data.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    # Write the header row if the file is empty
    if file.tell() == 0:
        writer.writerow(['Date', 'Time', 'Temperature (°C)', 'Pressure (hPa)', 'Humidity (%)'])

    while True:
        try:
            # Read sensor data
            data = bme280.sample(bus, address, calibration_params)

            # Extract temperature, pressure, humidity
            temperature_celsius = data.temperature
            pressure = data.pressure
            humidity = data.humidity

            # Get current date and time
            current_date = date.today()
            current_time = datetime.datetime.now().time()

            # Convert temperature to Fahrenheit
            temperature_fahrenheit = celsius_to_fahrenheit(temperature_celsius)

            # Print the readings
            print("Temperature: {:.2f} °C, {:.2f} °F".format(temperature_celsius, temperature_fahrenheit))
            print("Pressure: {:.2f} hPa".format(pressure))
            print("Humidity: {:.2f} %".format(humidity))
            print("Date:", current_date)
            print("Time:", current_time)

            # Write the data to the CSV file with date and time in separate columns
            writer.writerow([current_date, current_time, temperature_celsius, pressure, humidity])

            # Check if this is the first data write
            if not first_data_written:
                send_discord_message(f"First data entry written to CSV on {current_date} at {current_time}.")
                first_data_written = True

            # Wait for a few seconds before next reading
            time.sleep(2)

        except KeyboardInterrupt:
            print('Program stopped')
            break
        except Exception as e:
            print('An unexpected error occurred:', str(e))
            break
