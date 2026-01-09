from nicegui import ui
import networkx as nx
from PIL import Image, ImageDraw
import io, base64
import math 
import numpy as np
def create_page():




    # ===== GPS -> PIXEL TRANSFORM =====
    user_lat = None
    user_lon = None
    gps_status = ui.label("📡 Đang chờ GPS...").classes(
    'absolute bottom-4 right-4 z-20 '
    'bg-white px-4 py-2 rounded-full shadow text-sm')
    def request_gps():
        ui.run_javascript('''
            if (!navigator.geolocation) {
                emitEvent('gps-error', {message: 'Trình duyệt không hỗ trợ GPS'});
            } else {
                navigator.geolocation.getCurrentPosition(
                    (pos) => {
                        emitEvent('gps-update', {
                            lat: pos.coords.latitude,
                            lon: pos.coords.longitude
                        });
                    },
                    (err) => {
                        emitEvent('gps-error', {
                            message: err.message
                        });
                    }
                );
            }
        ''')
    def on_gps_update(e):
        nonlocal user_lat, user_lon
        user_lat = e.args['lat']
        user_lon = e.args['lon']

        gps_status.text = f"📍 GPS: {user_lat:.6f}, {user_lon:.6f}"
        update_path()

    ui.on('gps-update', on_gps_update)

    ui.on('gps-error', lambda e: (
        gps_status.set_text(f"❌ GPS lỗi: {e.args['message']}")
    ))
    ui.button(
    "📍 Lấy vị trí hiện tại",
    on_click=request_gps
).classes('bg-blue-600 text-white px-4 py-2 rounded')

    def build_gps_to_pixel(gps_points, pixel_points):
        """
        gps_points: dict {name: (lat, lon)}
        pixel_points: dict {name: (x, y)}
        """
        A = []
        Bx = []
        By = []

        for k in gps_points:
            lat, lon = gps_points[k]
            x, y = pixel_points[k]
            A.append([lat, lon, 1])
            Bx.append(x)
            By.append(y)

        A = np.array(A)
        Bx = np.array(Bx)
        By = np.array(By)

        coef_x = np.linalg.lstsq(A, Bx, rcond=None)[0]
        coef_y = np.linalg.lstsq(A, By, rcond=None)[0]

        def gps_to_pixel(lat, lon):
            x = coef_x[0]*lat + coef_x[1]*lon + coef_x[2]
            y = coef_y[0]*lat + coef_y[1]*lon + coef_y[2]
            return int(x), int(y)

        return gps_to_pixel


    # --- Style chung ---
    ui.query('body').style('background-color: #f0f4f8;') 
    with ui.column().classes('w-full items-center'):
        # --- Header ---
        with ui.row().classes('w-full justify-between items-center px-4 py-2 bg-white shadow-sm mb-4'):
            ui.button("⬅ Quay lại", on_click=lambda: ui.navigate.to('/')).classes('bg-slate-500 text-white px-4')
            ui.label("🌍 BẢN ĐỒ CAMPUS").classes("text-2xl md:text-3xl font-bold text-blue-800")
            ui.element('div').classes('w-24')
        # --- Ảnh bản đồ ---
        IMAGE_PATH = "khuonvientruong.jpg"
        # --- Dữ liệu địa điểm đã được thu gọn nên sẽ không hiện thị tọa độ các điểm---
        visible_locations = {
            "PARKING LOT A": (190, 840), 'GATE': (500, 900), "PARKING LOT B": (170, 600),
            "THE THINKER": (470, 760), "ALPHA BUILDING": (400, 500), "BETA BUILDING": (720, 700),
            "CANTEEN": (580, 390), "SOCCER": (880, 440), "BASKETBALL": (840, 330),
            "VOLLEYBALL": (850, 370), "VOVINAM": (900, 300),
            "HIGHSCHOOL DORMITARY": (1300, 300), "UNIVERSITY DORMITARY": (1370, 480),
        }
        # --- Các điểm ảo (Dùng nối đường nhưng không hiện trong menu chọn) 
        # đã được thu gọn nên sẽ không hiện thị tọa độ các điểm ---
        virtual_nodes = {
            "1": (300, 980), "2": (170, 970), "3": (80, 960), "4": (100, 640),
            "5": (590, 840), "BETA": (570, 740), "6": (280, 700), "7": (170, 760),
            'ALPHA': (420, 640), "8": (530, 600), "9": (420, 900), "10": (350, 700),
            "11": (380, 800), "12": (700, 540), "13": (730, 500), "14": (910, 380),
            "15": (930, 340), "16": (480, 420), "18": (720, 435), "19": (1060, 320),
            "20": (1120, 350), "21": (1065, 370), "22": (1240, 420), "23": (1300, 410),
        }
        locations = {**visible_locations, **virtual_nodes}
        gps_to_pixel = build_gps_to_pixel(
            gps_points={
            "GATE": (13.804580,109.219488),
            "ALPHA BUILDING": (13.803696, 109.219834),
            "BETA BUILDING": (13.804047, 109.219097),
            # "UNIVERSITY DORMITARY": (13.803590, 109.217654),
            },
            pixel_points={  
                "GATE": locations["GATE"],
                "ALPHA BUILDING": locations["ALPHA BUILDING"],
                "BETA BUILDING": locations["BETA BUILDING"],
            }
        )
        def snap_to_nearest_node(pixel):
            min_dist = float('inf')
            nearest = None
            ux, uy = pixel

            for name, (x, y) in locations.items():
                d = (ux - x) ** 2 + (uy - y) ** 2
                if d < min_dist:
                    min_dist = d
                    nearest = name

            return nearest

        # --- Xây dựng Đồ thị ---
        G = nx.Graph()
        # chứa các điểm nối với nhau 
        edges = [
            ('BETA','BETA BUILDING'), ('ALPHA BUILDING','ALPHA'),
            ("GATE","1"), ("1","2"), ("2","3"), ('2','PARKING LOT A'), ('3','4'), ("PARKING LOT B", "4"),
            ('GATE','THE THINKER'), ('GATE','5'), ('5','BETA'), ('BETA','THE THINKER'), ('6','ALPHA'), ('6','7'),
            ('6','PARKING LOT B'), ('7','PARKING LOT A'), ('BETA','8'), ('8','16'),('8','ALPHA'), ('9','GATE'),
            ('9','10'), ('10','6'), ('10','ALPHA'), ('10','11'), ('11','THE THINKER'), ('8','12'),
            ('BETA BUILDING','12'), ('12','13'), ('13','SOCCER'), ('SOCCER','14'), ('14','15'),
            ('VOLLEYBALL','15'), ('BASKETBALL','15'), ('VOVINAM','15'),
            ("BASKETBALL", "VOLLEYBALL"), ("VOLLEYBALL", "VOVINAM"), ("BASKETBALL", "VOVINAM"),
            ('ALPHA BUILDING','16'), ('16','CANTEEN'), ('CANTEEN','18'), ('18','13'), ('18','14'),
            ('14','19'), ('19','20'), ('20','HIGHSCHOOL DORMITARY'), ('SOCCER','21'), ('21','22'), ('22','23'),
            ('19','21'), ('23','UNIVERSITY DORMITARY'), ("HIGHSCHOOL DORMITARY", "UNIVERSITY DORMITARY")
        ]

        for a, b in edges:
            xa, ya = locations[a]
            xb, yb = locations[b]
            G.add_edge(a, b, weight=((xa - xb) ** 2 + (ya - yb) ** 2) ** 0.5)
        # --- Logic tìm đường ---
        def find_shortest_path(start, end):
            try:
                path = nx.shortest_path(G, source=start, target=end, weight="weight")
                dist = nx.shortest_path_length(G, source=start, target=end, weight="weight")
                return path, dist
            except nx.NetworkXNoPath:
                return [], float("inf")
        # --- Hàm vẽ đường đi lên ảnh ---
        def draw_dashed_line(draw, p1, p2, dash_len=20, gap_len=12, fill="red", width=8):
            x1, y1 = p1
            x2, y2 = p2

            dx = x2 - x1
            dy = y2 - y1
            distance = math.hypot(dx, dy)
            if distance == 0:
                return

            vx = dx / distance
            vy = dy / distance

            pos = 0
            while pos < distance:
                start = pos
                end = min(pos + dash_len, distance)

                sx = x1 + vx * start
                sy = y1 + vy * start
                ex = x1 + vx * end
                ey = y1 + vy * end

                draw.line([(sx, sy), (ex, ey)], fill=fill, width=width)
                pos += dash_len + gap_len

                # --- Logic vẽ hình ---
        def draw_path(path,user_pixel=None):
            try:
                img = Image.open(IMAGE_PATH).convert("RGB")
                draw = ImageDraw.Draw(img)
                if not path:
                    pass 
                # TRƯỜNG HỢP 1: Điểm đầu và cuối trùng nhau (List path chỉ có 1 phần tử)
                elif len(path) == 1:
                    p = locations[path[0]]
                    # Vẽ 1 chấm tròn đỏ to nổi bật
                    r = 15
                    draw.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), fill="#FF0000", outline="white", width=3)
                    # Vẽ thêm vòng tròn lan tỏa (hiệu ứng định vị)
                    draw.ellipse((p[0]-r*2, p[1]-r*2, p[0]+r*2, p[1]+r*2), outline="#FF0000", width=2)
                # TRƯỜNG HỢP 2: Có đường đi bình thường
                else:
                    # Vẽ dây nối
                    for i in range(len(path)-1):
                        p1 = locations[path[i]]
                        p2 = locations[path[i+1]]
                        draw_dashed_line(
                                    draw,
                                    p1,
                                    p2,
                                    dash_len=22,   # độ dài nét
                                    gap_len=12,    # khoảng hở
                                    fill="red",
                                    width=8
                                                )               
                    # Vẽ điểm đầu (Xanh)
                    start = locations[path[0]]
                    draw.ellipse((start[0]-12, start[1]-12, start[0]+12, start[1]+12), fill="#007bff", outline="white", width=2)
                    # Vẽ điểm cuối (Lục/Cờ đích)
                    end = locations[path[-1]]
                    draw.ellipse((end[0]-12, end[1]-12, end[0]+12, end[1]+12), fill="#28a745", outline="white", width=2)
                    if user_pixel:
                        draw.ellipse(
                            (user_pixel[0]-10, user_pixel[1]-10,
                            user_pixel[0]+10, user_pixel[1]+10),
                            fill="red")
                buf = io.BytesIO()
                
                img.save(buf, format="PNG")
                return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"
            except FileNotFoundError:
                ui.notify("Lỗi: Không tìm thấy file ảnh 'khuonvientruong.jpg'!", type='negative')
                return ""
            
        # --- UI Controller (Card điều khiển) ---
        # with ui.card().classes('w-full max-w-[1200px] p-6 mb-6 bg-white shadow-md rounded-lg'):
        #     with ui.row().classes("w-full justify-center gap-6 md:gap-12"):
        #         start_sel = ui.select(options=list(visible_locations.keys()), value="BETA BUILDING", label="📍 Điểm bắt đầu") \
        #             .classes('w-full md:w-1/3').props('outlined dense options-dense input-class="text-lg" label-class="text-lg"')
        #         ui.icon('arrow_forward', size='3em').classes('text-gray-400 self-center hidden md:block')
        #         end_sel = ui.select(options=list(visible_locations.keys()), value="BETA BUILDING", label="🏁 Điểm đến") \
        #             .classes('w-full md:w-1/3').props('outlined dense options-dense input-class="text-lg" label-class="text-lg"')
        #     btn_goto_beta = ui.button("🏢 CHUYỂN SANG SƠ ĐỒ TÒA BETA",
        #                                 on_click=lambda: ui.navigate.to('/beta')) \
        #                         .classes('w-full md:w-2/3 self-center bg-green-600 text-white text-lg font-bold animate-bounce')
        #     btn_goto_beta.visible = False
        zoom_level = 1.0
        with ui.card().classes('w-full max-w-[1200px] p-6 mb-6 bg-white shadow-md rounded-lg'):
            with ui.row().classes("w-full justify-center gap-6 md:gap-12"):
                # start_sel = ui.select(
                #     options=list(visible_locations.keys()),
                #     value = "BETA BUILDING",
                #     label="📍 Điểm bắt đầu"
                # ).classes('w-full md:w-1/3 text-sm py-1')

                ui.icon('arrow_forward', size='3em').classes('text-gray-400 self-center hidden md:block')

                end_sel = ui.select(
                    options=list(visible_locations.keys()),
                    value="BETA BUILDING",
                    label="🏁 Điểm đến"
                ).classes('w-full md:w-1/3 text-sm py-1')

            # 👇 NÚT Ở NGOÀI – LUÔN ĐƯỢC TẠO
            btn_goto_beta = ui.button(
                "🏢 CHUYỂN SANG SƠ ĐỒ TÒA BETA",
                on_click=lambda: ui.navigate.to('/beta')
            ).classes('w-full md:w-2/3 self-center bg-green-600 text-white text-base font-bold py-2')
                    # 2.5. KHUNG CHÚ THÍCH (LEGEND)
            # ===== KHUNG CHÚ THÍCH (NẰM NGOÀI – KHÔNG CHỒNG ẢNH) =====
        with ui.card().classes(
            'w-full max-w-[1200px] '
            'mb-3 px-4 py-3 '
            'bg-white shadow rounded-xl'
        ):
            ui.label("🗺️ CHÚ THÍCH").classes('font-bold text-gray-700 text-sm mb-2')

            with ui.row().classes('gap-6 flex-wrap'):
                with ui.row().classes('items-center gap-2'):
                    ui.element('div').classes('w-4 h-4 rounded-full bg-blue-600')
                    ui.label("Điểm đi").classes('text-gray-700 text-xs md:text-sm')

                with ui.row().classes('items-center gap-2'):
                    ui.element('div').classes('w-4 h-4 rounded-full bg-green-600')
                    ui.label("Điểm đến").classes('text-gray-700 text-xs md:text-sm')

                with ui.row().classes('items-center gap-2'):
                    ui.element('div').classes('w-4 h-4 rounded-full bg-red-600')
                    ui.label("Điểm hiện tại").classes('text-gray-700 text-xs md:text-sm')

        # --- KHUNG HIỂN THỊ BẢN ĐỒ (Overlay) ---
        with ui.element('div').classes(
            'relative w-full max-w-[1200px] '
            'h-[800px] border-4 border-white shadow-xl rounded-xl overflow-auto bg-gray-200'
        ):
            # image_view = ui.image().classes(
            #     'w-full h-auto object-contain'
            # ).style(
            #     'transform: scale(1.2); transform-origin: top left; transition: transform 0.2s ease;'
            # )

                        # 3. CỤM NÚT ZOOM VÀ HIỂN THỊ TỶ LỆ
            with ui.column().classes('sticky bottom-4 left-4 z-20 gap-2'): 
                with ui.button_group().classes('shadow-lg bg-white'):
                    ui.button(icon='add', on_click=lambda: adjust_zoom(0.2)).props('dense color=blue-700').tooltip('Phóng to')
                    ui.button(icon='remove', on_click=lambda: adjust_zoom(-0.2)).props('dense color=blue-700').tooltip('Thu nhỏ')      
                lbl_zoom = ui.label('120%').classes('bg-white/80 px-2 rounded text-xs font-bold text-center shadow')
            # 1. Ảnh bản đồ
            image_view = ui.image().classes('w-full h-auto object-contain')\
                .style('transform: scale(1.2); transform-origin: top left; transition: transform 0.2s ease;')
            # 2. Nhãn thông báo 
            distance_label = ui.label().classes(
                'absolute top-4 right-4 z-10 '
                'text-xl md:text-2xl font-bold '
                'px-6 py-3 rounded-full shadow-lg transition-all duration-300' )


        def adjust_zoom(delta):
            nonlocal zoom_level # Dùng nonlocal để sửa biến zoom_level ở ngoài hàm
            zoom_level = max(1.0, min(3.0, zoom_level + delta)) # Giới hạn zoom từ 100% đến 300%
            image_view.style(f'transform: scale({zoom_level}); transform-origin: top left; transition: transform 0.2s ease;')
            lbl_zoom.text = f"{int(zoom_level * 100)}%"
        # --- Hàm cập nhật đường đi (giữ nguyên logic cũ) ---
        def update_path():
            if user_lat is None or user_lon is None:
                return
            end = end_sel.value

            # GPS → pixel
            user_pixel = gps_to_pixel(user_lat, user_lon)

            # Snap GPS → node gần nhất
            start = snap_to_nearest_node(user_pixel)

            if not start or not end:
                return

            if start == end:
                image_view.source = draw_path([start])
                return

            path, dist = find_shortest_path(start, end)
            image_view.source = draw_path(path, user_pixel)


            if not path:
                distance_label.text = "🚫 Không tìm thấy đường đi!"
                distance_label.classes(remove='bg-blue-600/90', add='text-white bg-red-600/90')

        # Binding sự kiện
        # start_sel.on_value_change(update_path)
        end_sel.on_value_change(update_path)
        
        # Chạy lần đầu
        update_path()