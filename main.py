import time
from digitalio import DigitalInOut, Direction, Pull
import board
from adafruit_rgb_display import st7789
from display_utils import display_title_with_button, display_image, display_title_screen
from game_logic import Game

# 디스플레이 초기화 설정
cs_pin = DigitalInOut(board.CE0)
dc_pin = DigitalInOut(board.D25)
reset_pin = DigitalInOut(board.D24)
BAUDRATE = 24000000

spi = board.SPI()
disp = st7789.ST7789(
    spi,
    height=240,
    y_offset=80,
    rotation=180,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

# 백라이트 켜기
backlight = DigitalInOut(board.D26)
backlight.switch_to_output()
backlight.value = True

# 버튼 설정
button_A = DigitalInOut(board.D5); button_A.direction = Direction.INPUT; button_A.pull = Pull.UP
button_B = DigitalInOut(board.D6); button_B.direction = Direction.INPUT; button_B.pull = Pull.UP
button_L = DigitalInOut(board.D27); button_L.direction = Direction.INPUT; button_L.pull = Pull.UP
button_R = DigitalInOut(board.D23); button_R.direction = Direction.INPUT; button_R.pull = Pull.UP
button_U = DigitalInOut(board.D17); button_U.direction = Direction.INPUT; button_U.pull = Pull.UP
button_D = DigitalInOut(board.D22); button_D.direction = Direction.INPUT; button_D.pull = Pull.UP
button_C = DigitalInOut(board.D4); button_C.direction = Direction.INPUT; button_C.pull = Pull.UP

# 상태 변수 초기화
game_mode = False
in_title_screen = True
show_items = False
is_first_run = True

# 이미지 경로
title_image_path = "background_title.png"
start_button_path = "start_button.png"
game_image_path = "background_game.png"
cat_image_path = "cat.png"
fish_image_path = "fish.png"
coin_image_path = "coin.png"
key_image_path = "key.png"
oxygen_tank_path = "oxygen_tank.png"
life_image_path = "life.png"
treasure_chest_image_path = "treasure_chest.png"
game_over_image_path = "game_over.png"
rope_image_path = "rope.png"  # 밧줄 이미지 경로 추가

# Game 객체 생성
game = Game(
    disp,
    cat_image_path,
    game_image_path,
    fish_image_path,
    oxygen_tank_path,
    life_image_path,
    treasure_chest_image_path,
    game_over_image_path,
    num_fish=6,
    rope_image_path=rope_image_path  # rope_image_path 전달
)

# 초기 화면 표시
if is_first_run:
    display_title_with_button(disp, title_image_path, start_button_path)
else:
    display_title_screen(disp, title_image_path, coin_image_path, key_image_path, show_items)

# 메인 루프
last_fish_update = time.time()
last_screen_update = time.time()

while True:
    current_time = time.time()

    # 타이틀 화면 처리
    if in_title_screen:
        if not button_B.value:  # B 버튼으로 게임 시작
            game_mode = True
            in_title_screen = False
            show_items = False
            is_first_run = False
            game.reset_cat_position()  # 게임 시작 시 고양이 위치 초기화 (1일 추가는 이곳에서만 발생)
            game.display_game_screen()
            time.sleep(0.5)  # 중복 입력 방지
        continue

    # 게임 모드 처리
    if game_mode:
        # 고양이 이동 처리
        if not button_L.value:
            game.move_cat(-10, 0)
        elif not button_R.value:
            game.move_cat(10, 0)
        elif not button_U.value:
            game.move_cat(0, -10)
        elif not button_D.value:
            game.move_cat(0, 10)

        # 작살 발사
        if not button_A.value:  # A 버튼으로 작살 발사
            game.fire_spear()

        # 물고기 및 작살 업데이트
        if current_time - last_fish_update >= 0.1:
            game.update_fish_positions()
            game.update_spear()
            last_fish_update = current_time

        # 산소 시간 업데이트
        result = game.update_oxygen_time()
        if result == "title":  # 산소가 다 떨어지면 타이틀 화면으로
            game_mode = False
            in_title_screen = True
            show_items = True
            display_title_screen(disp, title_image_path, coin_image_path, key_image_path, show_items)
            time.sleep(0.5)
            continue

        # 고양이가 최상단에 도달하면 타이틀 화면으로
        if game.cat_reached_top():
            game_mode = False
            in_title_screen = True
            show_items = True
            display_title_screen(disp, title_image_path, coin_image_path, key_image_path, show_items)
            time.sleep(0.5)
            continue

        # 게임 화면 업데이트
        if current_time - last_screen_update >= 0.05:
            game.display_game_screen()
            last_screen_update = current_time

    time.sleep(0.01)  # 짧은 딜레이
