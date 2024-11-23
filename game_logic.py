from PIL import Image, ImageDraw, ImageFont
import random
import time
from spear import Spear

class Game:
    def __init__(self, disp, cat_image_path, background_path, fish_image_path, oxygen_tank_path, life_image_path, treasure_chest_image_path, game_over_image_path, rope_image_path=None, num_fish=6):
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
        self.reset_fish_positions()

        # 보물 상자 및 기타 아이템 설정
        self.treasure_chest_image = Image.open(treasure_chest_image_path).resize(fish_size)
        self.treasure_chest_x = (self.disp.width - self.treasure_chest_image.width) // 2
        self.treasure_chest_y = self.disp.height - self.treasure_chest_image.height
        self.oxygen_tank = Image.open(oxygen_tank_path).resize((20, 20))
        self.life_image = Image.open(life_image_path).resize((20, 20))
        self.game_over_image = Image.open(game_over_image_path).resize((self.disp.width, self.disp.height))
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

        # 잡은 물고기 수 초기화
        self.caught_fish_count = 0  # 여기 추가

        # 작살 객체 생성
        self.spear = Spear(disp, self.cat_image.width, rope_image_path)

        # 작살 상태 플래그
        self.is_spear_active = False


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

    def reset_cat_position(self, offset=20):
        """고양이를 화면 상단에서 약간 떨어진 위치로 초기화하고 Day를 증가시킵니다."""
        self.cat_x = (self.disp.width - self.cat_image.width) // 2
        self.cat_y = offset
        self.needs_update = True
        if self.day < self.max_day:
            self.day += 1
        self.oxygen_time = 20
        self.last_update_time = time.time()
        self.reset_fish_positions()

    def move_cat(self, dx, dy):
        """고양이의 위치를 업데이트합니다."""
        if self.is_spear_active:  # 작살이 발사 중이면 이동 금지
            print("Cannot move while spear is active!")  # 디버깅용 메시지
            return

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


    def update_spear(self):
        if self.spear.spear_active:
            self.spear.update()

            # 작살이 완료되면 활성화 상태를 해제
            if not self.spear.spear_active:  # 작살 동작이 완료되었는지 확인
                self.is_spear_active = False

            # 작살 진행 중일 때 충돌 확인
            if self.spear.spear_active and self.spear.spear_progress < 1:
                hit_fish_index = self.check_spear_collision()
                if hit_fish_index is not None:  # 물고기와 충돌했을 때
                    self.spear.spear_active = False  # 작살 멈춤
                    self.fish_positions.pop(hit_fish_index)  # 물고기 삭제
                    self.caught_fish_count += 1  # 잡은 물고기 수 증가


    def check_spear_collision(self):
        """작살과 물고기의 충돌 여부를 확인"""
        spear_x, spear_y = self.spear.get_tip_position(self.cat_x, self.cat_y)
        for i, (fish_x, fish_y) in enumerate(self.fish_positions):
            fish_width = self.fish_images[0].width
            fish_height = self.fish_images[0].height

            # 충돌 여부 확인 (작살의 끝부분과 물고기의 사각형 영역)
            if (fish_x <= spear_x <= fish_x + fish_width and
                fish_y <= spear_y <= fish_y + fish_height):
                print(f"Collision detected with fish at index {i}")  # 디버깅용 메시지
                return i  # 충돌한 물고기의 인덱스 반환
        return None


    def fire_spear(self):
        """작살 발사"""
        if not self.is_spear_active:  # 작살이 발사 중이 아닐 때만 발사 가능
            self.is_spear_active = True
            self.spear.fire(self.cat_flipped)
            print("Spear fired!")  # 디버깅용 메시지


    def update_spear(self):
        """작살 상태 업데이트 및 물고기와의 충돌 처리"""
        if self.spear.spear_active:
            self.spear.update()

            # 작살이 완료되면 활성화 상태를 해제
            if not self.spear.spear_active:  # 작살 동작이 완료되었는지 확인
                self.is_spear_active = False
                print("Spear deactivated.")  # 디버깅용 메시지

            # 작살 진행 중일 때 충돌 확인
            if self.spear.spear_active and self.spear.spear_progress < 1:
                hit_fish_index = self.check_spear_collision()
                if hit_fish_index is not None:  # 물고기와 충돌했을 때
                    self.spear.spear_active = False  # 작살 멈춤
                    self.is_spear_active = False  # 게임 작살 상태도 초기화
                    print(f"Fish caught at index {hit_fish_index}")  # 디버깅용 메시지

                    # 물고기 제거 및 잡은 물고기 수 증가
                    self.fish_positions.pop(hit_fish_index)  # 물고기 삭제
                    self.caught_fish_count += 1  # 잡은 물고기 수 증가
                    print(f"Fish caught! Total: {self.caught_fish_count}")  # 디버깅용 메시지



    def display_spear(self, screen):
        """작살 그리기"""
        self.spear.draw(screen, self.cat_x, self.cat_y, self.cat_flipped)

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
                self.lives -= 1
                self.oxygen_time = 20
                if self.lives <= 0:
                    self.game_over()
                else:
                    return "title"

    def display_day_and_oxygen(self, screen):
        """왼쪽 상단에 'Day - 숫자'와 산소 카운트 표시"""
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
        """게임 화면 업데이트"""
        screen = self.background.copy()

        for i, (x, y) in enumerate(self.fish_positions):
            if self.fish_directions[i] == "left":
                screen.paste(self.fish_flipped_images[i], (x, y), self.fish_flipped_images[i])
            else:
                screen.paste(self.fish_images[i], (x, y), self.fish_images[i])

        screen.paste(self.treasure_chest_image, (self.treasure_chest_x, self.treasure_chest_y), self.treasure_chest_image)
        screen.paste(self.cat_image, (self.cat_x, self.cat_y), self.cat_image)
        self.display_day_and_oxygen(screen)
        self.display_lives(screen)
        self.display_spear(screen)  # Spear 그리기
        screen = screen.resize((self.disp.width, self.disp.height))
        screen = screen.convert("RGB")
        self.disp.image(screen)

    def update_fish_positions(self):
        """물고기 위치를 업데이트합니다."""
        for i in range(len(self.fish_positions)):
            x, y = self.fish_positions[i]
            direction = self.fish_directions[i]
            speed = self.fish_speeds[i]

            if direction == "left":
                x -= speed
                if x <= 0:
                    x = 0
                    self.fish_directions[i] = "right"
            else:
                x += speed
                if x >= self.disp.width - self.fish_images[i].width:
                    x = self.disp.width - self.fish_images[i].width
                    self.fish_directions[i] = "left"

            self.fish_positions[i] = (x, y)

    def game_over(self):
        """게임 오버 시 game_over.png를 화면에 표시하고 종료"""
        self.disp.image(self.game_over_image)
        while True:
            time.sleep(0.1)
