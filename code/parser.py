import argparse
from torch import cuda



def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def args():
    parser = argparse.ArgumentParser(description="eye-tracker-model.")
    parser.add_argument("--tensorboard", help="ask if store the output to tensorboard",
                        type=str2bool, default=False)
    parser.add_argument("--comment", type=str, default="test")
    parser.add_argument("--batch_size", type=int, default= cuda.device_count()*100 if cuda.device_count() != 0 else 4)
    parser.add_argument("--doload", type=str2bool, help="load previous weights or not", default=True)
    parser.add_argument("--weights", type=str, default="",help="weight file location")
    parser.add_argument("--epochs", type=int, default=100, help="traing total epochs")
    parser.add_argument("--lr", type=float, default=1e-4, help="base learning rate")
    parser.add_argument("--opt", type=str, default="adam", help="choose optimizer in [adam, SGD]")
    parser.add_argument("--sigmoid", type=str2bool, default=False, help="use simoid activation function in the last layer or not")
    parser.add_argument("--delta", type=float, default=0.001, help="Tolerance for early stoping")
    parser.add_argument("--tag", type=str, default='', help="suffix of the weight file")
    parser.add_argument("--eval", type=str2bool, default=False, help="start eval mode")
    parser.add_argument("--evalFolder", type=int, default=3, help="choose a test folder to generate prediction")
    parser.add_argument("--resize", type=str2bool, default=False, help="resize picture to 256X256 (original 576X720)")
    parser.add_argument("--generating", type=str2bool, default=False, help="generating the gradient heat map over the origin image")
    parser.add_argument("--collect", type=str2bool, default=False, help="collect the intermediate embedding to middle.npy")
    parser.add_argument("--activation", type=str, default="none", help="choose the activation function to generate intermediate embedding")
    return parser