import json
import base64
import string
import random
import cv2 as cv
import numpy as np

from .models import Thing, Image, ImageTag
from .utils import image_recognition, qr_decoder, barcode_decoder

from typing import Optional, Tuple
from io import BytesIO
from PIL import Image as Img

from django.core.files.images import ImageFile
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

class ImageRecognitionConsumer(AsyncWebsocketConsumer):
    thing_id: Optional[int] = None

    async def connect(self) -> None:
        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        await self.close()

    async def receive(self, text_data: Optional[str] = None, bytes_data: Optional[bytes] = None) -> None:
        video_frame_after = None

        if text_data:
            self.thing_id = int(text_data)

        if bytes_data:
            video_frame_bytes_io = BytesIO(bytes_data)
            video_frame = Img.open(video_frame_bytes_io)

            images = await self.get_images()

            for image_object in images:
                image_bytes_io = self.read_image_bytes_and_convert_to_bytesio(image_object)

                image = Img.open(image_bytes_io)
                try:
                    video_frame_after, count_of_good_matches = image_recognition(video_frame, image)
                    if count_of_good_matches > 70:
                        break
                    else:
                        video_frame_after = video_frame
                        continue
                except:
                    video_frame_after = video_frame
            buffered = BytesIO()
            video_frame_after.save(buffered, format="JPEG")
            modified_frame_data = base64.b64encode(buffered.getvalue()).decode('utf-8')

            await self.send(modified_frame_data)
        else:
            await self.send(text_data=json.dumps({'status': 'error', 'message': 'No video frame data received'}))

    @staticmethod
    def read_image_bytes_and_convert_to_bytesio(image: Image) -> BytesIO:
        image_bytes = image.image.file.file.read()
        image_bytes_io = BytesIO(image_bytes)
        return image_bytes_io

    @database_sync_to_async
    def get_images(self) -> list:
        images = list(Image.objects.filter(thing__id=self.thing_id).exclude(tag__name="QRCODE"))
        return images

class AddImageConsumer(AsyncWebsocketConsumer):
    thing_id: Optional[int] = None

    async def connect(self) -> None:
        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        await self.close()

    async def receive(self, text_data: Optional[str] = None, bytes_data: Optional[bytes] = None) -> None:
        qr_code_data = None
        barcode = None
        message = ""

        if text_data:
            self.thing_id = int(text_data)

        if bytes_data:
            screenshot_bytes_io = BytesIO(bytes_data)

            thing = await database_sync_to_async(self.get_thing)()
            raw_image = Img.open(screenshot_bytes_io)

            try:
                barcode = barcode_decoder(raw_image)
                _, tag_name, barcode_data = barcode
                await self.update_barcode(barcode_data)

            except:
                pass

            try:
                qr_code = qr_decoder(raw_image)
                image, tag_name, qr_code_data = qr_code
                img_byte_arr = BytesIO()
                image.save(img_byte_arr, format='JPEG')

            except:
                img_byte_arr = screenshot_bytes_io

            end_image = ImageFile(img_byte_arr, name=self.get_random_name())

            if qr_code_data:
                try:
                    tag = await database_sync_to_async(self.get_image_tag)("QRCODE")
                    await Image.objects.acreate(thing=thing, image=end_image, tag=tag)
                    message = "QRCODE found."
                except:
                    pass
            else:
                await Image.objects.acreate(thing=thing, image=end_image)
            if barcode:
                message += "\nBarcode found."

            modified_frame_data = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            await self.send(json.dumps({"image": modified_frame_data, "message": message}))

    def get_thing(self) -> Thing:
        return Thing.objects.get(id=self.thing_id)

    @database_sync_to_async
    def update_barcode(self, barcode: str) -> int:
        return Thing.objects.filter(id=self.thing_id).update(barcode=barcode)

    @staticmethod
    def get_image_tag(tag_name: str) -> ImageTag:
        return ImageTag.objects.get(name=tag_name)

    @staticmethod
    def get_random_name() -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=30)) + ".jpg"

class ScannerConsumer(AsyncWebsocketConsumer):
    thing_id: Optional[int] = None

    async def connect(self) -> None:
        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        await self.close()

    async def receive(self, text_data: Optional[str] = None, bytes_data: Optional[bytes] = None) -> None:
        if bytes_data:
            matched_thing = None
            barcode_type = None
            qr_code_type = None
            barcode_data = None

            video_frame_bytes_io = BytesIO(bytes_data)
            video_frame = Img.open(video_frame_bytes_io)

            try:
                barcode = barcode_decoder(video_frame)
                _, barcode_type, barcode_data = barcode

            except:
                pass

            try:
                result = qr_decoder(video_frame)
                code_image, qr_code_type, code_data = result
            except:
                code_image = video_frame

            if qr_code_type:
                all_images = await self.get_qr_code_images()

                for image_object in all_images:
                    qr_code_image_bytes = image_object.image.file.file.read()
                    qr_code_image_bytes_io = BytesIO(qr_code_image_bytes)
                    qr_code_image = Img.open(qr_code_image_bytes_io)
                    video_frame_after, count_of_good_matches = image_recognition(code_image, qr_code_image)
                    if count_of_good_matches > 50:
                        matched_thing_list = await self.get_thing_id(image_object.id)
                        matched_thing = matched_thing_list[0]
                        break

                else:
                    error_message = "QRCODE doesn\'t match any item."
                    await self.send(text_data=json.dumps({'status': 'error', 'message': error_message}))

            elif barcode_type:
                try:
                    matched_thing_list = await self.get_thing_codes(barcode_data)
                    matched_thing = matched_thing_list[0]
                except:
                    error_message = 'Barcode doesn\'t match any item.'
                    await self.send(text_data=json.dumps({'status': 'error', 'message': error_message}))

            if matched_thing:
                await self.send(json.dumps({"found_thing": matched_thing.name, 'thing_id': matched_thing.id,
                                            'thing_description': matched_thing.description}))

    @database_sync_to_async
    def get_qr_code_images(self) -> list:
        return list(Image.objects.filter(tag__name="QRCODE"))

    @database_sync_to_async
    def get_thing_id(self, img_id: int) -> list:
        return list(Thing.objects.filter(image__id=img_id))

    @database_sync_to_async
    def get_thing_codes(self, barcode: str) -> list:
        return list(Thing.objects.filter(barcode=barcode))
