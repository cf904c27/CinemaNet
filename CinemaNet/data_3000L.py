# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/05-1-MNetV2-100x177-3000L.ipynb (unless otherwise specified).

__all__ = ['get_labels', 'path', 'il_train', 'il_valid', 'regex', 'fnames_all', 'count', 'train_fnames',
           'samples_per_label', 'fnames_train', 'fnames_valid', 'lls', 'get_data_3000L']

# Cell
from fastai.vision import *
from fastai.callbacks import SaveModelCallback, EarlyStoppingCallback, CSVLogger
from .train_utils import *
from .custom_head import *
from .wandb import *
from .MixMatch import *

import wandb

# Cell
path = Path('/home/rahul/github_projects/CinemaNet/')

def get_labels(f):
    if re.search(f"{regex['EWS']}", str(f)): return 'Extreme Wide'
    if re.search(f"{regex['LS']}",  str(f)): return 'Long'
    if re.search(f"{regex['MS']}",  str(f)): return 'Medium'
    if re.search(f"{regex['MCU']}", str(f)): return 'Medium Close-Up'
    if re.search(f"{regex['CU']}",  str(f)): return 'Close-Up'
    if re.search(f"{regex['ECU']}", str(f)): return 'Extreme Close-Up'

# Cell
il_train = ImageList.from_folder(path/'train', presort=True)
il_valid = ImageList.from_folder(path/'valid', presort=True)
regex = {
    'CU' : '\/Close\-Up\/',
    'ECU': '\/Extreme Close\-Up\/',
    'EWS': '\/Extreme Wide\/',
    'LS' : '\/Long\/',
    'MS' : '\/Medium\/',
    'MCU': '\/Medium Close\-Up\/'
}

# Cell
fnames_all   = list(il_train.items) + list(il_valid.items)
count        = {}
train_fnames = {}
samples_per_label = 500


for key in regex:
    i=0
    train_fnames[key] = []
    for f in fnames_all:
        if re.search(f"{regex[key]}.*", str(f)):
            i+=1
            count[key] = i
            train_fnames[key].append(f)
            if i >= samples_per_label: break;
count

# Cell
fnames_train = sum(train_fnames.values(),[])
fnames_valid = list(set(fnames_all) - set(fnames_train))

# Cell
lls = LabelLists(path,
                 train=ImageList(fnames_train),
                 valid=ImageList(fnames_valid))

# Cell
def get_data_3000L(img_size, tfms=get_transforms(max_zoom=1.), batch_size=64):
    data = (lls
            .label_from_func(get_labels)
            .transform(tfms=get_transforms(max_zoom=1.),
                       size=img_size,
                       resize_method=ResizeMethod.SQUISH)
            .databunch(bs=batch_size).normalize(imagenet_stats))
    return data