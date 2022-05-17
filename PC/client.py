# Running on Raspberry Pi 1
import socketio

sio = socketio.Client()

def send_sensor_readings():
    while True:
        sio.emit('my_message', {'temp':75})
        sio.sleep(5)

@sio.event
def connect():
    print('connection established')
    sio.start_background_task(send_sensor_readings)

@sio.event
def my_message(data):
    print('message received with ', data)


@sio.event
def disconnect():
    print('disconnected from server')

sio.connect('http://localhost:5000', headers={'device_id':'client1'})
sio.wait()
