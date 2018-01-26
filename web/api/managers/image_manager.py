from PIL import Image  # 画像処理ライブラリ


class ImageManager:
    def save(self, image_data, path, fileName):
        image_data.save(path + "/" + fileName)

    def save_request_image(self, http_request_image_data, path, fileName):
        image = Image.open(http_request_image_data)
        self.save(image, path, fileName)
        image.close()

    def delete(self, path):
        pass

    def clip(self, data, left, top, width, height):
        pic = Image.open(data)
        # 矩形の範囲
        box = (left, top, left + width, top + height)
        return pic.crop(box)

    # 一回り大きくclip
    def clip_bigger(self, data, left, top, width, height):
        img = Image.open(data)
        img_height = img.size[1]
        img_width = img.size[0]

        new_left = left - width / 3
        if new_left < 0: new_left = 0
        new_top = top - height / 3
        if new_top < 0: new_top = 0

        new_right = new_left + width * 5 / 3
        if new_right > img_width: new_right = img_width
        new_bottom = new_top + height * 5 / 3
        if new_bottom > img_height: new_bottom = img_height

        box = (new_left, new_top, new_right, new_bottom)
        return img.crop(box)
