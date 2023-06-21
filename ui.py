from argparse import ArgumentParser


def handle_args(parser: ArgumentParser):
    # handle arguments

    parser.add_argument('-d', dest='dataset_filepath', type=str,
                        help='A cap*.txt file. If ommited will read all files inside datasets/')
    parser.add_argument('-i', dest='n_iter', type=int,
                        help='Amount of iterations. Default = 5')
    parser.add_argument('-r', dest='relaxed', type=bool,
                        help='True if relaxed, false or omitted if not')

    return parser.parse_args()
