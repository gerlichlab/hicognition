
import os
import binascii
import hashlib
from werkzeug.utils import secure_filename
from ..models import File, PhysicalFile
from ..daos import file_dao, physicalfile_dao


class FileServiceNotInitializedError(Exception):
    pass
class FileHashIncorrectException(Exception):
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
    def create(self, file_hash, file_stream, file_name, user_id):
        # save file to temporary dir and get md5, then check if md5 is correct
        temp_path, md5 = self._save_file_temp(file_stream, file_name)
        if md5 != file_hash:
            os.remove(temp_path)
            raise FileHashIncorrectException
        
        physical_file = physicalfile_dao.get_by_hash(md5)
        if not physical_file:
            path = os.path.join(self.file_dir, secure_filename(f"{md5[:7]}_{file_name}"))
            os.rename(temp_path, path)
            phys_file = PhysicalFile(
                path=path,
                md5=md5
            )
            physicalfile_dao.add(phys_file)
        else:
            os.remove(temp_path)
        
        file = file_dao.get_by_hash_userid(md5, user_id)
        if not file:
            file = File(
                name=file_name,
                md5=md5,
                user_id=user_id
            )
            file_dao.add(file)
        #user.
        return file

    def _generate_random_filepath(self):
        random_name = binascii.b2a_hex(os.urandom(10)).decode('utf-8')
        return os.path.join(self.file_dir, random_name)

    def _save_file_temp(self, file_handle, file_name):
        tmp_file_path = self._generate_random_filepath()
        md5 = hashlib.md5()
        with open(tmp_file_path, 'wb') as tmp_file_handle:
            while True:
                data = file_handle.read(2048)
                if not data:
                    break
                tmp_file_handle.write(data)
                md5.update(data)
        md5_hexdigest = md5.hexdigest()
        return tmp_file_path, md5_hexdigest

    def calc_md5(self, file_handle):
        md5 = hashlib.md5()
        while True:
            data = file_handle.read(2048)
            if not data:
                break
            md5.update(data)
        return md5
    

file_service = FileService()