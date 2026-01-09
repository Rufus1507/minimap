from nicegui import ui
import campus_map 
import beta_map

# --- TRANG CHỦ (MENU) ---
@ui.page('/')
def main_menu():
    with ui.column().classes('w-full items-center justify-center h-screen bg-gray-100'):
        ui.label("🗺️ HỆ THỐNG DẪN ĐƯỜNG ĐẠI HỌC").classes('text-4xl font-bold mb-10 text-blue-900')
        
        with ui.row().classes('gap-10'):
            # Nút 1: Bản đồ trường
            with ui.card().classes('w-72 h-64 items-center justify-center hover:bg-blue-50 cursor-pointer transition-all shadow-lg') \
                    .on('click', lambda: ui.navigate.to('/campus')):
                ui.icon('map', size='5em').classes('text-blue-500')
                ui.label("KHUÔN VIÊN TRƯỜNG").classes('text-xl font-bold mt-4 text-blue-800')
                ui.label("Tìm đường giữa các tòa nhà").classes('text-gray-500 text-center text-sm')

            # Nút 2: Bản đồ tòa Beta
            with ui.card().classes('w-72 h-64 items-center justify-center hover:bg-green-50 cursor-pointer transition-all shadow-lg') \
                    .on('click', lambda: ui.navigate.to('/beta')):
                ui.icon('apartment', size='5em').classes('text-green-500')
                ui.label("SƠ ĐỒ TÒA BETA").classes('text-xl font-bold mt-4 text-green-800')
                ui.label("Tìm đường giữa các phòng của 5 tầng").classes('text-gray-500 text-center text-sm')

# --- ĐỊNH NGHĨA TRANG CON ---
@ui.page('/campus')
def page_campus():
    campus_map.create_page()

@ui.page('/beta')
def page_beta():
    beta_map.create_page()

# --- CHẠY SERVER ---
ui.run(title="University Navigation", port=8000)