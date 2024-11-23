from PIL import Image

class Spear:
    def __init__(self, disp, cat_width, rope_image_path):
        self.disp = disp
        self.spear_active = False  # 작살 발사 여부
        self.spear_direction = None  # 작살 방향
        self.spear_progress = 0  # 작살 진행 상태
        self.spear_speed = 0.2  # 작살 이동 속도
        self.spear_length = int(self.disp.width / 3)  # 작살 최대 길이
        self.cat_width = cat_width  # 고양이 이미지의 너비
        self.rope_image = Image.open(rope_image_path).resize((self.spear_length, 10))  # 밧줄 이미지

    def fire(self, flipped):
        """작살 발사 시작"""
        if not self.spear_active:
            self.spear_active = True
            self.spear_direction = "right" if flipped else "left"  # 방향 설정
            self.spear_progress = 0

    def update(self):
        """작살 상태 업데이트"""
        if self.spear_active:
            if self.spear_progress < 1:  # 작살 나가는 중
                self.spear_progress += self.spear_speed
            elif self.spear_progress >= 1 and self.spear_progress < 2:  # 작살 되돌아오는 중
                self.spear_progress += self.spear_speed
            else:  # 작살 동작 종료
                self.spear_active = False  # 작살 비활성화
                self.spear_progress = 0
                print("Spear finished and reset.")  # 디버깅용 메시지



    def draw(self, screen, cat_x, cat_y, flipped):
        """밧줄 이미지를 화면에 그립니다."""
        if self.spear_active:
            progress = self.spear_progress if self.spear_progress <= 1 else 2 - self.spear_progress
            spear_x = cat_x + self.cat_width // 2  # 고양이 중심에서 시작
            spear_y = cat_y + self.cat_width // 2

            if self.spear_direction == "left":
                end_x = spear_x - int(self.spear_length * progress)
                rope_image = self.rope_image.transpose(Image.FLIP_LEFT_RIGHT)  # 좌우 반전
            elif self.spear_direction == "right":
                end_x = spear_x + int(self.spear_length * progress)
                rope_image = self.rope_image

            # 밧줄 이미지의 길이를 잘라서 동적으로 출력
            rope_crop_width = abs(end_x - spear_x)  # 현재 진행 상태에 따른 밧줄 길이
            cropped_rope = rope_image.crop((0, 0, rope_crop_width, rope_image.height))

            if self.spear_direction == "right":
                screen.paste(cropped_rope, (spear_x, spear_y - rope_image.height // 2), cropped_rope)
            elif self.spear_direction == "left":
                screen.paste(cropped_rope, (spear_x - rope_crop_width, spear_y - rope_image.height // 2), cropped_rope)

    def get_tip_position(self, cat_x, cat_y):
        """작살 끝부분의 위치를 반환"""
        progress = self.spear_progress if self.spear_progress <= 1 else 2 - self.spear_progress
        spear_x = cat_x + self.cat_width // 2
        spear_y = cat_y + self.cat_width // 2

        if self.spear_direction == "left":
            tip_x = spear_x - int(self.spear_length * progress)
        elif self.spear_direction == "right":
            tip_x = spear_x + int(self.spear_length * progress)
        return tip_x, spear_y
