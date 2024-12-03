import time
from digitalio import DigitalInOut, Direction, Pull
import board
from adafruit_rgb_display import st7789
from display_utils import display_title_with_button, display_title_screen
from game_logic import Game

# 디스플레이 초기화 설정
cs_pin = DigitalInOut(board.CE0)  
dc_pin = DigitalInOut(board.D25)  
reset_pin = DigitalInOut(board.D24)  
BAUDRATE = 24000000 

# SPI 디스플레이 초기화
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

# 디스플레이 백라이트 설정
backlight = DigitalInOut(board.D26)
backlight.switch_to_output()
backlight.value = True  # 백라이트 활성화

# 버튼 설정
# 버튼은 Pull-UP 설정 
button_A = DigitalInOut(board.D5)       #5
button_A.direction = Direction.INPUT
button_A.pull = Pull.UP

button_B = DigitalInOut(board.D6)       #6
button_B.direction = Direction.INPUT
button_B.pull = Pull.UP

button_L = DigitalInOut(board.D27)      #조이스틱 왼쪽
button_L.direction = Direction.INPUT
button_L.pull = Pull.UP

button_R = DigitalInOut(board.D23)      #조이스틱 오른쪽
button_R.direction = Direction.INPUT
button_R.pull = Pull.UP

button_U = DigitalInOut(board.D17)      #조이스틱 위
button_U.direction = Direction.INPUT
button_U.pull = Pull.UP

button_D = DigitalInOut(board.D22)      #조이스틱 아래
button_D.direction = Direction.INPUT
button_D.pull = Pull.UP

# 상태 변수 초기화
game_mode = False           # 게임 중인지 여부
in_title_screen = True      # 현재 타이틀 화면 여부
show_items = False          # 아이템 표시 여부
is_first_run = True         # 프로그램 첫 실행 여부
coin = 0                    # 플레이어의 코인 수 초기화
key_purchased = False       # 열쇠 구매 여부
treasure_opening = False    # 보물상자 여는 중 여부
treasure_open_start_time = None  # 보물상자 여는 시작 시간

# 이미지 경로 설정
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
game_clear_image_path = "game_clear.png"  
rope_image_path = "rope.png"

# Game 객체 생성
# 게임 로직과 화면 관리 역할
game = Game(
    disp,
    cat_image_path,
    game_image_path,
    fish_image_path,
    oxygen_tank_path,
    life_image_path,
    treasure_chest_image_path,
    game_over_image_path,
    game_clear_image_path,  
    num_fish=6,  # 게임 내 물고기 수
    rope_image_path=rope_image_path,
)

# 초기 화면 표시
if is_first_run:
    display_title_with_button(disp, title_image_path, start_button_path)
else:
    display_title_screen(disp, title_image_path, coin_image_path, key_image_path, show_items, coin, key_purchased)

# 메인 루프
last_fish_update = time.time()  # 물고기 업데이트 시간 기록
last_screen_update = time.time()  # 화면 업데이트 시간 기록

while True:
    current_time = time.time()  # 현재 시간 갱신

    # 타이틀 화면 처리
    if in_title_screen:
        # A 버튼으로 열쇠 구매
        if not button_A.value and not key_purchased and coin >= 1000:
            coin -= 1000  # 코인 차감
            key_purchased = True  # 열쇠 구매 상태 설정
            print("열쇠 구매")  # 디버깅 메시지

            # 타이틀 화면 업데이트
            display_title_screen(disp, title_image_path, coin_image_path, key_image_path, show_items, coin, key_purchased)
            time.sleep(0.5)  # 중복 입력 방지

        # B 버튼으로 게임 시작
        if not button_B.value:
            game_mode = True
            in_title_screen = False
            show_items = False
            is_first_run = False
            game.reset_cat_position()  # 고양이 위치 초기화
            game.display_game_screen()  # 게임 화면 표시
            time.sleep(0.5)  # 중복 입력 방지
        continue

    # 게임 모드 처리
    if game_mode:
        # DAY-5 종료 시 즉시 게임오버 조건 확인
        if game.day > 5 and not game.treasure_opened:
            print("Game Over") 
            game.display_game_over_screen()  # 게임 오버 화면 표시
            break  # 게임 루프 종료

        # 고양이 이동 처리
        if not treasure_opening:
            if not button_L.value:
                game.move_cat(-10, 0)
            elif not button_R.value:
                game.move_cat(10, 0)
            elif not button_U.value:
                game.move_cat(0, -10)
            elif not button_D.value:
                game.move_cat(0, 10)

        # 작살 발사
        if not button_A.value:
            game.fire_spear()

        # 물고기 및 작살 업데이트
        if current_time - last_fish_update >= 0.1:  # 0.1초마다 업데이트
            game.update_fish_positions()
            game.update_spear()
            last_fish_update = current_time

        # 코인 업데이트
        coin = game.caught_fish_count * 100

        # 보물상자 열기 트리거
        if not button_B.value and game.is_near_treasure() and key_purchased and not treasure_opening:
            treasure_opening = True
            treasure_open_start_time = current_time

        # 보물상자 열기 처리
        if treasure_opening:
            elapsed_time = current_time - treasure_open_start_time
            if elapsed_time >= 1:
                print(" Game clear")
                game.treasure_opened = True  # 보물상자가 열렸음을 기록
                game.display_game_clear_screen()  # 게임 클리어 화면 표시
                break  # 게임 클리어 후 종료

        # 산소 부족 시 상태 처리
        result = game.update_oxygen_time()
        if result == "title":  # 산소 부족으로 하트를 잃었을 때
            game.reset_cat_position()  # 고양이 위치 초기화
            game_mode = False
            in_title_screen = True
            show_items = True
            display_title_screen(disp, title_image_path, coin_image_path, key_image_path, show_items, coin, key_purchased)
            time.sleep(0.5)
            continue

        # 고양이가 최상단에 도달한 경우
        if game.cat_reached_top():
            game.update_day()  # 날짜 증가
            game.reset_cat_position()
            game_mode = False
            in_title_screen = True
            show_items = True
            display_title_screen(disp, title_image_path, coin_image_path, key_image_path, show_items, coin, key_purchased)
            time.sleep(0.5)
            continue

        # 게임 화면 업데이트
        if current_time - last_screen_update >= 0.05:  # 0.05초마다 화면 갱신
            game.display_game_screen()
            last_screen_update = current_time

    time.sleep(0.01)  # 메인 루프 주기 조정
