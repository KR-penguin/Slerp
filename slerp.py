# slerp_pygame.py
# 실행 전: pip install pygame
import math
import random
import pygame

WIDTH, HEIGHT = 800, 800
BG = (250, 250, 250)
COL_AXIS = (210, 210, 210)
COL_A = (220, 0, 0)
COL_B = (0, 100, 220)
COL_LERP = (180, 120, 0)
COL_SLERP = (0, 180, 80)
COL_TEXT = (40, 40, 40)

# --------- 수학 유틸 (2D & 3D) ----------
def dot(a, b):
    if len(a) == 2:
        return a[0]*b[0] + a[1]*b[1]
    else:  # 3D
        return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def length(v):
    if len(v) == 2:
        return math.hypot(v[0], v[1])
    else:  # 3D
        return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

def normalize(v):
    l = length(v)
    if l < 1e-12:
        if len(v) == 2:
            return (1.0, 0.0)
        else:
            return (1.0, 0.0, 0.0)
    if len(v) == 2:
        return (v[0]/l, v[1]/l)
    else:
        return (v[0]/l, v[1]/l, v[2]/l)

def add(a, b):
    if len(a) == 2:
        return (a[0]+b[0], a[1]+b[1])
    else:
        return (a[0]+b[0], a[1]+b[1], a[2]+b[2])

def mul(v, s):
    if len(v) == 2:
        return (v[0]*s, v[1]*s)
    else:
        return (v[0]*s, v[1]*s, v[2]*s)

def lerp(a, b, t):
    return add(mul(a, 1.0 - t), mul(b, t))

def slerp(a_in, b_in, t):
    # 단위 벡터 보장
    a = normalize(a_in)
    b = normalize(b_in)
    d = max(-1.0, min(1.0, dot(a, b)))
    theta = math.acos(d)
    s = math.sin(theta)
    if s < 1e-6:
        # 각이 매우 작으면 LERP 근사
        return normalize(lerp(a, b, t))
    s1 = math.sin((1.0 - t)*theta) / s
    s2 = math.sin(t*theta) / s
    return add(mul(a, s1), mul(b, s2))

# --------- 화면 유틸 (2D & 3D 투영) ----------
def world_to_screen_2d(v, cx, cy, radius):
    # 수학: +y 위 / 화면: +y 아래 → y축 반전
    x = cx + v[0]*radius
    y = cy - v[1]*radius
    return (int(round(x)), int(round(y)))

def world_to_screen_3d(v, cx, cy, radius, rot_x, rot_y):
    """3D 벡터를 2D 화면 좌표로 투영 (회전 포함)"""
    # Y축 회전
    cos_y, sin_y = math.cos(rot_y), math.sin(rot_y)
    x1 = v[0] * cos_y - v[2] * sin_y
    y1 = v[1]
    z1 = v[0] * sin_y + v[2] * cos_y
    
    # X축 회전
    cos_x, sin_x = math.cos(rot_x), math.sin(rot_x)
    x2 = x1
    y2 = y1 * cos_x - z1 * sin_x
    z2 = y1 * sin_x + z1 * cos_x
    
    # 간단한 원근 투영 (거리에 따른 스케일링)
    distance = 3.0  # 카메라 거리
    scale = radius / (distance + z2)
    
    x = cx + x2 * scale
    y = cy - y2 * scale
    return (int(round(x)), int(round(y)))

def draw_arrow(surf, center, end_pt, color, width=3):
    pygame.draw.line(surf, color, center, end_pt, width)
    # 간단한 화살촉
    dx = end_pt[0]-center[0]
    dy = end_pt[1]-center[1]
    d = math.sqrt(dx*dx + dy*dy)
    if d < 1: return
    ang = math.atan2(dy, dx)
    L = 12
    a1 = (end_pt[0] - L*math.cos(ang - math.pi/8),
          end_pt[1] - L*math.sin(ang - math.pi/8))
    a2 = (end_pt[0] - L*math.cos(ang + math.pi/8),
          end_pt[1] - L*math.sin(ang + math.pi/8))
    pygame.draw.line(surf, color, end_pt, a1, width)
    pygame.draw.line(surf, color, end_pt, a2, width)

def random_unit_vec_2d():
    ang = random.random()*2*math.pi
    return (math.cos(ang), math.sin(ang))

def random_unit_vec_3d():
    # 구면 위의 균등 분포
    theta = random.random() * 2 * math.pi
    z = random.random() * 2 - 1
    r = math.sqrt(1 - z*z)
    return (r * math.cos(theta), r * math.sin(theta), z)

def show_menu():
    """시작 메뉴 표시"""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SLERP Demo - Select Mode")
    # 여러 폰트 후보 중 사용 가능한 것 선택
    font_title = pygame.font.SysFont("consolas,courier,monospace", 36, bold=True)
    font_option = pygame.font.SysFont("consolas,courier,monospace", 24)
    
    selected = None
    while selected is None:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_2:
                    selected = "2D"
                elif e.key == pygame.K_3:
                    selected = "3D"
        
        screen.fill(BG)
        
        # 제목
        title = font_title.render("SLERP Visualization", True, COL_TEXT)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        
        # 옵션
        opt1 = font_option.render("Press [2] for 2D Mode", True, COL_A)
        opt2 = font_option.render("Press [3] for 3D Mode", True, COL_B)
        
        screen.blit(opt1, (WIDTH//2 - opt1.get_width()//2, 320))
        screen.blit(opt2, (WIDTH//2 - opt2.get_width()//2, 360))
        
        pygame.display.flip()
    
    return selected

def main():
    # 모드 선택
    mode = show_menu()
    if mode is None:
        return
    
    is_3d = (mode == "3D")
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    title = f"SLERP vs LERP ({mode}) - Space: toggle LERP, R: random A/B"
    if is_3d:
        title += ", Arrows: rotate"
    else:
        title += ", ←/→: speed"
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()
    # 여러 폰트 후보 중 사용 가능한 것 선택
    font = pygame.font.SysFont("consolas,courier,monospace", 18)

    cx, cy = WIDTH//2, HEIGHT//2
    radius = min(WIDTH, HEIGHT)//2 - 40

    # 초기 두 방향
    if is_3d:
        A = (1.0, 0.0, 0.0)
        B = (0.0, 1.0, 0.0)
        rot_x = 0.3  # 초기 회전각
        rot_y = 0.5
    else:
        A = (1.0, 0.0)
        B = (0.0, 1.0)
        rot_x = rot_y = 0

    t = 0.0
    dir_sign = 1.0
    speed = 0.75   # t/초
    show_lerp = True

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    show_lerp = not show_lerp
                elif e.key == pygame.K_r:
                    if is_3d:
                        A = random_unit_vec_3d()
                        B = random_unit_vec_3d()
                    else:
                        A = random_unit_vec_2d()
                        B = random_unit_vec_2d()
        
        # 연속 키 입력 처리
        keys = pygame.key.get_pressed()
        if is_3d:
            if keys[pygame.K_LEFT]:
                rot_y -= 2.0 * dt
            if keys[pygame.K_RIGHT]:
                rot_y += 2.0 * dt
            if keys[pygame.K_UP]:
                rot_x -= 2.0 * dt
            if keys[pygame.K_DOWN]:
                rot_x += 2.0 * dt
        else:
            if keys[pygame.K_LEFT]:
                speed = max(0.1, speed - 0.5 * dt)
            if keys[pygame.K_RIGHT]:
                speed = min(3.0, speed + 0.5 * dt)

        # t 왕복(0↔1)
        t += dir_sign * speed * dt
        if t >= 1.0:
            t = 1.0; dir_sign = -1.0
        elif t <= 0.0:
            t = 0.0; dir_sign = +1.0

        # 현재 보간
        v_slerp = slerp(A, B, t)
        v_lerp_norm = normalize(lerp(A, B, t))  # 비교 공정성 위해 원 위로 투영

        # 그리기
        screen.fill(BG)

        # 원(단위원/구), 축
        pygame.draw.circle(screen, (200,200,200), (cx,cy), radius, 1)
        
        if is_3d:
            # 3D 축 그리기 (크기 증가)
            axis_len = radius * 1.2
            origin = (cx, cy)
            
            # X, Y, Z 축
            x_axis = world_to_screen_3d((1, 0, 0), cx, cy, axis_len, rot_x, rot_y)
            y_axis = world_to_screen_3d((0, 1, 0), cx, cy, axis_len, rot_x, rot_y)
            z_axis = world_to_screen_3d((0, 0, 1), cx, cy, axis_len, rot_x, rot_y)
            
            pygame.draw.line(screen, (255, 150, 150), origin, x_axis, 2)  # X축 - 빨강 (굵게)
            pygame.draw.line(screen, (150, 255, 150), origin, y_axis, 2)  # Y축 - 초록 (굵게)
            pygame.draw.line(screen, (150, 150, 255), origin, z_axis, 2)  # Z축 - 파랑 (굵게)
            
            # 축 레이블
            font_axis = pygame.font.SysFont("consolas,courier,arial,monospace", 16, bold=True)
            lbl_x = font_axis.render("X", True, (200, 0, 0))
            lbl_y = font_axis.render("Y", True, (0, 180, 0))
            lbl_z = font_axis.render("Z", True, (0, 0, 200))
            screen.blit(lbl_x, (x_axis[0] + 5, x_axis[1] - 10))
            screen.blit(lbl_y, (y_axis[0] + 5, y_axis[1] - 10))
            screen.blit(lbl_z, (z_axis[0] + 5, z_axis[1] - 10))
        else:
            # 2D 축
            pygame.draw.line(screen, COL_AXIS, (cx-radius, cy), (cx+radius, cy), 1)
            pygame.draw.line(screen, COL_AXIS, (cx, cy-radius), (cx, cy+radius), 1)

        # 중심
        center = (cx, cy)

        # 벡터 표시
        if is_3d:
            end_A = world_to_screen_3d(A, cx, cy, radius, rot_x, rot_y)
            end_B = world_to_screen_3d(B, cx, cy, radius, rot_x, rot_y)
            end_S = world_to_screen_3d(v_slerp, cx, cy, radius, rot_x, rot_y)
            end_L = world_to_screen_3d(v_lerp_norm, cx, cy, radius, rot_x, rot_y)
        else:
            end_A = world_to_screen_2d(A, cx, cy, radius)
            end_B = world_to_screen_2d(B, cx, cy, radius)
            end_S = world_to_screen_2d(v_slerp, cx, cy, radius)
            end_L = world_to_screen_2d(v_lerp_norm, cx, cy, radius)

        draw_arrow(screen, center, end_A, COL_A, 2)
        draw_arrow(screen, center, end_B, COL_B, 2)
        if show_lerp:
            draw_arrow(screen, center, end_L, COL_LERP, 3)
        draw_arrow(screen, center, end_S, COL_SLERP, 4)

        # 포인트 점
        pygame.draw.circle(screen, COL_A, end_A, 4)
        pygame.draw.circle(screen, COL_B, end_B, 4)
        if show_lerp:
            pygame.draw.circle(screen, COL_LERP, end_L, 4)
        pygame.draw.circle(screen, COL_SLERP, end_S, 4)

        # 텍스트
        legend = f"Mode: {mode}   [Space] LERP {'ON' if show_lerp else 'OFF'}   t={t:0.3f}"
        if is_3d:
            help1 = "R: randomize A/B   Arrow Keys: rotate view"
        else:
            help1 = f"R: randomize A/B   LEFT/RIGHT: speed +/-   speed={speed:0.2f}"
        info = "Red=A  Blue=B  Green=SLERP(arc)  Yellow=LERP(normalized)"
        
        txt1 = font.render(legend, True, COL_TEXT); screen.blit(txt1, (10, 10))
        txt2 = font.render(help1, True, COL_TEXT);  screen.blit(txt2, (10, 32))
        txt3 = font.render(info, True, COL_TEXT);   screen.blit(txt3, (10, 54))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
