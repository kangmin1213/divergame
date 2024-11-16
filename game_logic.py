from PIL import Image, ImageDraw, ImageFont
import random
import time

class Game:
    def __init__(self, disp, cat_image_path, background_path, fish_image_path, oxygen_tank_path, life_image_path, treasure_chest_image_path, game_over_image_path, num_fish=6):
        self.disp = disp
        self.cat_image_original = Image.open(cat_image_path).resize((50, 50))
        self.cat_image_flipped = self.cat_image_original.transpose(Image.FLIP_LEFT_RIGHT)
        self.cat_image = self.cat_image_original
        self.background = Image.open(background_path).resize((disp.width, disp.height))

        # 물고기 이미지 및 이동 설정
        fish_size = (self.cat_image.width // 2, self.cat_image.height // 2)
        fish_image = Image.open(fish_image_path).resize(fish_size)
        self.fish_images = [fish_image] * num_fish
        self.fish_flipped_images = [fish_image.transpose(Image.FLIP_LEFT_RIGHT) for fish_image in self.fish_images]
        self.num_fish = num_fish
        self.reset_fish_positions()  # 물고기 위치 초기화

        # 보물 상자 및 기타 아이템 설정
        self.treasure_chest_image = Image.open(treasure_chest_image_path).resize(fish_size)
        self.treasure_chest_x = (self.disp.width - self.treasure_chest_image.width) // 2
        self.treasure_chest_y = self.disp.height - self.treasure_chest_image.height
        self.oxygen_tank = Image.open(oxygen_tank_path).resize((20, 20))
        self.life_image = Image.open(life_image_path).resize((20, 20))
        self.game_over_image = Image.open(game_over_image_path).resize((self.disp.width, self.disp.height))  # 추가: 게임 오버 이미지
        self.lives = 2  # 초기 생명 설정

        # 고양이 및 산소 시간 초기화
        self.cat_x = (disp.width - self.cat_image.width) // 2
        self.cat_y = (disp.height - self.cat_image.height) // 2
        self.cat_flipped = False
        self.needs_update = True
        self.day = 0
        self.max_day = 7
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        self.small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
        self.oxygen_time = 20
        self.last_update_time = time.time()

    def reset_fish_positions(self):
        """물고기 위치와 이동 방향을 초기화합니다."""
        self.fish_positions = self.generate_fish_positions(self.num_fish)
        self.fish_directions = [random.choice(["left", "right"]) for _ in range(self.num_fish)]
        self.fish_speeds = [random.randint(1, 3) for _ in range(self.num_fish)]

    def generate_fish_positions(self, num_fish, margin=30):
        """초기 물고기 위치 생성"""
        positions = []
        cell_width = (self.disp.width - 2 * margin) // 2
        cell_height = (self.disp.height - 2 * margin) // 3

        for i in range(3):
            for j in range(2):
                if len(positions) < num_fish:
                    x_min = margin + j * cell_width
                    x_max = x_min + cell_width - self.fish_images[0].width
                    y_min = margin + i * cell_height
                    y_max = y_min + cell_height - self.fish_images[0].height

                    x = random.randint(x_min, x_max)
                    y = random.randint(y_min, y_max)
                    positions.append((x, y))
        
        return positions

    def update_fish_positions(self):
        """물고기 위치를 업데이트하여 좌우로 이동하고, 화면 밖으로 나가면 방향을 전환합니다."""
        for i in range(len(self.fish_positions)):
            x, y = self.fish_positions[i]
            direction = self.fish_directions[i]
            speed = self.fish_speeds[i]

            # 방향에 따라 이동하고 위치 업데이트
            if direction == "left":
                x -= speed
                if x <= 0:  # 왼쪽 벽에 닿으면 방향 전환
                    x = 0
                    self.fish_directions[i] = "right"
            else:
                x += speed
                if x >= self.disp.width - self.fish_images[i].width:  # 오른쪽 벽에 닿으면 방향 전환
                    x = self.disp.width - self.fish_images[i].width
                    self.fish_directions[i] = "left"

            # 업데이트된 위치 저장
            self.fish_positions[i] = (x, y)

    def display_day_and_oxygen(self, screen):
        """왼쪽 상단에 'Day - 숫자'와 산소통 아이콘 및 카운트다운 표시"""
        draw = ImageDraw.Draw(screen)
        day_text = f"Day - {self.day}"
        oxygen_text = f"{self.oxygen_time}s"
        draw.text((10, 5), day_text, font=self.font, fill="black")
        screen.paste(self.oxygen_tank, (10, 30), self.oxygen_tank)
        draw.text((35, 32), oxygen_text, font=self.small_font, fill="red")

    def display_lives(self, screen):
        """오른쪽 상단에 남은 life 이미지를 표시"""
        life_x = self.disp.width - 40
        life_y = 10
        for i in range(self.lives):
            screen.paste(self.life_image, (life_x - i * 25, life_y), self.life_image)

    def display_game_screen(self):
        """게임 화면을 업데이트하여 물고기 위치와 움직임을 반영"""
        screen = self.background.copy()
        
        # 물고기 위치 업데이트 및 반전 표시
        for i, (x, y) in enumerate(self.fish_positions):
            if self.fish_directions[i] == "left":
                screen.paste(self.fish_flipped_images[i], (x, y), self.fish_flipped_images[i])
            else:
                screen.paste(self.fish_images[i], (x, y), self.fish_images[i])

        # 보물 상자 및 고양이 표시
        screen.paste(self.treasure_chest_image, (self.treasure_chest_x, self.treasure_chest_y), self.treasure_chest_image)
        screen.paste(self.cat_image, (self.cat_x, self.cat_y), self.cat_image)
        self.display_day_and_oxygen(screen)
        self.display_lives(screen)
        self.disp.image(screen)

    def update_cat_position(self):
        """고양이 위치와 물고기 위치 업데이트 후 화면 새로고침"""
        self.update_fish_positions()  # 물고기 위치 업데이트
        self.display_game_screen()    # 화면 업데이트

    def move_cat(self, dx, dy):
        new_x = max(0, min(self.disp.width - self.cat_image.width, self.cat_x + dx))
        new_y = max(0, min(self.disp.height - self.cat_image.height, self.cat_y + dy))

        if new_x != self.cat_x or new_y != self.cat_y:
            self.cat_x, self.cat_y = new_x, new_y
            self.needs_update = True

        if dx > 0 and not self.cat_flipped:
            self.cat_image = self.cat_image_flipped
            self.cat_flipped = True
            self.needs_update = True
        elif dx < 0 and self.cat_flipped:
            self.cat_image = self.cat_image_original
            self.cat_flipped = False
            self.needs_update = True

        self.update_cat_position()

    def reset_cat_position(self, offset=20):
        """고양이를 화면 상단에서 약간 떨어진 위치로 초기화하고 Day를 증가시킵니다."""
        self.cat_x = (self.disp.width - self.cat_image.width) // 2
        self.cat_y = offset
        self.needs_update = True
        if self.day < self.max_day:
            self.day += 1
        self.oxygen_time = 20
        self.last_update_time = time.time()
        self.reset_fish_positions()  # 물고기 위치와 방향을 초기화

    def cat_reached_top(self):
        """고양이가 화면의 최상단에 닿았는지 확인합니다."""
        return self.cat_y <= 0

    def update_oxygen_time(self):
        """산소 시간을 카운트 다운하고, 0이 되면 생명 감소 처리 후 타이틀 화면으로 전환"""
        current_time = time.time()
        if current_time - self.last_update_time >= 1:
            self.oxygen_time -= 1
            self.last_update_time = current_time
            self.needs_update = True

            if self.oxygen_time <= 0:
                self.lives -= 1  # 생명 감소
                self.oxygen_time = 20  # 산소 시간 초기화
                if self.lives <= 0:
                    self.game_over()
                else:
                    return "title"  # 생명 감소 후 타이틀 화면으로 돌아가도록 신호

    def game_over(self):
        """게임 오버 시 game_over.png를 화면에 표시하고 종료"""
        self.disp.image(self.game_over_image)

        # 게임 종료 상태를 유지하기 위한 무한 루프
        while True:
            time.sleep(0.1)
