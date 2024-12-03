from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789


def display_image(disp, image_path):
     
    image = Image.open(image_path)  # 이미지 열기
    image = image.resize((disp.width, disp.height))  # 디스플레이 크기에 맞게 조정
    disp.image(image)  # 이미지 출력


def display_title_screen(disp, title_image_path, coin_image_path, key_image_path, show_items=False, coin=0, key_purchased=False):
    
    # 배경 이미지 로드 및 리사이즈
    title_image = Image.open(title_image_path).resize((disp.width, disp.height))
    screen = title_image.copy()  # 타이틀 이미지를 복사하여 화면 생성

    if show_items:
        # 코인 이미지와 값 표시
        coin_image = Image.open(coin_image_path).resize((20, 20))  # 코인 이미지 크기 조정
        screen.paste(coin_image, (10, 10), coin_image)  # 화면에 코인 이미지 붙이기
        
        draw = ImageDraw.Draw(screen)  # 화면에 텍스트 그리기 설정
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # 폰트 경로
        coin_font = ImageFont.truetype(font_path, 18)  # 폰트 크기 설정
        draw.text((40, 8), f"{coin}", font=coin_font, fill="black")  # 코인 값 텍스트 출력

        # 열쇠 이미지와 상태 표시
        key_image = Image.open(key_image_path).resize((20, 20))  # 열쇠 이미지 크기 조정
        key_x, key_y = disp.width - 100, 10  # 열쇠 이미지 위치
        screen.paste(key_image, (key_x, key_y), key_image)  # 화면에 열쇠 이미지 붙이기

        # 열쇠 구매 상태 텍스트
        key_font_size = 25 if key_purchased else 14  # 구매 상태에 따라 폰트 크기 설정
        key_font = ImageFont.truetype(font_path, key_font_size)
        key_text = "✔" if key_purchased else "#5 buy"  # 구매 상태 텍스트
        key_color = "green" if key_purchased else "black"  # 텍스트 색상 설정
        key_text_y = key_y - 2 if key_purchased else key_y + 2  # 텍스트 위치
        draw.text((key_x + 25, key_text_y), key_text, font=key_font, fill=key_color)  # 텍스트 출력

    # 최종 화면 출력
    disp.image(screen)


def display_title_with_button(disp, title_image_path, start_button_path):
   
    # 배경 이미지 로드 및 리사이즈
    title_image = Image.open(title_image_path).resize((disp.width, disp.height))

    # 버튼 이미지 로드 및 크기 조정
    start_button = Image.open(start_button_path)
    new_size = (start_button.width // 3, start_button.height // 3)  # 버튼 이미지를 1/3 크기로 조정
    start_button = start_button.resize(new_size)

    # 버튼 이미지 위치 계산 (중앙에 배치)
    button_x = (title_image.width - start_button.width) // 2
    button_y = (title_image.height - start_button.height) // 2 + 10  # 약간 아래로 이동
    title_image.paste(start_button, (button_x, button_y), start_button)  # 버튼 붙이기

    # 디스플레이에 최종 이미지 출력
    disp.image(title_image)
