import numpy as np
from ultralytics.models.yolo import YOLO

import sys
sys.path.append('pytorchvideo')
import cv2

class obj:
    def __init__(self, kind, x_1, y_1, x_2, y_2):
        self.kind = kind
        # Yes, top is min, bottom is max
        # . - - - - > x
        # |
        # |
        # |
        # V
        # y
        self.top = min(y_1, y_2)
        self.bottom = max(y_1, y_2)
        self.left = min(x_1, x_2)
        self.right = max(x_1, x_2)

        self.x = abs(x_1-x_2)
        self.y = abs(y_1-y_2)
        self.ratio = self.y / self.x

        # if self.ratio > accepted_ratios[self.kind]["max"] or self.ratio < accepted_ratios[self.kind]["min"]:
        #     raise RatioError()

    def __repr__(self):
        return f"{self.kind} at ({self.left:3.0f}, {self.top:3.0f}), ({self.right:3.0f}, {self.bottom:3.0f})"
    
def ConvertPredictionToDict(model, pic):
    res = model.predict(pic, verbose=False)[0]
    items = res.names
    classes = np.array(res.boxes.cls.cpu().numpy())
    boxes = np.array(res.boxes.xyxy.cpu().numpy())

    master = {}
    for i in items.items():
        master[i[1]] = []

    for c, b in zip(classes, boxes):
        try:
            master[items[c]].append(obj(items[c], *b))
        except:
            print("Ratio error")
            pass
    return master
    

def rel_pos(model, pic, x_tol=0.25, y_tol=0.1):
    # returns main?, too high?
    def _main_setup(flask, burette):
        if not flask.left - x_tol*flask.x <= burette.left:
            return (False, False)
        if not flask.right + x_tol*flask.x >= burette.right:
            return (False, False)
        if not flask.top - y_tol*flask.y <= burette.bottom:
            return (True, True)
        return (True, False)
    
    def _tile_correct(tile, flask):
        if not tile.top - y_tol*tile.y <= flask.bottom:
            return False
        if not tile.left - x_tol*tile.x <= flask.left:
            return False
        if not tile.right + x_tol*tile.x >= flask.right:
            return False
        return True
    
    def _funnel_not_correct(burette, funnel):
        if not funnel.bottom + y_tol*funnel.y >= burette.top:
            return False
        if not funnel.left - x_tol*funnel.x <= burette.left:
            return False
        if not funnel.right + x_tol*funnel.x >= burette.right:
            return False
        return True
    
    def _biggest(arr, return_index=False):
        area = np.array(map(lambda a: a.x*a.y, arr))
        if return_index:
            return np.argmax(area)
        else:
            return arr[np.argmax(area)]
    
    # Converting predictions into dictionary of objects
    master = ConvertPredictionToDict(model, pic)

    # Plotting for test purposes
    # plttr(pic, master)

    # Evaluating the objects detected
    output = {
        "white_tile_present": None,
        "funnel_present": None,
        "burette_too_high": None,
    }
    
    # Checking for white tile
    if len(master["Conical flask"]) > 0 and len(master["White tile"]) > 0:
        flask = _biggest(master["Conical flask"])
        for tile in master["White tile"]:
            if _tile_correct(tile, flask):
                output["white_tile_present"] = True
                break
        else:
            output["white_tile_present"] = False
    elif len(master["Conical flask"]) > 0:
        output["white_tile_present"] = False
        
    # Checking for funnel
    if len(master["Burette"]) > 0 and len(master["Filter funnel"]) > 0:
        burette = _biggest(master["Burette"])
        for funnel in master["Filter funnel"]:
            if _funnel_not_correct(burette, funnel):
                output["funnel_present"] = True
                break
        else:
            output["funnel_present"] = False
    elif len(master["Burette"]) > 0:
        output["funnel_present"] = False
            
    # Checking for burette too high
    if len(master["Conical flask"]) > 0 and len(master["Burette"]) > 0:
        flask = _biggest(master["Conical flask"])
        for burette in master["Burette"]:
            res = _main_setup(flask, burette)
            if res == (True, True):
                output["burette_too_high"] = True
                break
        else:
            output["burette_too_high"] = False
    return output #main_objs

def plttr(pic: np.ndarray, master: dict, x_tol=0.25, y_tol=0.1, tpe="master"):
    base = pic.copy()
    if tpe == "master":
       objs = [j for i in master.items() for j in i[1]]
    elif tpe == "main":
       objs = [i[1] for i in master.items() if i[1] != []]
    for i in objs:
       cv2.rectangle(base, (int(i.left), int(i.top)), (int(i.right), int(i.bottom)), (57, 255, 20), 1)
       cv2.rectangle(base, (int(i.left-x_tol*i.x), int(i.top-y_tol*i.y)), (int(i.right+x_tol*i.x), int(i.bottom+y_tol*i.y)), (31, 199, 0), 1)
    
    cv2.imshow("", base)
    cv2.waitKey(0)

if __name__ == "__main__":
    # Load the video file
    def load_frame_at_duration(video_path,time=0):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_index = int(fps * time)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        cap.release()
        cv2.destroyAllWindows()
        return frame

    def pad_and_resize(frame, target_size):
        original_height, original_width, _ = frame.shape

        # Calculate the padding size
        max_dim = max(original_height, original_width)
        pad_top = (max_dim - original_height) // 2
        pad_bottom = max_dim - original_height - pad_top
        pad_left = (max_dim - original_width) // 2
        pad_right = max_dim - original_width - pad_left

        # Pad the frame with zeros to make it a square
        padded_frame = cv2.copyMakeBorder(frame, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT, value=[0, 0, 0])

        # Resize the padded frame to (640, 640, 3)
        desired_size = (640, 640)
        resized_frame = cv2.resize(padded_frame, desired_size)
        return resized_frame
    
    video_path = r"C:\Users\zedon\Desktop\PW-samples\S1_incorrect.mp4"
    frame = load_frame_at_duration(video_path, 2)
    resized_frame = pad_and_resize(frame, (640, 640))
    
    model = YOLO("models/object_model.pt")
    print(rel_pos(model, resized_frame))
    
    # cv2.imwrite("frame.png", resized_frame * 255)
    
    cv2.imshow("frame", resized_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()