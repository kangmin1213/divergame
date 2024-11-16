from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789

def display_image(disp, image_path):
    """이미지를 화면에 맞게 리사이즈하여 표시합니다."""
    image = Image.open(image_path)
    image = image.resize((disp.width, disp.height))
    disp.image(image)

def display_title_screen(disp, title_image_path, coin_image_path, key_image_path, show_items=False):
    """타이틀 화면을 표시하고, show_items가 True일 때만 코인 및 키 이미지를 상단에 표시합니다."""
    title_image = Image.open(title_image_path)
    title_image = title_image.resize((disp.width, disp.height))
    
    screen = title_image.copy()
    
    # show_items가 True일 때만 추가 이미지와 텍스트 표시
    if show_items:
        # Coin 이미지 좌측 상단에 배치
        coin_image = Image.open(coin_image_path).resize((20, 20))
        screen.paste(coin_image, (10, 10), coin_image)

        # Key 이미지와 "구매" 텍스트 우측 상단에 배치
        key_image = Image.open(key_image_path).resize((20, 20))
        screen.paste(key_image, (disp.width - 60, 10), key_image)

        # "구매" 텍스트 표시
        draw = ImageDraw.Draw(screen)
        font = ImageFont.load_default()
        draw.text((disp.width - 35, 12), "#5 buy", font=font, fill="black")

    # 최종 화면 출력
    disp.image(screen)

def display_title_with_button(disp, title_image_path, start_button_path):
    """타이틀 화면 중앙에 1/3 크기의 'Start Game' 버튼을 추가하여 표시합니다."""
    title_image = Image.open(title_image_path)
    title_image = title_image.resize((disp.width, disp.height))
    
    # "Start Game" 버튼 이미지 열기 및 크기 조정
    start_button = Image.open(start_button_path)
    new_size = (start_button.width // 3, start_button.height // 3)  # 1/3 크기로 줄이기
    start_button = start_button.resize(new_size)
    
    # 타이틀 이미지 중앙에 버튼 이미지 배치 (아래로 10 픽셀 이동)
    button_x = (title_image.width - start_button.width) // 2
    button_y = (title_image.height - start_button.height) // 2 + 10
    title_image.paste(start_button, (button_x, button_y), start_button)
    
    # 디스플레이에 타이틀 이미지 출력
    disp.image(title_image)
