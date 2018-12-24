from config.tg_app_credentials import tg_session, tg_api_id, tg_api_hash
import hashlib
from io import BytesIO
import sys
from telethon import TelegramClient, custom, errors, events, functions, helpers, types, utils, sync
from telethon.client import TelegramBaseClient, UserMethods


class TelegramFileManager(object):
    def __init__(self, tg_session, tg_api_id, tg_api_hash, loop=None):
        super(TelegramFileManager, self).__init__()
        self.client = TelegramClient(tg_session, tg_api_id, tg_api_hash, loop=loop)
        self.client.start()

    def upload(self, file, file_name=None):
        entity = types.InputPeerSelf()

        # begin _file_to_media
        media = None
        file_handle = None

        # begin _upload_file
        file_id = helpers.generate_random_long()

        if not file_name and getattr(file, 'name', None):
            file_name = file.name
            if file_name is None:
                file_name = str(file_id)

        file = file.read()
        file_size = len(file)
        part_size = int(utils.get_appropriated_part_size(file_size) * 1024)

        is_large = file_size > 10 * 1024 * 1024
        hash_md5 = hashlib.md5()
        if not is_large:
            hash_md5.update(file)

        part_count = (file_size + part_size - 1) // part_size

        with BytesIO(file) as stream:
            for part_index in range(part_count):
                part = stream.read(part_size)

                if is_large:
                    request = functions.upload.SaveBigFilePartRequest(
                        file_id, part_index, part_count, part)
                else:
                    request = functions.upload.SaveFilePartRequest(
                        file_id, part_index, part)

                result = self.client(request)
                yield float(round(100.0 * (part_index/part_count), 2))
                if not result:
                    raise RuntimeError(
                        'Failed to upload file part {}.'.format(part_index))

        if is_large:
            file_handle = types.InputFileBig(file_id, part_count, file_name)
        else:
            file_handle = custom.InputSizedFile(
                file_id, part_count, file_name, md5=hash_md5, size=file_size)
        # end _upload_file

        attributes, mime_type = utils.get_attributes(
            file, force_document=True, voice_note=False, video_note=False)
        attributes[0].file_name = file_name

        media = types.InputMediaUploadedDocument(
            file=file_handle,
            mime_type=mime_type,
            attributes=attributes
        )
        # end _file_to_media

        request = functions.messages.SendMediaRequest(
            entity, media, reply_to_msg_id=None, message='',
            entities=[], reply_markup=None, silent=None
        )
        t = self.client(request)
        if type(t) != types.Updates:
            t = self.client.loop.run_until_complete(t)
        msg = self.client._get_response_message(request,
            t, entity)
        yield msg

    def download(self, input_location):
        part_size = 64 * 1024

        dc_id, input_location = utils.get_input_location(input_location)
        exported = dc_id and self.client.session.dc_id != dc_id
        if exported:
            try:
                sender = TelegramFileManager.wait(TelegramBaseClient._borrow_exported_sender(dc_id))
            except errors.DcIdInvalidError:
                config = TelegramFileManager.wait(self(functions.help.GetConfigRequest()))
                for option in config.dc_options:
                    if option.ip_address == self.client.session.server_address:
                        self.client.session.set_dc(
                            option.id, option.ip_address, option.port)
                        self.client.session.save()
                        break

                sender = self.client._sender
                exported = False
        else:
            sender = self.client._sender

        try:
            offset = 0
            while True:
                try:
                    result = TelegramFileManager.wait(sender.send(functions.upload.GetFileRequest(
                        input_location, offset, part_size
                    )))
                    if isinstance(result, types.upload.FileCdnRedirect):
                        raise NotImplementedError
                except errors.FileMigrateError as e:
                    sender = TelegramFileManager.wait(TelegramBaseClient._borrow_exported_sender(e.new_dc))
                    exported = True
                    continue

                offset += part_size
                if not result.bytes:
                    break

                yield result.bytes
        finally:
            if exported:
                TelegramFileManager.wait(self._return_exported_sender(sender))
            elif sender != self.client._sender:
                sender.disconnect()


def main():
    if len(sys.argv) < 2:
        print('Syntax: python telegramfilemanager.py path/to/file')
        quit()
    path = ' '.join(sys.argv[1:])
    tfm = TelegramFileManager(tg_session, tg_api_id, tg_api_hash)

    print('\n')
    for step in tfm.upload(open(path, 'rb'), file_name=path.split('/')[-1]):
        if type(step) == float:
            print(step, end='%\r')
        else:
            print(step.stringify())


if __name__ == '__main__':
	main()

