import fnmatch as fn
import os
import re
from vectorModel import *
from rnnLSTM import RnnLSTM, RnnDense, RnnDense2, RnnAttentionDense2, RnnConvDense, EnsembleModel
import utils
import random

if __name__ == '__main__':
    import pickle as pkl
    import sys

    import argparse


    def listparse(arg):
        return arg.split(',')


    parser = argparse.ArgumentParser()
    parser.add_argument('command',
                        choices=['train', 'test', 'predict'],
                        help='train/test/predict')
    parser.add_argument('-p', '--project',
                        default='linux',
                        help='project name, should be a subdir in data')
    parser.add_argument('-l', '--langs',
                        type=listparse,
                        default=['c', 'h'],
                        help='languages to use as a comma separated list')
    parser.add_argument('--restore',
                        help='file from which to restore parameters for testing or resuming training')
    parser.add_argument('--ckpt',
                        default='',
                        help='prefix of checkpoint files')
    parser.add_argument('--win',
                        type=int,
                        default=40,
                        help='window size')
    parser.add_argument('--dim',
                        type=int,
                        default=32,
                        help='word vector dimensions')
    parser.add_argument('--filt',
                        type=int,
                        default=7,
                        help='convolution filt size')
    parser.add_argument('--cdim',
                        type=int,
                        default=64,
                        help='number of convolution filters')
    parser.add_argument('--zdim',
                        type=int,
                        default=512,
                        help='intermediate vector dimensions')
    parser.add_argument('--zdim2',
                        type=int,
                        default=512,
                        help='intermediate vector dimensions #2')
    parser.add_argument('--lr',
                        type=float,
                        default=0.05,
                        help='learning rate')
    parser.add_argument('--reg',
                        type=float,
                        default=0.0,
                        help='regularization constant')
    parser.add_argument('--batch',
                        type=int,
                        default=32,
                        help='batch size')
    parser.add_argument('--files',
                        type=listparse,
                        help='list of files for prediction')
    args = parser.parse_args()

    keywords = []
    keywords_file = os.path.join('../key_words', args.project)
    with open(keywords_file) as fp:
        for line in fp:
            kw = re.sub(' [0-9]*$', '', line.strip())
            keywords.append(kw)
    print(keywords)

    if args.command == 'test':
        model = EnsembleModel(keywords, winSize=args.win)
    else:
        model = RnnAttentionDense2(keywords, winSize=args.win,
                                   wdim=args.dim, zdim=args.zdim, zdim2=args.zdim2,
                                   reg=args.reg,
                                   load_from_file=False)

    if args.restore is not None:
        model.restoreFrom(args.restore)
        print('Restored model from %s' % args.restore)

    data_dir = os.path.join('../data', args.project)
    files = utils.matchingFiles([data_dir], args.langs)
    filesAndTokens = []

    # choose the first half of files based on a deterministic random range
    robj = random.Random(12345)
    robj.shuffle(files)

    if args.command == 'train':
        fileSubset = files[:len(files) / 2]
    elif args.command == 'test':
        fileSubset = files[len(files) / 2:]
    else:
        fileSubset = files[len(files) / 2:]

    if args.command == 'train' or args.command == 'test':
        for i, name in enumerate(fileSubset):
            if i % 1000 == 0:
                print('%d files done' % i)
            filesAndTokens.append((name, utils.tokenize(name)))
        print(len(filesAndTokens))
        print(sum([len(tokens) for name, tokens in filesAndTokens]))

    #    model = PositionDependentVectorModel(keywords, winSize=args.win,
    #                                         wdim=args.dim, stepsize=args.lr,
    #                                         reg=args.reg)
    #    model = ConstantAttentionVectorModel(keywords, winSize=args.win,
    #                                         wdim=args.dim, stepsize=args.lr,
    #                                         reg=args.reg)
    #    model = NonLinearVectorModel(keywords, winSize=args.win,
    #                                 wdim=args.dim, zdim=args.zdim,
    #                                 stepsize=args.lr,
    #                                 reg=args.reg)
    #    model = RnnDense(keywords, winSize=args.win,
    #                    wdim=args.dim, zdim=args.zdim,
    #                    reg=args.reg,
    #                    load_from_file=False)
    #                    stepsize=args.lr,
    #                    reg=args.reg)
    #    model = RnnConvDense(keywords, winSize=args.win,
    #                         wdim=args.dim, kSize=args.filt, convdim=args.cdim,
    #                         zdim=args.zdim,
    #                         reg=args.reg,
    #                         load_from_file=False)

    if args.command == 'test':
        model.test(filesAndTokens, batchsize=args.batch)

    elif args.command == 'predict':
        predictionFiles = []
        if args.files is None:
            for _ in range(100):
                randomFile = random.choice(fileSubset)
                predictionFiles.append(randomFile)
        else:
            predictionFiles = args.files

        for fileName in predictionFiles:
            outputFile = os.path.basename(fileName) + '.html'
            print('Evaluating on %s' % fileName)
            tokens, content = utils.tokenize(fileName, True)
            annotations, candidates, attentions = model.testOverlap(tokens)
            spans = utils.matchTokensToContent(tokens, content)
            assert len(spans) == len(tokens)
            contentAnns = [-1 for _ in range(len(content))]
            for ann, span in zip(annotations, spans):
                for ia, a in enumerate(ann):
                    contentAnns[ia + span[0]] = a

            print('Generating %s' % outputFile)

            with open(outputFile, 'w') as fp:
                # print >> fp, utils.HTMLHeader()
                # print >> fp, utils.colorizedHTML(content, contentAnns, spans)
                # print >> fp, utils.HTMLFooter(candidates, attentions)
                pass

    else:
        model.train(filesAndTokens, ckpt_prefix=args.ckpt, batchsize=args.batch)
