# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-pico-web-server-micropython/

# Import necessary modules
import network
import socket
import time
import random

from TemperatureSensors import Thermistor

from machine import Pin

# Create an LED object on pin 'LED'
#led = Pin('LED', Pin.OUT)

# Wi-Fi credentials
ssid = '***'
password = '***'


thermistor_1 = Thermistor(26)
thermistor_2 = Thermistor(27)
thermistor_3 = Thermistor(28)

# HTML template for the webpage
def webpage(temperature_value_1, temperature_value_2, temperature_value_3):
    html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pico Web Server</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
            <h1>Raspberry Pi Pico Web Server</h1>
            <p>Temperature 1 (26) value: {temperature_value_1}</p>
            <p>Temperature 2 (27) value: {temperature_value_2}</p>
            <p>Temperature 3 (28) value: {temperature_value_3}</p>
        </body>
        </html>
        """
    return str(html)

def json(temperature_value_1, temperature_value_2, temperature_value_3):
    response = f"""{
    [
        {
            "id":"26",
            "value":temperature_value_1
        },
        {
            "id":"27", 
            "value":temperature_value_2
        },
        {
            "id":"28", 
            "value":temperature_value_3
        }
    ]
 }"""
    return str(response)

# Connect to WLAN
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for Wi-Fi connection
connection_timeout = 10
while connection_timeout > 0:
    if wlan.status() >= 3:
        break
    connection_timeout -= 1
    print('Waiting for Wi-Fi connection...')
    time.sleep(1)

# Check if connection is successful
if wlan.status() != 3:
    raise RuntimeError('Failed to establish a network connection')
else:
    print('Connection successful!')
    network_info = wlan.ifconfig()
    print('IP address:', network_info[0])

# Set up socket and start listening
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen()

print('Listening on', addr)

# Initialize variables
temperature_value_1 = 0
temperature_value_2 = 0
temperature_value_3 = 0

# Main loop to listen for connections
while True:
    try:
        conn, addr = s.accept()
        print('Got a connection from', addr)
        
        # Receive and parse the request
        request = conn.recv(1024)
        request = str(request)
        print('Request content = %s' % request)

        try:
            request = request.split()[1]
            print('Request:', request)
        except IndexError:
            pass
        
        # Process the request and update variables
        if request == '/' or request == '/value':
            temperature_value_1 = thermistor_1.ReadTemperature()
            temperature_value_2 = thermistor_2.ReadTemperature()
            temperature_value_3 = thermistor_3.ReadTemperature()
            
            # Generate HTML response
            response = webpage(temperature_value_1, temperature_value_2, temperature_value_3)  

            # Send the HTTP response and close the connection
            conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            conn.send(response)
            conn.close()
        elif request == '/json':
            temperature_value_1 = thermistor_1.ReadTemperature()
            temperature_value_2 = thermistor_2.ReadTemperature()
            temperature_value_3 = thermistor_3.ReadTemperature()
            
            response = json(temperature_value_1, temperature_value_2, temperature_value_3) 
            
            conn.send('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
            conn.send(response)
            conn.close()
        
        else:
            conn.send('HTTP/1.0 404 Not Found\r\nContent-type: text/html\r\n\r\n')
            conn.close()

    except OSError as e:
        conn.close()
        print('Connection closed')
