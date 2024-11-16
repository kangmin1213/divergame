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
game_over_image_path = "game_over.png"  # 추가: 게임 오버 이미지 경로

# 화면 전환 상태 변수
game_mode = False  # False: 타이틀 화면, True: 게임 화면
show_items = False  # 타이틀 화면에서 아이템을 표시할지 여부

# Game 객체 생성 (물고기 6마리 설정)
game = Game(
    disp,
    cat_image_path,
    game_image_path,
    fish_image_path,
    oxygen_tank_path,
    life_image_path,
    treasure_chest_image_path,
    game_over_image_path,  # 추가: 게임 오버 이미지 경로 전달
    num_fish=6
)

# 초기 화면 (타이틀 화면) 표시
display_title_with_button(disp, title_image_path, start_button_path)

# 메인 루프
while True:
    # 타이틀 화면에서 B 버튼이 눌리면 게임 모드로 전환
    if not game_mode and not button_B.value:
        game_mode = True
        show_items = False  # 초기화면에서 아이템이 보이지 않음
        game.reset_cat_position()  # 고양이 위치 초기화
        game.display_game_screen()  # 게임 화면 표시
        time.sleep(0.5)  # 중복 반응 방지

    # 게임 모드일 때 고양이 이동 처리
    if game_mode:
        if not button_L.value:
            game.move_cat(-10, 0)  # 왼쪽으로 이동
        elif not button_R.value:
            game.move_cat(10, 0)   # 오른쪽으로 이동
        elif not button_U.value:
            game.move_cat(0, -10)  # 위로 이동
        elif not button_D.value:
            game.move_cat(0, 10)   # 아래로 이동

        # 산소 카운트다운 업데이트 및 화면 전환
        result = game.update_oxygen_time()
        if result == "title":  # 산소가 모두 소진되어 타이틀 화면으로 전환
            game_mode = False
            show_items = True  # 물 위로 올라온 후의 타이틀 화면에서 아이템 표시
            display_title_screen(disp, title_image_path, coin_image_path, key_image_path, show_items)
            time.sleep(0.5)

        # 고양이가 최상단에 닿았을 때 타이틀 화면으로 전환
        if game.cat_reached_top():
            game_mode = False
            show_items = True  # 물 위로 올라온 후의 타이틀 화면에서 아이템 표시
            display_title_screen(disp, title_image_path, coin_image_path, key_image_path, show_items)
            time.sleep(0.5)

    # 짧은 딜레이로 반복
    time.sleep(0.1)
