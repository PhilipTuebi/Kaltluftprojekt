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

# Load calibration parameters for the BME280 sensor
calibration_params = bme280.load_calibration_params(bus, address)

# Function to convert temperature from Celsius to Fahrenheit
def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

# Function to check if the internet connection is available
# Attempts to connect to Google's DNS server (8.8.8.8) to verify connectivity
def check_internet_connection():
    try:
        # Set a timeout for the connection attempt
        socket.setdefaulttimeout(5)
        # Try to establish a socket connection to Google's DNS server
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except socket.error:
        # Return False if the connection attempt fails
        return False

# Function to send a simple message to a Discord webhook
# Takes a string 'message' as input and sends it to the specified Discord webhook URL
def send_discord_message(message):
    webhook_url = "https://discordapp.com/api/webhooks/-deleted because of privacy reasons-"
    data = {"content": message}
    try:
        # Send a POST request to the Discord webhook with the message
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print("Discord message sent successfully!")
        else:
            print(f"Failed to send Discord message. Status code: {response.status_code}")
    except Exception as e:
        # Handle any errors that occur during the request
        print(f"An error occurred while sending Discord message: {str(e)}")

# Function to send a file to a Discord webhook
# Takes the file path and a message as input, and sends the file along with the message to the specified Discord webhook URL
def send_discord_file(file_path, message):
    webhook_url = "https://discordapp.com/api/webhooks/-deleted because of privacy reasons-"
    with open(file_path, 'rb') as file:
        data = {"content": message}
        files = {'file': file}
        try:
            # Send a POST request to the Discord webhook with the file and message
            response = requests.post(webhook_url, data=data, files=files)
            if response.status_code == 204:
                print("CSV file sent successfully to Discord!")
            else:
                print(f"Failed to send CSV file to Discord. Status code: {response.status_code}")
        except Exception as e:
            # Handle any errors that occur during the request
            print(f"An error occurred while sending CSV file to Discord: {str(e)}")

# Main loop: Wait for an active internet connection before proceeding
while not check_internet_connection():
    print("Waiting for internet connection...")
    time.sleep(5)

# Once the internet connection is established, send an initial Discord message and the CSV file
send_discord_message("Internet connection established on Raspberry Pi. Starting data logging.")
send_discord_file("BME280_data.csv", "Here is the BME280_data.csv file after establishing internet connection.")

# Flag to track the first data write to the CSV file
first_data_written = False

# Open the CSV file in append mode, creating it if it doesn't exist
with open('/home/felix/BME280_data.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    # Write the header row if the file is empty
    if file.tell() == 0:
        writer.writerow(['Date', 'Time', 'Temperature (°C)', 'Pressure (hPa)', 'Humidity (%)'])

    # Infinite loop to continually read sensor data and write it to the CSV file
    while True:
        try:
            # Read sensor data from the BME280
            data = bme280.sample(bus, address, calibration_params)

            # Extract temperature, pressure, and humidity values
            temperature_celsius = data.temperature
            pressure = data.pressure
            humidity = data.humidity

            # Get current date and time
            current_date = date.today()
            current_time = datetime.datetime.now().time()

            # Convert temperature from Celsius to Fahrenheit
            temperature_fahrenheit = celsius_to_fahrenheit(temperature_celsius)

            # Print the sensor readings to the console
            print("Temperature: {:.2f} °C, {:.2f} °F".format(temperature_celsius, temperature_fahrenheit))
            print("Pressure: {:.2f} hPa".format(pressure))
            print("Humidity: {:.2f} %".format(humidity))
            print("Date:", current_date)
            print("Time:", current_time)

            # Write the sensor data to the CSV file with date and time
            writer.writerow([current_date, current_time, temperature_celsius, pressure, humidity])

            # Send a Discord message if this is the first data entry
            if not first_data_written:
                send_discord_message(f"First data entry written to CSV on {current_date} at {current_time}.")
                first_data_written = True

            # Wait for 2 seconds before taking the next reading
            time.sleep(2)

        except KeyboardInterrupt:
            # Handle a manual interruption (Ctrl+C) by stopping the program
            print('Program stopped')
            break
        except Exception as e:
            # Handle any other unexpected errors
            print('An unexpected error occurred:', str(e))
            break
