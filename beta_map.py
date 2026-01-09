from nicegui import ui
import networkx as nx
from PIL import Image, ImageDraw
import io, base64
import random 
import math

@ui.page('/campus')
def campus_page():
    ui.label("🗺️ ĐÂY LÀ BẢN ĐỒ TOÀN KHUÔN VIÊN (CAMPUS)").classes('text-4xl text-blue-600')
    ui.button("Quay lại Tòa nhà", on_click=lambda: ui.navigate.to('/')).classes('mt-4')
count=0
def create_page():
    # --- UI GÓC PHẢI MÀN HÌNH: TRẠNG THÁI THANG MÁY ---
    # Biến lưu trạng thái thang máy
    elevator_state = {'current_floor': 'Floor 1'} 
    
    # Thẻ hiển thị cố định (z-index cao để nổi lên trên)
    with ui.card().classes('fixed top-4 right-4 z-50 bg-yellow-100 border-2 border-orange-400 shadow-lg'):
        with ui.row().classes('items-center'):
            ui.label('🛗').classes('text-l')
            with ui.column().classes('gap-0'):
                ui.label('Thang máy đang ở:').classes('text-xs text-gray-500')
                # Bind text để khi biến thay đổi, giao diện tự cập nhật
                lbl_elev_floor = ui.label(elevator_state['current_floor']).classes('font-bold text-orange-700 text-l')

    # --- UI CHÍNH ---
    ui.button("⬅ Quay lại Menu", on_click=lambda: ui.navigate.to('/')).classes('mb-4 bg-gray-500 text-white')
    ui.label("🏢 BẢN ĐỒ TÒA BETA (5 TẦNG)").classes("text-1xl font-bold text-green-600 mb-4")

    FLOOR_PLANS = {
        "Floor 1": "floor1.PNG", "Floor 2": "floor2.PNG", "Floor 3": "floor3.PNG",
        "Floor 4": "floor4.PNG", "Floor 5": "floor5.PNG"
    }

    # --- TỌA ĐỘ & GRAPH (Giữ nguyên như cũ) ---
    f1_loc = {"EXTRA FRONT": (520, 1000), "STAIRS_F1_A": (900, 500),"STAIRS_F1_B": (240, 500), "LAB AI": (890, 290),
              "IT SP": (803, 351), "MEETING ROOM": (798, 608), "STUDENTS SP": (682, 753), "BRONZE DRUM": (520, 800), "ADMISSIONS OFFICE": (370, 900),
              "WC FEMALE (F1)": (236, 400), "WC MALE (F1)":  (238, 584), "EXTRA BACK": (126, 290), "F1_2": (800, 300), "F1_1": (795, 497), "F1_3": (677, 679),"MAIN HALL":(520,650),
              "F1_4": (379, 680), "F1_5": (275, 315), "LIBRARY": (275, 315),"ELEVATOR_1":(745,500) }
    f2_loc = { "201": (245, 165), "202": (510 , 200), "203": (780, 165)
                , "204": (780, 50), "205": (780, 100), "206": (780, 225), "207": (950, 270), "208": (830, 270), "209":(950, 695)
                , "210": (830, 695), "211": (780, 750), "212": (780, 895), "213": (780, 950), "214": (780, 825), "215": (510, 750)
                , "216": (245, 825), "217": (245, 950), "218": (245, 895), "219": (245, 750), "220": (245, 225),"WC MALE (F2)": (245, 600), "WC FEMALE (F2)": (245, 380)
                , "ELEVATOR_2": (750, 500), "STAIRS_F2_B": (780, 500), "STAIRS_F2_A": (245, 500), "F2_1": (245, 270), "F2_2": (510, 270), "F2_3": (780, 270)
                ,"F2_4": (830, 695), "F2_5": (510, 695), "F2_6": (245, 659)}
    f3_loc = { "301": (167, 777), "302": (199 , 511), "303": (161, 246)
                , "304": (48, 246), "305": (100, 246), "306": (225, 246), "307": (270, 69), "308": (270, 190), "309":(700, 70)
                , "310": (700, 191), "311": (741, 246), "312": (895, 246), "313": (950, 246), "314": (828, 246), "315": (788, 502)
                , "316": (822, 777), "317": (952, 777), "318": (895, 777), "319": (745, 777), "320": (233, 770), "WC MALE (F3)": (603, 777), "WC FEMALE (F3)": (376, 777)
                , "ELEVATOR_3": (495, 246), "STAIRS_F3_B": (495, 777), "STAIRS_F3_A": (495, 180), "F3_1": (270, 777), "F3_2": (270, 500), "F3_3": (270, 246)
                ,"F3_4": (697, 246), "F3_5": (700, 503), "F3_6": (695, 777)}    
    f4_loc = { "401": (167, 777), "402": (199 , 511), "403": (161, 246)
                , "404": (48, 246), "405": (100, 246), "406": (225, 246), "407": (270, 69), "408": (270, 190), "409":(700, 70)
                , "410": (700, 191), "411": (741, 246), "412": (895, 246), "413": (950, 246), "414": (828, 246), "415": (788, 502)
                , "416": (822, 777), "417": (952, 777), "418": (895, 777), "419": (745, 777), "420": (233, 770), "WC MALE (F4)": (603, 777), "WC FEMALE (F4)": (376, 777)
                , "ELEVATOR_4": (495, 246), "STAIRS_F4_B": (495, 777), "STAIRS_F4_A": (495, 180), "F4_1": (270, 777), "F4_2": (270, 500), "F4_3": (270, 246)
                ,"F4_4": (697, 246), "F4_5": (700, 503), "F4_6": (695, 777)}
    f5_loc = {"501": (361, 282), "502": (415, 251), "503": (688, 251), "504": (732, 282), "505": (361, 282),"506": (859, 282), "507": (804, 282),
              "508": (753, 469), "509": (758, 571), "510": (806, 765), "511": (907, 765), "512": (806, 765), "513": (732, 765), "WC MALE (F5)": (600, 765),
              "WC FEMALE (F5)": (407, 765), "514": (320, 765),"515": (105, 765),"516": (200, 765), "STAIRS_F5_B": (505, 831),
              "ELEVATOR_5": (505, 282), "STAIRS_F5_A": (504, 232), "F5_1": (689, 282), "F5_2": (689, 765), "F5_3": (505, 765), "F5_4": (689, 470), "F5_5": (689, 571)}
    all_floors = { "Floor 1": f1_loc, "Floor 2": f2_loc, "Floor 3": f3_loc, "Floor 4": f4_loc, "Floor 5": f5_loc }

    G = nx.Graph()
    def dist(p1, p2): return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5 

    # Nối Tầng 1
    list_edges_f1 = [("EXTRA FRONT", "BRONZE DRUM"), ("BRONZE DRUM", "ADMISSIONS OFFICE"), ("BRONZE DRUM", "STUDENTS SP"),
                ("MAIN HALL", "BRONZE DRUM"), ("MAIN HALL", "WC MALE (F1)"), ("MAIN HALL", "WC FEMALE (F1)"),
                ("MAIN HALL", "MEETING ROOM"), ("MAIN HALL", "ADMISSIONS OFFICE"), ("MAIN HALL", "STUDENTS SP"),
                ("MAIN HALL", "LIBRARY"), ("MEETING ROOM", "F1_1"), ("F1_1", "ELEVATOR_1"),("F1_1", "STAIRS_F1_A"),
                ("LIBRARY","EXTRA BACK"),
                ("IT SP", "LIBRARY"), ("IT SP", "F1_1"), ("IT SP", "F1_2"),("LAB AI", "F1_2"),("LIBRARY", "F1_2"),
                ("IT SP", "WC MALE (F1)"),("IT SP", "WC FEMALE (F1)"),("F1_2", "WC MALE (F1)"),("F1_2", "WC FEMALE (F1)"),
                ("LIBRARY", "WC MALE (F1)"),("LIBRARY", "WC FEMALE (F1)"),("MAIN HALL", "F1_3"),("MEETING ROOM", "F1_3"),
                ("STUDENTS SP", "F1_3"),("BRONZE DRUM", "F1_3"),("F1_4", "F1_3"),("MAIN HALL", "F1_4"),
                ("WC MALE (F1)", "F1_4"),("LIBRARY", "F1_4"),("STUDENTS SP", "F1_4"),("BRONZE DRUM", "F1_4"),("EXTRA FRONT", "F1_4"),
                ("F1_4", "STAIRS_F1_B"),("WC MALE (F1)", "STAIRS_F1_B"),("WC FEMALE (F1)", "STAIRS_F1_B"),("MAIN HALL", "STAIRS_F1_B"),("F1_3", "STAIRS_F1_B"),("LIBRARY", "STAIRS_F1_B"),
                ("F1_2", "STAIRS_F1_B"),("IT SP", "STAIRS_F1_B"),("F1_4","ADMISSIONS OFFICE"),
                ("MAIN HALL", "LIBRARY"), ("MEETING ROOM", "F1_1"), ("F1_1", "ELEVATOR_1"),("F1_1", "STAIRS_F1_A")]    
    for u,v in list_edges_f1: 
        G.add_edge(u, v, weight=dist(f1_loc[u], f1_loc[v]), type='walk')

    # Nối Tầng 2 (Đã sửa lỗi mất nét)
    list_edges_f2 = [('201','220'),('220','F2_1'), ('F2_1','WC FEMALE (F2)', ), ('WC FEMALE (F2)','STAIRS_F2_B'), ('STAIRS_F2_B','WC MALE (F2)'), ('WC MALE (F2)','219'), ('219','216'),
                ('216','218'), ('218','217'), ('WC MALE (F2)','F2_6'), ('F2_1','F2_2'), ('F2_2','202'), ('F2_2','F2_3'), ('F2_3','208'),
                ('208','207'), ('F2_3','206'), ('206','203'), ('203','205'), ('205','204'), ('F2_3','ELEVATOR_2'), ('ELEVATOR_2','STAIRS_F2_A'), ('ELEVATOR_2','F2_4'),
               ('F2_4', '210'), ('210','209'), ('F2_4','211'), ('211','214'), ('214','212'), ('212','213'), ('F2_4','F2_5'), ('F2_5','215'), ('F2_5','F2_6')
                ]
    for u, v in list_edges_f2: 
        if u in f2_loc and v in f2_loc: 
            G.add_edge(u, v, weight=dist(f2_loc[u], f2_loc[v]), type='walk')

    # Nối Tầng 3
    list_edges_f3 = [('301','320'),('320','F3_1'), ('F3_1','WC FEMALE (F3)', ), ('WC FEMALE (F3)','STAIRS_F3_B'), ('STAIRS_F3_B','WC MALE (F3)'), ('WC MALE (F3)','319'), ('319','316'),
                ('316','318'), ('318','317'), ('WC MALE (F3)','F3_6'), ('F3_1','F3_2'), ('F3_2','302'), ('F3_2','F3_3'), ('F3_3','308'),
                ('308','307'), ('F3_3','306'), ('306','303'), ('303','305'), ('305','304'), ('F3_3','ELEVATOR_3'), ('ELEVATOR_3','STAIRS_F3_A'), ('ELEVATOR_3','F3_4'),
               ('F3_4', '310'), ('310','309'), ('F3_4','311'), ('311','314'), ('314','312'), ('312','313'), ('F3_4','F3_5'), ('F3_5','315'), ('F3_5','F3_6')]
    for u, v in list_edges_f3: 
        if u in f3_loc and v in f3_loc: 
            G.add_edge(u, v, weight=dist(f3_loc[u], f3_loc[v]), type='walk')
    # Nối tầng 4
    list_edges_f4 = [('401','420'),('420','F4_1'), ('F4_1','WC FEMALE (F4)', ), ('WC FEMALE (F4)','STAIRS_F4_B'), ('STAIRS_F4_B','WC MALE (F4)'), ('WC MALE (F4)','419'), ('419','416'),
                ('416','418'), ('418','417'), ('WC MALE (F4)','F4_6'), ('F4_1','F4_2'), ('F4_2','402'), ('F4_2','F4_3'), ('F4_3','408'),
                ('408','407'), ('F4_3','406'), ('406','403'), ('403','405'), ('405','404'), ('F4_3','ELEVATOR_4'), ('ELEVATOR_4','STAIRS_F4_A'), ('ELEVATOR_4','F4_4'),
               ('F4_4', '410'), ('410','409'), ('F4_4','411'), ('411','414'), ('414','412'), ('412','413'), ('F4_4','F4_5'), ('F4_5','415'), ('F4_5','F4_6'),('401','WC MALE (F4)')]
    for u, v in list_edges_f4: 
        if u in f4_loc and v in f4_loc: 
            G.add_edge(u, v, weight=dist(f4_loc[u], f4_loc[v]), type='walk')
    # Nối tầng 5
    list_edges_f5 = [('501','502'),('501','ELEVATOR_5'), ('ELEVATOR_5','STAIRS_F5_A', ), ('ELEVATOR_5','F5_1'), ('F5_1','503'), ('F5_1','504'), ('504','507'),
                ('507','505'), ('505','506'), ('F5_1','F5_4'), ('F5_4','F5_5'), ('F5_4','508'), ('F5_5','509'), ('F5_5','F5_2'),
                ('F5_2','513'), ('513','510'), ('510','512'), ('512','511'), ('F5_2','504'), ('F5_2','WC MALE (F5)'), ('WC MALE (F5)','F5_3'), ('F5_3','WC FEMALE (F5)'), ('WC FEMALE (F5)','514'),
               ('514', '516'), ('516','515'),('502','ELEVATOR_5'),('STAIRS_F5_B','F5_3')]
    for u, v in list_edges_f5: 
        if u in f5_loc and v in f5_loc: 
            G.add_edge(u, v, weight=dist(f5_loc[u], f5_loc[v]), type='walk')
    # Nối Trục Dọc
    for i in range(1, 5):
        G.add_edge(f"STAIRS_F{i}_A", f"STAIRS_F{i+1}_A", weight=50, type='stair')
        G.add_edge(f"STAIRS_F{i}_B", f"STAIRS_F{i+1}_B", weight=50, type='stair')
        G.add_edge(f"ELEVATOR_{i}", f"ELEVATOR_{i+1}", weight=10, type='elevator')

    # --- HÀM VẼ (Ẩn chữ Elevator) ---

    def draw_dashed_line(draw, p1, p2, dash_len=20, gap_len=15, fill="red", width=10):
        x1, y1 = p1
        x2, y2 = p2

        dx = x2 - x1
        dy = y2 - y1
        dist = math.hypot(dx, dy)

        if dist == 0:
            return

        vx = dx / dist
        vy = dy / dist

        pos = 0
        while pos < dist:
            start = pos
            end = min(pos + dash_len, dist)

            sx = x1 + vx * start
            sy = y1 + vy * start
            ex = x1 + vx * end
            ey = y1 + vy * end

            draw.line([(sx, sy), (ex, ey)], fill=fill, width=width)
            pos += dash_len + gap_len

# --- HÀM VẼ (Đã sửa: Chỉ hiện điểm Đầu/Cuối/Thang trên lộ trình) ---
    def draw_smart(path, floor_name):
        try:
            img = Image.open(FLOOR_PLANS[floor_name]).convert("RGB")
            draw = ImageDraw.Draw(img)
            coord = all_floors[floor_name]

            # Lọc ra các điểm thuộc tầng này có trong lộ trình
            nodes_on_floor = [n for n in path if n in coord]

            # --- BƯỚC 1: VẼ ĐƯỜNG NỐI (Vẽ trước để nằm dưới) ---
            for i in range(len(path)-1):
                u, v = path[i], path[i+1]
                if u in coord and v in coord:
                    # Vẽ đường nối màu đỏ
                    draw_dashed_line(
                            draw,
                            coord[u],
                            coord[v],
                            dash_len=25,   # độ dài nét
                            gap_len=15,    # khoảng trống
                            fill="red",
                            width=10
                        )
            # --- BƯỚC 2: VẼ CÁC ĐIỂM QUAN TRỌNG (Vẽ đè lên trên) ---
            for node in nodes_on_floor:
                x, y = coord[node]
                
                # Xác định xem điểm này là gì?
                is_start = (node == path[0])   # Là điểm bắt đầu hành trình?
                is_end = (node == path[-1])    # Là điểm kết thúc hành trình?
                is_stair = "STAIRS" in node    # Là cầu thang?
                is_elev = "ELEVATOR" in node   # Là thang máy?

                # Chỉ vẽ nếu nó là 1 trong 4 loại trên
                if is_start or is_end or is_stair or is_elev:
                    
                    # Chọn màu sắc cho dễ nhìn
                    if is_start:
                        fill_color = "#00FF00" # Xanh lá (Start)
                        text_label = f""
                        size = 20 # Điểm to
                    elif is_end:
                        fill_color = "#FF0000" # Đỏ (End)
                        text_label = f""
                        size = 20
                    elif is_elev:
                        fill_color = "#9b59b6" # Tím (Thang máy)
                        text_label = node
                        size = 15
                    else: # Cầu thang
                        fill_color = "#e67e22" # Cam (Cầu thang)
                        text_label = node
                        size = 15

                    # Vẽ chấm tròn
                    draw.ellipse((x-size, y-size, x+size, y+size), fill=fill_color, outline="white", width=3)
                    
                    # Vẽ chữ tên điểm (Màu đen cho dễ đọc, có viền trắng nhẹ nếu cần)
                    # Vẽ chữ lệch lên trên một chút
                    draw.text((x-80, y-50), text_label, fill="black", font_size=30, stroke_width=2, stroke_fill="white")

            buf = io.BytesIO(); img.save(buf, format="PNG")
            return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"
        except Exception as e:
            print(e)
            return ""

    # --- UI CONTROL ---
    rooms_db = {
        "Floor 1": ["EXTRA FRONT", "STAIRS_F1_A", "LAB AI", "IT SP", "MEETING ROOM", "STUDENTS SP", "BRONZE DRUM", "ADMISSIONS OFFICE", "WC MALE (F1)", "WC FEMALE (F1)", "LIBRARY","STAIRS_F1_B" , "MAIN HALL", "EXTRA BACK", "ELEVATOR_1"],
        "Floor 2": ["201", "202", "203", "204", "205", "206", "207", "208", "209","210", "211", "212", "213", "214", "215", "216", "217", "218", "219", "220", "WC MALE (F2)", "WC FEMALE (F2)", "ELEVATOR_2", "STAIRS_F2_A","STAIRS_F2_B"],
        "Floor 3": ["301", "302", "303", "304", "305", "306", "307", "308", "309","310", "311", "312", "313", "314", "315", "316", "317", "318","319", "320", "WC MALE (F3)", "WC FEMALE (F3)", "ELEVATOR_3","STAIRS_F3_B", "STAIRS_F3_A"],
        "Floor 4": ["401", "402", "403", "404", "405", "406", "407", "408", "409","410", "411", "412", "413", "414", "415", "416", "417", "418","419", "420", "WC MALE (F4)", "WC FEMALE (F4)", "ELEVATOR_4","STAIRS_F4_B", "STAIRS_F4_A"],
        "Floor 5": ["501", "502", "503", "504", "505", "506", "507", "508", "509", "510", "511", "512", "513", "515", "515", "516","WC MALE (F5)", "WC FEMALE (F5)", "ELEVATOR_5","STAIRS_F5_B", "STAIRS_F5_A" ]
    }
    floor_list = list(rooms_db.keys())

    with ui.card().classes('w-full p-4 bg-gray-50'):
        # --- LOGIC RANDOM MỚI ---
        def random_route():
            # 1. Random thang máy (Để mô phỏng thực tế)
            elevator_state['current_floor'] = random.choice(floor_list)
            lbl_elev_floor.text = elevator_state['current_floor'] 
            ui.notify(f"🛗 Thang đang ở {elevator_state['current_floor']}.", type='positive')
            
        # ui.button("🎲 Random Vị Trí Thang Máy", on_click=random_route).classes('w-full bg-purple-600 text-white mb-4')

        with ui.row().classes("gap-8 w-full justify-center" ):
            
            # --- CỘT ĐIỂM ĐI ---
            with ui.column().classes('items-center'):
                ui.label("📍 ĐIỂM ĐI").classes('font-bold text-blue-600 text-sm')
                s_floor = ui.select(floor_list, value="Floor 1", label="Tầng") \
                    .classes('text-sm w-35') \
                    .props('input-class="text-xl" popup-content-class="text-sm"')
                s_room = ui.select(rooms_db["Floor 1"], value="EXTRA FRONT", label="Phòng") \
                    .classes('text-sm w-35') \
                    .props('input-class="text-xl" popup-content-class="text-sm"')

            # --- CỘT ĐIỂM ĐẾN ---
            with ui.column().classes('items-center'):
                ui.label("🏁 ĐIỂM ĐẾN").classes('font-bold text-red-600 text-sm')
                e_floor = ui.select(floor_list, value="Floor 1", label="Tầng") \
                    .classes('text-sm w-35') \
                    .props('input-class="text-xl" popup-content-class="text-sm"')
                e_room = ui.select(rooms_db["Floor 1"], value="EXTRA FRONT", label="Phòng") \
                    .classes('text-sm w-35') \
                    .props('input-class="text-xl" popup-content-class="text-sm"')

    btn_campus = ui.button("🌍 RA KHỎI TÒA NHÀ -> SANG CAMPUS MAP", 
                           on_click=lambda: ui.navigate.to('/campus')) \
                   .classes('w-full mt-4 bg-red-600 text-white text-l font-bold animate-pulse')
    # btn_campus.visible = False
    result_card = ui.card().classes('w-full p-2 bg-white border-2 border-gray-200 mt-4')
    with ui.card().classes(
            'w-fit p-3 mt-4 bg-white border border-gray-300 shadow-md rounded-xl'
    ):
        ui.label("📝 CHÚ THÍCH").classes('font-bold text-gray-700 mb-2')

        with ui.row().classes('items-center gap-3'):
            ui.element('div').classes('w-4 h-4 rounded-full bg-green-500')
            ui.label("Điểm đi").classes('text-sm')

        with ui.row().classes('items-center gap-3 mt-1'):
            ui.element('div').classes('w-4 h-4 rounded-full bg-red-500')
            ui.label("Điểm đến").classes('text-sm')

    image_container = ui.row().classes('w-full justify-center gap-4')

    # --- HÀM TÍNH THỜI GIAN (Có tính vị trí thang máy) ---
    def calculate_time_logic(path, graph_source):
        time = 0
        floors_vertical = 0
        used_elevator = False
        
        for i in range(len(path)-1):
            u, v = path[i], path[i+1]
            edge = graph_source.get_edge_data(u, v)
            etype = edge.get('type', 'walk')
            dist = edge.get('weight', 0)

            if etype == 'walk': time += dist / 150
            elif etype == 'stair': time += 20
            elif etype == 'elevator': 
                floors_vertical += 1
                used_elevator = True
        
        if used_elevator and floors_vertical > 0:
            # 1. Tính khoảng cách từ tầng thang máy đang đứng -> tầng người dùng đang đứng
            # Lấy số tầng (VD: "Floor 5" -> 5)
            elev_f_num = int(elevator_state['current_floor'].split()[-1])
            user_f_num = int(s_floor.value.split()[-1])
            
            # Thời gian thang di chuyển đến chỗ bạn (5s/tầng) + 10s mở cửa đón
            wait_time = (abs(elev_f_num - user_f_num) * 5) + 10
            
            # Thời gian di chuyển của bạn + wait_time
            time += (floors_vertical * 5) + wait_time
            
        return time

    def update():
        if not s_room.value or not e_room.value: return
        start, end = s_room.value, e_room.value
        global count
        try:
            G_stair = G.copy(); G_stair.remove_edges_from([(u,v) for u,v,d in G.edges(data=True) if d.get('type') == 'elevator'])
            try: p_stair = nx.shortest_path(G_stair, start, end, weight='weight'); t_stair = calculate_time_logic(p_stair, G_stair)
            except: p_stair = None; t_stair = float('inf')

            G_elev = G.copy(); G_elev.remove_edges_from([(u,v) for u,v,d in G.edges(data=True) if d.get('type') == 'stair'])
            try: p_elev = nx.shortest_path(G_elev, start, end, weight='weight'); t_elev = calculate_time_logic(p_elev, G_elev)
            except: p_elev = None; t_elev = float('inf')

            # result_card.clear()
            # with result_card:
            #     ui.label(f"⏱️ SO SÁNH (Thang đang ở {elevator_state['current_floor']})").classes('text-lg font-bold')
            #     with ui.row().classes('gap-10'):
            #         txt_stair = f"{t_stair:.1f}s" if t_stair != float('inf') else "N/A"
            #         txt_elev = f"{t_elev:.1f}s" if t_elev != float('inf') else "N/A"
            #         ui.label(f"🏃 Thang bộ: {txt_stair}").classes('text-blue-600')
            #         ui.label(f"🛗 Thang máy: {txt_elev}").classes('text-purple-600')
            #
            #     if t_elev < t_stair:
            #         ui.label("💡 GỢI Ý: Đi THANG MÁY!").classes('text-green-600 font-bold text-xl')
            #         final_path = p_elev
            #     else:
            #         ui.label("💡 GỢI Ý: Đi THANG BỘ!").classes('text-green-600 font-bold text-xl')
            #         final_path = p_stair
            if t_elev < t_stair:
                final_path = p_elev
            else:
                final_path = p_stair
            if count==4:
                count=0
                random_route()
            else:
                count+=1
            image_container.clear()
            if final_path:
                with image_container:
                    if s_floor.value == e_floor.value: ui.image(draw_smart(final_path, s_floor.value)).style("width:600px")
                    else:
                        with ui.column().classes('items-center'): 
                            ui.label(f"Start: {s_floor.value}").classes('text-l font-bold text-blue-600 mb-2')
                            ui.image(draw_smart(final_path, s_floor.value)).style("width:400px")
                        
                        ui.icon('arrow_forward', size='1em').classes('self-center text-gray-400 mx-4')
                        
                        with ui.column().classes('items-center'):
                            ui.label(f"End: {e_floor.value}").classes('text-l font-bold text-red-600 mb-2')
                            ui.image(draw_smart(final_path, e_floor.value)).style("width:400px")
        except Exception as e: ui.notify(f"Lỗi: {str(e)}")

    def update_s_list(): s_room.options = rooms_db[s_floor.value]; s_room.value = s_room.options[0]; update()
    def update_e_list(): e_room.options = rooms_db[e_floor.value]; e_room.value = e_room.options[0]; update()
    s_floor.on_value_change(update_s_list); e_floor.on_value_change(update_e_list)
    s_room.on_value_change(update); e_room.on_value_change(update)
    update()