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

# 화면 전환 상태 변수 초기화
game_mode = False
in_title_screen = True
show_items = False
is_first_run = True  # 프로그램이 처음 실행되었는지 여부

# 이미지 파일 경로
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
    num_fish=6
)

# 초기 타이틀 화면 표시 (첫 실행에서는 게임 시작 버튼 포함)
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
        if not button_B.value:  # B 버튼을 눌렀을 때만 게임 시작
            game_mode = True
            in_title_screen = False
            show_items = False
            is_first_run = False  # 첫 실행 후 플래그를 False로 변경
            game.reset_cat_position()
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

        # 물고기 위치 업데이트
        if current_time - last_fish_update >= 0.1:
            game.update_fish_positions()
            last_fish_update = current_time

        # 산소 시간 업데이트
        result = game.update_oxygen_time()
        if result == "title":  # 산소가 소진되면 타이틀 화면으로 전환
            game_mode = False
            in_title_screen = True
            show_items = True
            display_title_screen(disp, title_image_path, coin_image_path, key_image_path, show_items)
            time.sleep(0.5)
            continue

        # 고양이가 최상단에 도달했을 때 타이틀 화면으로 전환
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
