from PIL import Image, ImageDraw, ImageFont
import random
import time
from spear import Spear


class Game:
    def __init__(self, disp, cat_image_path, background_path, fish_image_path, oxygen_tank_path, life_image_path, treasure_chest_image_path, game_over_image_path, game_clear_image_path, num_fish=6, rope_image_path=None):
        self.disp = disp
        self.cat_image_original = Image.open(cat_image_path).resize((50, 50))
        self.background = Image.open(background_path).resize((disp.width, disp.height))
        self.game_clear_image_path = game_clear_image_path  # 게임 클리어 이미지 경로 추가
        self.cat_image_flipped = self.cat_image_original.transpose(Image.FLIP_LEFT_RIGHT)
        self.cat_image = self.cat_image_original
        
                # 보물상자 상태 초기화
        self.treasure_opened = False  # 보물상자가 열렸는지 여부

        # 물고기 이미지 및 이동 설정
        fish_size = (self.cat_image.width // 2, self.cat_image.height // 2)  
        fish_image = Image.open(fish_image_path).resize(fish_size)  
        self.fish_images = [fish_image] * num_fish  
        self.fish_flipped_images = [fish_image.transpose(Image.FLIP_LEFT_RIGHT) for fish_image in self.fish_images]  # 좌우 반전 물고기 이미지 
        self.num_fish = num_fish  # 물고기 개수 
        self.reset_fish_positions()  # 물고기 위치 

        # 보물상자 및 기타 아이템 설정
        self.treasure_chest_image = Image.open(treasure_chest_image_path).resize(fish_size)  
        self.treasure_chest_x = (self.disp.width - self.treasure_chest_image.width) // 2  
        self.treasure_chest_y = self.disp.height - self.treasure_chest_image.height  
        self.oxygen_tank = Image.open(oxygen_tank_path).resize((20, 20))  
        self.life_image = Image.open(life_image_path).resize((20, 20))  
        self.game_over_image = Image.open(game_over_image_path).resize((self.disp.width, self.disp.height))  
        self.game_clear_image_path = game_clear_image_path  
        self.lives = 2  

        # 고양이 및 산소 시간 초기화
        self.cat_x = (disp.width - self.cat_image.width) // 2  # 고양이 x 좌표를 화면 중앙에 초기화
        self.cat_y = (disp.height - self.cat_image.height) // 2  # 고양이 y 좌표를 화면 중앙에 초기화
        self.cat_flipped = False  # 고양이 방향 플래그 (False: 왼쪽, True: 오른쪽)
        self.needs_update = True  # 화면 업데이트 필요 여부 
        self.day = 1  # 게임 시작일 
        self.max_day = 6  # 최대 진행 가능 일 수 + 1
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)  # 큰 텍스트용 폰트 설정
        self.small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)  # 작은 텍스트용 폰트 설정
        self.oxygen_time = 20  # 초기 산소 시간 설정
        self.last_update_time = time.time()  # 산소 시간 업데이트 기준 시간

        # 잡은 물고기 수 초기화
        self.caught_fish_count = 0  # 잡은 물고기 

        # 작살 객체 생성
        self.spear = Spear(disp, self.cat_image.width, rope_image_path)  

        # 작살 상태 플래그
        self.is_spear_active = False  # 작살이 발사 중인지 여부


    def reset_fish_positions(self):   # 물고기의 위치와 이동 방향, 속도 설정

        # 물고기 초기 위치 설정
        self.fish_positions = self.generate_fish_positions(self.num_fish)
        # 물고기의 이동 방향을 무작위로 설정 (왼쪽 또는 오른쪽)
        self.fish_directions = [random.choice(["left", "right"]) for _ in range(self.num_fish)]
        # 물고기의 속도를 1~3의 범위에서 무작위로 설정
        self.fish_speeds = [random.randint(1, 3) for _ in range(self.num_fish)]

    def generate_fish_positions(self, num_fish, margin=30):     # 초기 물고기 위치 설정(margin: 화면 가장자리 여백)
   
        positions = []
        # 화면을 2열 x 3행으로 나누어 각 셀에 물고기를 배치
        cell_width = (self.disp.width - 2 * margin) // 2
        cell_height = (self.disp.height - 2 * margin) // 3

        # 각 셀에 물고기 배치
        for i in range(3):  # 3행 반복
            for j in range(2):  # 2열 반복
                if len(positions) < num_fish:  # 물고기 수 만큼 배치
                    # 물고기의 최소/최대 x, y 좌표를 설정
                    x_min = margin + j * cell_width
                    x_max = x_min + cell_width - self.fish_images[0].width
                    y_min = margin + i * cell_height
                    y_max = y_min + cell_height - self.fish_images[0].height

                    # 물고기의 위치를 랜덤하게 선택
                    x = random.randint(x_min, x_max)
                    y = random.randint(y_min, y_max)
                    positions.append((x, y))  
        
        return positions  

    def reset_cat_position(self, offset=None):      # offset: 화면 상단에서의 거리
        
        if offset is None:
            offset = self.disp.height // 5  # 화면 높이의 20% 지점
        # 고양이 위치를 화면 중앙 상단에 배치
        self.cat_x = (self.disp.width - self.cat_image.width) // 2
        self.cat_y = offset
        self.needs_update = True  # 화면 업데이트 
        self.oxygen_time = 20  # 산소통 시간 
        self.last_update_time = time.time()  # 산소 시간 업데이트 
        self.reset_fish_positions()  # 물고기 위치 초기화

    def update_day(self):   # 날짜를 증가시키고 게임 오버 조건 설정
        
        if self.day < self.max_day:  # 최대 날짜에 도달하지 않았으면
            self.day += 1  # 날짜 증가
            self.check_game_over_due_to_day()  # 게임 오버 조건(날짜)


    def move_cat(self, dx, dy):     # 고양이의 위치를 업데이트
        
        # 작살이 발사 중이면 이동 금지
        if self.is_spear_active:
            return

        # 고양이의 움직임 제한
        new_x = max(0, min(self.disp.width - self.cat_image.width, self.cat_x + dx))
        new_y = max(0, min(self.disp.height - self.cat_image.height, self.cat_y + dy))

        # 위치가 변경 업데이트
        if new_x != self.cat_x or new_y != self.cat_y:
            self.cat_x, self.cat_y = new_x, new_y
            self.needs_update = True  

        # 고양이 이미지를 좌우 반전
        if dx > 0 and not self.cat_flipped:  # 오른쪽 이동
            self.cat_image = self.cat_image_flipped
            self.cat_flipped = True
            self.needs_update = True
        elif dx < 0 and self.cat_flipped:  # 왼쪽 이동
            self.cat_image = self.cat_image_original
            self.cat_flipped = False
            self.needs_update = True

    def update_spear(self):     # 작살의 상태 업데이트 및 충돌을 처리

        if self.spear.spear_active:  # 작살이 활성화 상태일 때만 업데이트
            self.spear.update()  # 작살 진행 상태 업데이트

            # 작살 동작이 완료되었는지 확인
            if not self.spear.spear_active:  # 작살 동작이 끝난 경우
                self.is_spear_active = False  # 작살 상태 플래그 해제

            # 충돌 여부
            if self.spear.spear_active:  # 작살이 진행 중일때
                hit_fish_index = self.check_spear_collision()  # 충돌 확인
                if hit_fish_index is not None:  # 충돌했을 경우
                    self.spear.spear_active = False  # 작살 멈춤
                    self.is_spear_active = False  # 작살 상태 초기화

                    # 물고기 제거 및 잡은 물고기 수 증가
                    self.fish_positions.pop(hit_fish_index)  # 충돌한 물고기 삭제
                    self.caught_fish_count += 1  # 잡은 물고기 수 증가

    def fire_spear(self):  # 작살을 발사
        
        if not self.is_spear_active:  # 작살이 발사 중이 아닐 때만 발사 가능
            self.is_spear_active = True
            self.spear.fire(self.cat_flipped)  #방향에 따라 작살 발사

    def check_spear_collision(self):    # 물고기와 충돌 여부 확인
        
        # 작살의 끝부분 좌표 가져오기
        spear_x, spear_y = self.spear.get_tip_position(self.cat_x, self.cat_y)
        for i, (fish_x, fish_y) in enumerate(self.fish_positions):
            fish_width = self.fish_images[0].width
            fish_height = self.fish_images[0].height

            # 작살 끝부분이 물고기의 사각형 영역 안에 있는지 확인
            if (fish_x <= spear_x <= fish_x + fish_width and
                fish_y <= spear_y <= fish_y + fish_height):
                return i  # 충돌한 물고기의 인덱스 반환
        return None  # 충돌이 없으면 None 반환


    def display_spear(self, screen):       # 작살을 표시
        
        self.spear.draw(screen, self.cat_x, self.cat_y, self.cat_flipped)

    def cat_reached_top(self):  # 고양이의 화면 최상단에 도달 여부 (True면 최상단에 도달, 아니면 False)
        
        return self.cat_y <= 0

    def update_oxygen_time(self):   # 산소 시간을 1초 단위로 감소, 산소가 0이 되면 생명을 감소 및 날짜를 증가
        
        current_time = time.time()
        if current_time - self.last_update_time >= 1:    # 1초가 경과했는지 확인
            self.oxygen_time -= 1                        # 산소 시간 감소
            self.last_update_time = current_time         # 마지막 업데이트 시간 갱신
            self.needs_update = True                     # 화면 업데이트 필요 플래그 설정

            if self.oxygen_time <= 0:   # 산소가 0이 되면
                self.lives -= 1         # 생명 감소
                print(f"남은 목숨: {self.lives}")  # 남은 생명 출력
                self.update_day()  # 날짜 증가

                # 산소 시간 초기화
                self.oxygen_time = 20

                if self.lives > 0:
                    return "title"  # 생명이 남아있으면 타이틀 화면으로 돌아감
                else:
                    self.game_over()  # 생명이 모두 소진되면 게임 오버

    def display_day_and_oxygen(self, screen):   # 화면에 'Day - 숫자'와 산소 시간 표시
       
        draw = ImageDraw.Draw(screen)
        
        # 날짜 표시
        day_text = f"Day - {self.day}"
        draw.text((10, 5), day_text, font=self.font, fill="black")  

        # 산소 시간 텍스트와 아이콘 표시
        oxygen_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        screen.paste(self.oxygen_tank, (10, 30), self.oxygen_tank)  # 산소탱크 아이콘
        oxygen_text = f"{self.oxygen_time}s"                        # 남은 산소 시간
        draw.text((35, 32), oxygen_text, font=oxygen_font, fill="red")  # 산소 시간 표시

    def display_lives(self, screen):    # 생명 표시

        life_x = self.disp.width - 40  # 생명 표시 시작 위치
        life_y = 10                     # 생명 표시 y 좌표
        for i in range(self.lives):  # 남은 생명 수만큼 반복
            screen.paste(self.life_image, (life_x - i * 25, life_y), self.life_image)  # 생명 아이콘 표시

    def display_game_screen(self):  # 게임 화면 업데이트

        screen = self.background.copy()  # 배경 이미지 복사

        # 물고기 그리기
        for i, (x, y) in enumerate(self.fish_positions):
            if self.fish_directions[i] == "left":  # 왼쪽으로 이동 중인 물고기
                screen.paste(self.fish_flipped_images[i], (x, y), self.fish_flipped_images[i])
            else:  # 오른쪽으로 이동 중인 물고기
                screen.paste(self.fish_images[i], (x, y), self.fish_images[i])

        # 보물상자, 고양이, 작살, 상태 정보 표시
        screen.paste(self.treasure_chest_image, (self.treasure_chest_x, self.treasure_chest_y), self.treasure_chest_image)
        screen.paste(self.cat_image, (self.cat_x, self.cat_y), self.cat_image)
        self.display_day_and_oxygen(screen)  # 날짜 및 산소 시간 표시
        self.display_lives(screen)  # 생명 표시
        self.display_spear(screen)  # 작살 표시

        # 화면 크기에 맞게 조정하고 디스플레이에 출력
        screen = screen.resize((self.disp.width, self.disp.height))
        screen = screen.convert("RGB")
        self.disp.image(screen)

    def update_fish_positions(self):    # 물고기들의 위치를 업데이트

        for i in range(len(self.fish_positions)):
            x, y = self.fish_positions[i]
            direction = self.fish_directions[i]
            speed = self.fish_speeds[i]

            # 물고기의 이동 방향에 따라 x 좌표 업데이트
            if direction == "left":
                x -= speed
                if x <= 0:  # 왼쪽 경계 도달 시 방향 변경
                    x = 0
                    self.fish_directions[i] = "right"
            else:
                x += speed
                if x >= self.disp.width - self.fish_images[i].width:  # 오른쪽 경계 도달 시 방향 변경
                    x = self.disp.width - self.fish_images[i].width
                    self.fish_directions[i] = "left"

            # 업데이트된 위치 저장
            self.fish_positions[i] = (x, y)

    def is_near_treasure(self):     # 고양이가 보물상자 근처에 있는지 확인

        # 고양이 중심 좌표 계산
        cat_center_x = self.cat_x + self.cat_image.width // 2
        cat_center_y = self.cat_y + self.cat_image.height // 2
        # 보물상자 중심 좌표 계산
        treasure_center_x = self.treasure_chest_x + self.treasure_chest_image.width // 2
        treasure_center_y = self.treasure_chest_y + self.treasure_chest_image.height // 2

        # 두 중심 사이의 거리 계산
        distance = ((cat_center_x - treasure_center_x) ** 2 + (cat_center_y - treasure_center_y) ** 2) ** 0.5
        return distance < 40  # 거리 기준 

    def display_game_clear_screen(self):    # 게임 클리어 화면

        game_clear_image = Image.open(self.game_clear_image_path).resize((self.disp.width, self.disp.height))
        self.disp.image(game_clear_image)

    def game_over(self):    # 게임 오버 화면을 표시 (하트를 모두 잃었을 경우)
        self.disp.image(self.game_over_image)
        exit()  # 게임 종료

    def display_game_over_screen(self):     # 게임 오버 화면을 표시 (5일이 지났을 경우)
        if self.game_over_image:
            self.disp.image(self.game_over_image)  # 게임오버 이미지 표시
        exit()  # 게임 종료

    def check_game_over_due_to_day(self):   # DAY-5가 끝났고 보물상자를 열지 못했으면 게임오버.
        
        if self.day > 5 and not self.treasure_opened:
            self.display_game_over_screen()  # 게임오버 화면 표시
            exit()  # 게임 종료
