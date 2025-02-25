from machine import Pin, ADC, SoftI2C
import ujson
import ssd1306
import network
import utime as time
import dht
import urequests

DEVICE_ID = "esp32-sic6"
WIFI_SSID = "rawr"
WIFI_PASSWORD = "12345678"
TOKEN = "BBUS-xbL1j5pc4ujrqlA01X6119Pp63T4XJ"
DHT_PIN = Pin(15)
redLed = Pin(2, Pin.OUT)
yellowLed = Pin(4, Pin.OUT)
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
    
def did_receive_callback(topic, message):
    print('\n\nData Received! \ntopic = {0}, message = {1}'.format(topic, message))

def create_json_data(temperature, humidity):
    data = ujson.dumps({
        "device_id": DEVICE_ID,
        "temp": temperature,
        "humidity": humidity,
        "type": "sensor"
    })
    return data

def send_data(temperature, humidity):
    print("sending data to ubidots")
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_ID
    headers = {"Content-Type": "application/json", "X-Auth-Token": TOKEN}
    data = {
        "temp": temperature,
        "humidity": humidity,
    }
    response = urequests.post(url, json=data, headers=headers)
    print("Done Sending Data!")
    print("Response:", response.text)

def control_leds(temperature):
    if temperature > 23:
        redLed.on()     # Red LED ON
        yellowLed.off() # Yellow LED OFF
        print("Red LED ON (Temp > 20°C)")
    else:
        redLed.off()    # Red LED OFF
        yellowLed.on()  # Yellow LED ON
        print("Yellow LED ON (Temp <= 20°C)")
        
def send_to_api(temperature, humidity):
    print("sending data to mongodb")
    api_url = "http://192.168.137.103:5000/create"
    headers = {"Content-Type": "application/json"}
    data = {"temp": temperature, "humidity": humidity}
    
    try:
        response = urequests.post(api_url, json=data, headers=headers)
        print("API Response:", response.text)
    except Exception as e:
        print("Gagal mengirim data:", e)
    
wifi_client = network.WLAN(network.STA_IF)
wifi_client.active(True)
print("Connecting device to WiFi")
wifi_client.connect(WIFI_SSID, WIFI_PASSWORD)

while not wifi_client.isconnected():
    print("Connecting")
    time.sleep(0.1)
print("WiFi Connected!")
print(wifi_client.ifconfig())

dht_sensor = dht.DHT11(DHT_PIN)
telemetry_data_old = ""

while True:
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        
        send_to_api(temperature, humidity)


        # Control LEDs based on temperature
        control_leds(temperature)
        
        # Print to Serial
        print(f"Temperature: {temperature}°C, Humidity: {humidity}%")

        # Display Data on OLED
        oled.fill(0)
        oled.text("Temp: {} C".format(temperature), 0, 10)
        oled.text("Humidity: {}%".format(humidity), 0, 30)
        oled.show()
        

        send_data(temperature, humidity)
    except:
        pass

    time.sleep(5)
