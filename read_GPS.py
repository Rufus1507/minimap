from nicegui import ui

lat = ui.label('Latitude: --')
lng = ui.label('Longitude: --')
status = ui.label('Status: Chưa lấy vị trí')

def get_location():
    ui.run_javascript('''
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                emitEvent('gps', {
                    lat: pos.coords.latitude,
                    lng: pos.coords.longitude
                });
            },
            (err) => {
                emitEvent('gps_error', { message: err.message });
            }
        );
    ''')

ui.on('gps', lambda e: (
    lat.set_text(f"Latitude: {e.args['lat']}"),
    lng.set_text(f"Longitude: {e.args['lng']}"),
    status.set_text("Status: Đã lấy vị trí")
))

ui.on('gps_error', lambda e: (
    status.set_text(f"Lỗi: {e.args['message']}")
))

ui.button('📍 Lấy vị trí hiện tại', on_click=get_location)

ui.run()
