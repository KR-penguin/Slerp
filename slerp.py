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

# --------- 수학 유틸 ----------
def dot(a, b): return a[0]*b[0] + a[1]*b[1]
def length(v): return math.hypot(v[0], v[1])
def normalize(v):
    l = length(v)
    if l < 1e-12: return (1.0, 0.0)
    return (v[0]/l, v[1]/l)
def add(a,b): return (a[0]+b[0], a[1]+b[1])
def mul(v, s): return (v[0]*s, v[1]*s)
def lerp(a, b, t): return add(mul(a, 1.0 - t), mul(b, t))

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

# --------- 화면 유틸 ----------
def world_to_screen(v, cx, cy, radius):
    # 수학: +y 위 / 화면: +y 아래 → y축 반전
    x = cx + v[0]*radius
    y = cy - v[1]*radius
    return (int(round(x)), int(round(y)))

def draw_arrow(surf, center, end_pt, color, width=3):
    pygame.draw.line(surf, color, center, end_pt, width)
    # 간단한 화살촉
    dx = end_pt[0]-center[0]
    dy = end_pt[1]-center[1]
    ang = math.atan2(dy, dx)
    L = 12
    a1 = (end_pt[0] - L*math.cos(ang - math.pi/8),
          end_pt[1] - L*math.sin(ang - math.pi/8))
    a2 = (end_pt[0] - L*math.cos(ang + math.pi/8),
          end_pt[1] - L*math.sin(ang + math.pi/8))
    pygame.draw.line(surf, color, end_pt, a1, width)
    pygame.draw.line(surf, color, end_pt, a2, width)

def random_unit_vec():
    ang = random.random()*2*math.pi
    return (math.cos(ang), math.sin(ang))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SLERP vs LERP (Space: toggle LERP, R: random A/B, ←/→: speed)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    cx, cy = WIDTH//2, HEIGHT//2
    radius = min(WIDTH, HEIGHT)//2 - 40

    # 초기 두 방향
    A = (1.0, 0.0)
    B = (0.0, 1.0)

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
                    A = random_unit_vec()
                    B = random_unit_vec()
                elif e.key == pygame.K_LEFT:
                    speed = max(0.1, speed - 0.15)
                elif e.key == pygame.K_RIGHT:
                    speed = min(3.0, speed + 0.15)

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

        # 원(단위원), 축
        pygame.draw.circle(screen, (200,200,200), (cx,cy), radius, 1)
        pygame.draw.line(screen, COL_AXIS, (cx-radius, cy), (cx+radius, cy), 1)
        pygame.draw.line(screen, COL_AXIS, (cx, cy-radius), (cx, cy+radius), 1)

        # 중심
        center = (cx, cy)

        # 벡터 표시
        end_A = world_to_screen(A, cx, cy, radius)
        end_B = world_to_screen(B, cx, cy, radius)
        end_S = world_to_screen(v_slerp, cx, cy, radius)
        end_L = world_to_screen(v_lerp_norm, cx, cy, radius)

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
        legend = f"[Space] LERP {'ON' if show_lerp else 'OFF'}   t={t:0.3f}   speed={speed:0.2f}"
        help1 = "R: randomize A/B   LEFT/RIGHT: speed +/-"
        info = "Red=A  Blue=B  Green=SLERP(arc)  Yellow=LERP(normalized)"
        txt1 = font.render(legend, True, COL_TEXT); screen.blit(txt1, (10, 10))
        txt2 = font.render(help1, True, COL_TEXT);  screen.blit(txt2, (10, 32))
        txt3 = font.render(info, True, COL_TEXT);   screen.blit(txt3, (10, 54))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
