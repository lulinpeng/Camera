import cv2
import os
import argparse
import logging
import math

class Camera:
    def __init__(self, camera_index:int=None, fps:float=None, width:int=None, height:int=None, cmdfile:str=None):
        logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        logging.getLogger().setLevel(logging.INFO)
        self.logger = logging.getLogger()
        self.camera_index = 0 if camera_index is None else camera_index
        self.cmdfile = 'cmd.txt' if cmdfile is None else cmdfile
        self.fps = 5.0 if fps is None else fps
        self.width = 640 if width is None else width
        self.height = 480 if height is None else height
        self.cap = cv2.VideoCapture(self.camera_index)
        self.logger.info(f'CAP_PROP_FRAME_WIDTH = {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)}')
        self.logger.info(f'CAP_PROP_FRAME_HEIGHT = {self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}')
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.logger.info(f'CAP_PROP_FRAME_WIDTH = {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)}')
        self.logger.info(f'CAP_PROP_FRAME_HEIGHT = {self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}')
        
        # check Video Capture is open
        self.logger.info(f"Is camera open?  {self.cap.isOpened()}")
        return
    
    def show_all_cameras(self):
        cameras = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.read()[0]:
                cameras.append(i)
                cap.release()
            else:
                break
        return cameras
    
    def get_command(self):
        if os.path.isfile(self.cmdfile):
            with open(self.cmdfile) as f:
                cmd = f.read()
                self.logger.info(f'cmdfile: {self.cmdfile}, cmd = {cmd}')
                return cmd
            
    def set_command(self, cmd:str):
        if os.path.isfile(self.cmdfile):
            with open(self.cmdfile, 'w') as f:
                f.write(cmd)
                self.logger.info(f'write command {cmd} into cmdfile {self.cmdfile}')
                return cmd
    
    # collect images from camera
    def collect(self, outdir:str=None, batchfile:str=None):
        outdir = 'collect_pics' if outdir is None else outdir
        batchfile = 'batch.txt' if batchfile is None else batchfile
        os.makedirs(outdir, exist_ok=True)
        MAX_IMG_ID = 1000000
        img_id = 0
        imgs = []
        batch_id = 0
        while True:
            cmd = self.get_command()
            if cmd == 'stop' or cmd == 'end':
                self.set_command('')
                break
            elif cmd == 'batch':
                if os.path.isfile(batchfile):
                    with open(batchfile) as f:
                        img_paths = f.readlines()
                        img_paths = [img_path.strip() for img_path in img_paths]
                        for img_path in img_paths:
                            if os.path.exists(img_path):
                                os.remove(img_path)
                self.logger.info(f'save batch')
                with open(batchfile, 'w') as f:
                    self.logger.info(imgs)
                    f.write(f'{str(batch_id).zfill(6)}\n')
                    batch_id += 1
                    f.write('\n'.join(imgs))
                    imgs = []
                self.set_command('')
            success, img = self.cap.read() # read a frame
            if success:
                cv2.imshow("Image", img)
                interval = round(1000 / self.fps)
                img_path = os.path.abspath(os.path.join(outdir, f'{str(img_id).zfill(math.ceil(math.log10(MAX_IMG_ID)))}.jpg'))
                img_id = (img_id + 1) % MAX_IMG_ID
                self.logger.info(f'collect image {img_path}')
                cv2.imwrite(img_path, img)
                imgs.append(img_path)
                cv2.waitKey(interval)
            else:
                self.logger.info(f'success {success}')
                break
        return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Camerat Tools')
    subparsers = parser.add_subparsers( dest="command", title="available commands", metavar="command")
    parser_encode = subparsers.add_parser("collect", help="collect images from camera", description="collect images from camera")
    parser_encode.add_argument('--fps', type=float, default=None, help='frames per second')
    parser_encode.add_argument('--camera', type=int, choices = [0, 1, 2], default = 0,  help='0 for usb camera, 1 for built-in camera, and 2 for iPhone camera')
    
    parser_encode = subparsers.add_parser("show", help="show all availiable cameras", description="show all availiable cameras")
    args = parser.parse_args()
    
    if not hasattr(args, "command") or args.command is None:
        parser.print_help()
    if args.command == 'collect':
        print(f'+++++ collect +++++')
        camera = Camera(fps = args.fps, camera_index = args.camera)
        camera.collect()
    elif args.command == 'show':
        print(f'+++++ show +++++')
        camera = Camera()
        cameras = camera.show_all_cameras()
        print(f'All availiable cameras are {cameras}')