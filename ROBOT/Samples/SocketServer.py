# Running on the Raspberry Pi server

import eventlet
import socketio

sio = socketio.Server()
app = socketio.WSGIApp(sio)


def get_device_id(environ):
    return environ.get('HTTP_DEVICE_ID', None)


@sio.event
def connect(sid, environ):
    print(environ)
    device_id = get_device_id(environ) or sid
    sio.save_session(sid, {'device_id': device_id})
    print('{} is connected'.format(device_id))

# this function run on demand


@sio.on('send')
def send(sid, data):
    session = sio.get_session(sid)
    print('Received data from {}: {}'.format(session['device_id'], data))
    sio.emit('receive', {'page': 'main', 'camera': True, 'capture': False,
             'scan': False, 'cpu': 35, 'battery_1': 7.32, 'battery_2': 3.5})

# this function running real time


@sio.on('talk')
def talk(sid):
    session = sio.get_session(sid)
    # print('Received -> Sent to {}'.format(session['device_id']))
    sio.emit('listen', {'page': 0, 'cpu_temp': 35, 'battery_1': 7.32, 'battery_2': 3.5, 'camera': True, 'capture': False,
             'scan': False,'think':True,'talk':False,'speak':False})


@sio.event
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    print("Server Started")
    eventlet.wsgi.server(eventlet.listen(
        ('192.168.2.19', 5000)), app, log_output=False)
