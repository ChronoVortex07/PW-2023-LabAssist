import numpy as np
import cv2 as cv
import itertools as it
from warnings import warn
from ultralytics import YOLO


# Warnings
class BuretteTooHigh(Warning):
   pass

class NoMainSetup(Warning):
   pass

class WhiteTileNotPresent(Warning):
    pass

class FunnelAboveBurette(Warning):
    pass

class RatioError(Exception):
    pass



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
    

class result:
    def __init__(self, master, **kwargs):
        self.master = master
        for k, v in kwargs.items():
            self.__setattr__(k, v)


def ConvertPredictionToDict(model, pic):
        res = model(pic)[0]
        items = res.names
        classes = np.array(res.boxes.cls.cpu().numpy())
        boxes = np.array(res.boxes.xyxy.cpu().numpy())

        master = {}
        for i in items.items():
            master[i[1]] = []

        for c, b in zip(classes, boxes):
            try:
                master[items[c]].append(obj(items[c], *b))
            except RatioError:
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
    
    def _funnel_notcorrect(burette, funnel):
        if not funnel.bottom + y_tol*funnel.y >= burette.top:
            return False
        if not funnel.left - x_tol*funnel.x <= burette.left:
            return False
        if not funnel.right + x_tol*funnel.x >= burette.right:
            return False
        return True
    
    def _pipette_in_flask(flask, pipette):
        # No tolerance for flask, pipette
        if not flask.top <= pipette.bottom:
            return False
        # Highly likely for this setup to be slanted so can only ensure one condition
        if not flask.left - x_tol*flask.x <= pipette.left and not flask.right + x_tol*flask.x >= pipette.right:
            return False
        return True
    

    def _closest(arr):
        def _dist(o1, o2):
            x1 = np.mean((o1.left, o1.right))
            x2 = np.mean((o2.left, o2.right))
            y1 = np.mean((o1.top, o1.bottom))
            y2 = np.mean((o2.top, o2.bottom))
            return np.sqrt((x1-x2)**2 + (y1-y2)**2)
    
        dist = np.array(map(lambda x: _dist(*x), arr))
        return arr[np.argmin(dist)]
    
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
    main_objs = {"Conical flask_b": [], "Burette": [], "Pipette": [], "Conical flask_p": []}
    too_high = []
    flask_burette = list(it.product(master["Conical flask"], master["Burette"]))
    for i in flask_burette:
        
        res = _main_setup(*i)
        if res == (True, False):
            main_objs["Conical flask_b"].append(i[0])
            main_objs["Burette"].append(i[1])
        elif res == (True, True):
            # sides match, but burette too high
            too_high.append(i)

    # If there exist multiple main setups, take the biggest one
    if len(main_objs["Burette"]) > 0:
        max_index = _biggest(main_objs["Burette"], return_index=True)
        main_objs["Conical flask_b"] = main_objs["Conical flask_b"][max_index]
        main_objs["Burette"] = main_objs["Burette"][max_index]

    # No properly positioned burette, flask found, using closest burette, flask where burette is too high        
    if len(too_high) !=0 and "Conical flask" not in main_objs.keys():
        warn("Lower Your Burette!", BuretteTooHigh)
        closest_obj = _closest(too_high)
        main_objs["Conical flask_b"], main_objs["Burette"] = closest_obj[0], closest_obj[1]

    # Checking of funnel, tile depends on existence of main setup
    if main_objs["Burette"] != []:
        tile_flask =list(it.product(master["White tile"], [main_objs["Conical flask_b"]]))
        for i in tile_flask:
            if _tile_correct(*i):
                main_objs["White tile"] = i[0]
                break
            warn("Place white tile below conical flask!", WhiteTileNotPresent)

        burette_funnel = list(it.product([main_objs["Burette"]], master["Filter funnel"]))
        for i in burette_funnel:
            if _funnel_notcorrect(*i):
                main_objs["Filter funnel"] = i[1]
                warn("Remove filter funnel above burette", FunnelAboveBurette)
                break

    else:
        warn("???", NoMainSetup)

    # # Finding leaky pipette
    # pipette_flask = list(it.product(master["Pipette"], master["Conical flask"]))
    # for i in pipette_flask:
    #     if _pipette_in_flask(*i):
    #         main_objs["Pipette"].append(i[0])
    #         main_objs["Conical flask_p"].append(i[1])
    
    # # If there exist multiple pipette/flask, take the biggest one
    # max_index = _biggest(main_objs["Pipette"], return_index=True)
    # main_objs["Pipette"] = main_objs["Pipette"][max_index]
    # main_objs["Conical flask_p"] = main_objs["Conical flask_p"][max_index]


    # plttr(pic, main_objs, tpe="main")
    print("End")

    # Prepping to return
    res = result(main_objs)
    return main_objs


def plttr(pic: np.ndarray, master: dict, x_tol=0.25, y_tol=0.1, tpe="master"):
    base = pic.copy()
    if tpe == "master":
       objs = [j for i in master.items() for j in i[1]]
    elif tpe == "main":
       objs = [i[1] for i in master.items() if i[1] != []]
    for i in objs:
       cv.rectangle(base, (int(i.left), int(i.top)), (int(i.right), int(i.bottom)), (57, 255, 20), 1)
       cv.rectangle(base, (int(i.left-x_tol*i.x), int(i.top-y_tol*i.y)), (int(i.right+x_tol*i.x), int(i.bottom+y_tol*i.y)), (31, 199, 0), 1)
    
    cv.imshow("", base)
    cv.waitKey(0)


if __name__ == "__main__":
    model = YOLO("models/object_model.pt")
    pic = cv.imread("IMG_3910_cs.jpeg")
    rel_pos(model, pic)