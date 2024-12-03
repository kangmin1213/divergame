from PIL import Image

class Spear:
    def __init__(self, disp, cat_width, rope_image_path):
        
        self.disp = disp
        self.spear_active = False        # 작살이 현재 발사 중인지 여부
        self.spear_direction = None      # 작살 발사 방향 
        self.spear_progress = 0          # 작살의 진행 상태 
        self.spear_speed = 0.3           # 작살 이동 속도 
        self.spear_length = int(self.disp.width / 3)  # 작살의 최대 길이
        self.cat_width = cat_width       # 고양이 이미지의 너비
        # 밧줄 이미지를 불러오고 크기를 조정
        self.rope_image = Image.open(rope_image_path).resize((self.spear_length, 10))

    def fire(self, flipped):
        """
        작살 발사
        flipped: 고양이의 방향 (True: 오른쪽, False: 왼쪽)
        """
        if not self.spear_active:
            self.spear_active = True  # 작살 활성화
            self.spear_direction = "right" if flipped else "left"  # 발사 방향 설정
            self.spear_progress = 0  # 진행 상태 초기화

    def update(self):
        """
        작살 상태를 업데이트
        작살이 발사되고 돌아오는 과정을 처리
        """
        if self.spear_active:
            if self.spear_progress < 1:  # 작살이 나가는 중
                self.spear_progress += self.spear_speed
            elif self.spear_progress >= 1 and self.spear_progress < 2:  # 작살이 돌아오는 중
                self.spear_progress += self.spear_speed
            else:  # 작살 동작 완료
                self.spear_active = False  # 작살 비활성화
                self.spear_progress = 0  # 진행 상태 초기화
            

    def draw(self, screen, cat_x, cat_y, flipped):
        
        if self.spear_active:
            # 진행 상태에 따라 작살의 길이를 계산
            progress = self.spear_progress if self.spear_progress <= 1 else 2 - self.spear_progress
            spear_x = cat_x + self.cat_width // 2  # 고양이 중심 x 좌표
            spear_y = cat_y + self.cat_width // 2  # 고양이 중심 y 좌표

            if self.spear_direction == "left":
                end_x = spear_x - int(self.spear_length * progress)  # 왼쪽으로 작살 진행
                rope_image = self.rope_image.transpose(Image.FLIP_LEFT_RIGHT)  # 밧줄 이미지 좌우 반전
            elif self.spear_direction == "right":
                end_x = spear_x + int(self.spear_length * progress)  # 오른쪽으로 작살 진행
                rope_image = self.rope_image

            # 진행 상태에 맞게 밧줄 이미지를 잘라냄
            rope_crop_width = abs(end_x - spear_x)  # 밧줄의 현재 길이
            cropped_rope = rope_image.crop((0, 0, rope_crop_width, rope_image.height))

            # 밧줄 이미지를 화면에 출력
            if self.spear_direction == "right":
                screen.paste(cropped_rope, (spear_x, spear_y - rope_image.height // 2), cropped_rope)
            elif self.spear_direction == "left":
                screen.paste(cropped_rope, (spear_x - rope_crop_width, spear_y - rope_image.height // 2), cropped_rope)

    def get_tip_position(self, cat_x, cat_y):
       
        # 작살의 진행 상태에 따른 끝부분 좌표 계산
        progress = self.spear_progress if self.spear_progress <= 1 else 2 - self.spear_progress
        spear_x = cat_x + self.cat_width // 2  # 고양이 중심 x 좌표
        spear_y = cat_y + self.cat_width // 2  # 고양이 중심 y 좌표

        if self.spear_direction == "left":
            tip_x = spear_x - int(self.spear_length * progress)
        elif self.spear_direction == "right":
            tip_x = spear_x + int(self.spear_length * progress)
        return tip_x, spear_y  # 끝부분 좌표 반환
