# Running on the Raspberry Pi server

import eventlet
import socketio
import sensor_data

sio = socketio.Server()
app = socketio.WSGIApp(sio)
DB =sensor_data.DB

def get_device_id(environ):
    return environ.get('HTTP_DEVICE_ID', None)

def start_sensors():
    return sensor_data.run()

@sio.event
def connect(sid, environ):
    task = sio.start_background_task(start_sensors)
    device_id = get_device_id(environ) or sid
    sio.save_session(sid, {'device_id': device_id})
    print('{} is connected'.format(device_id))

# this function run on demand
@sio.on('send')
def send(sid, data):
    #tek key value gelirse
    # key = [k for k, v in data.items()][0]
    # value = data[key]
    for key, value in data.items():
        save = DB.saveData(key,value)
        response = f"{key} değeri {value} olarak değişti."
        sio.emit('receive', response)
        sio.sleep(.2)
    # session = sio.get_session(sid)
    # print('Received data from {}: {}'.format(session['device_id'], data))

# this function running real time
@sio.on('talk')
def talk(sid):
    task = sio.start_background_task(start_sensors)
    sio.sleep(.2)
    response = DB.getData()
    sio.emit('listen', response)


@sio.event
def disconnect(sid):
    print('disconnect ', sid)
    
def run():
    print("Server Started")
    eventlet.wsgi.server(eventlet.listen(
        ('192.168.2.19', 5000)), app, log_output=False)

# use when you need to run standalone
if __name__ == '__main__':
    run()