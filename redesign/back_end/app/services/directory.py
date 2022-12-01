
import os
import binascii
import hashlib
from werkzeug.utils import secure_filename
from ..models import File
from ..daos import file_dao


class FileServiceNotInitializedError(Exception):
    pass

class FileService:
    file_dir = None
    def init_app(self, app):
        self.file_dir = app.config['FILEUPLOAD_DIR']
    
    def is_init(func):
        def f(self, *args, **kwargs):
            if self.file_dir is None:
                raise FileServiceNotInitializedError
            return func(self, *args, **kwargs)
        return f
    
    @is_init
    def create(self, file_stream, file_name, owner_id): # TODO owner_id?
        path, md5 = self._save_file(file_stream, file_name)
        file = File(
            name=file_name,
            path=path,
            md5=md5,
            owner_id=owner_id
        )
        file_dao.add(file)
        return file

    def _generate_random_filepath(self):
        random_name = binascii.b2a_hex(os.urandom(10)).decode('utf-8')
        return os.path.join(self.file_dir, random_name)

    def _save_file(self, file_handle, file_name):
        tmp_file = self._generate_random_filepath()
        md5 = hashlib.md5()
        with open(tmp_file, 'wb') as tmp_file_handle:
            while True:
                data = file_handle.read(2048)
                if not data:
                    break
                tmp_file_handle.write(data)
                md5.update(data)
        md5_hexdigest = md5.hexdigest()
        file_path = os.path.join(self.file_dir, secure_filename(f"{md5_hexdigest[:7]}_{file_name}"))
        os.rename(tmp_file, file_path)
        return file_path, md5_hexdigest

    def calc_md5(self, file_handle):
        md5 = hashlib.md5()
        while True:
            data = file_handle.read(2048)
            if not data:
                break
            md5.update(data)
        return md5
    

file_service = FileService()