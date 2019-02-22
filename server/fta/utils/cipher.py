# coding: utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import base64

from Crypto.Cipher import AES

try:
    from django.conf import settings
except ImportError:
    from fta import settings


class AESCipher(object):
    BLOCK_LENGTH = 16

    @classmethod
    def format_data(cls, data, size):
        if len(data) == size:
            return data
        array = [0 for i in range(size)]
        for i, d in enumerate(data):
            array[i % size] ^= ord(d)
        return b"".join(map(lambda x: chr(x % 256), array))

    @classmethod
    def default_cipher(cls):
        if getattr(settings, "NO_CIPHER_SECRET", False):
            return None
        return cls(key=settings.APP_SECRET_KEY)

    def __init__(self, key, iv=None):
        self.key = self.format_data(key, self.BLOCK_LENGTH)
        self.iv = self.format_data(iv or key, self.BLOCK_LENGTH)

    @property
    def cipher(self):
        return AES.new(self.key, AES.MODE_CBC, self.iv)

    def encrypt(self, bin_data):
        bin_length = len(bin_data)
        candidate_cnt = bin_length % self.BLOCK_LENGTH
        if candidate_cnt:
            bin_data += b"\0" * (
                self.BLOCK_LENGTH - candidate_cnt
            )
        return base64.b64encode(self.cipher.encrypt(bin_data))

    def decrypt(self, bin_data):
        return self.cipher.decrypt(base64.b64decode(bin_data)).rstrip("\0")
