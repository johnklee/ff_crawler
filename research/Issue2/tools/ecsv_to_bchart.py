#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

r'''
This toolkit is used to translate the evaluation result as CSV to bar chart
for better interpretation
'''
from termgraph import draw_chart
import pandas as pd
import os
import logging
import coloredlogs
import argparse


################################
# Constants
################################
MODU_PATH = os.path.dirname(__file__) if os.path.dirname(__file__) else './'
''' Path of current module '''

LOGGER_FORMAT = "%(threadName)s/%(levelname)s: <%(pathname)s#%(lineno)s> %(message)s"
''' Format of Logger '''

LOGGER_LEVEL = 20  # CRITICAL=50; ERROR=40; WARNING=30; INFO=20; DEBUG=10
''' Message level of Logger '''


################################
# Global Variables
################################
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(LOGGER_LEVEL)
logger.propagate = False
coloredlogs.install(
    level=LOGGER_LEVEL,
    logger=logger,
    fmt=LOGGER_FORMAT)
''' logger initialization '''


################################
# Main
################################
def main():
    parser = argparse.ArgumentParser(description='Utility to draw bar chart of TE evaluation result as CSV.')
    parser.add_argument('csv_path', type=str, help='CSV file path to work on')
    parser.add_argument('--type', type=str, default='token_match', choices={'token_match', 'line_match', 'sequence_match'}, help='Metric type. (default:%(default)s)')
    parser.add_argument('--show_th', type=float, default=0.8, help='Show record with score under than the setting here (default=%(default)s)')
    args = parser.parse_args()

    if os.path.isfile(args.csv_path):
        show_list = []
        df = pd.read_csv(args.csv_path, names=['doc_id', 'type', 'score'])
        logger.info('Head(n=5) of loading dataframe:\n{}\n'.format(str(df.head(n=5))))
        dist_dict = {"{}-{}".format((rank + 1) * 10, rank * 10): 0 for rank in range(9, -1, -1)}  # Key as score range; value as count
        for ri, row in df.iterrows():
            if row['type'] == args.type:
                rank = int(float(row['score']) * 10)
                if rank < 0:
                    continue

                rank = 9 if rank == 10 else rank
                key = "{}-{}".format((rank + 1) * 10, rank * 10)
                dist_dict[key] = dist_dict.get(key, 0) + 1
                if row['score'] < args.show_th:
                    show_list.append((row['score'], row['doc_id']))

        draw_chart(dist_dict, title="===== {} distribution ({{data_sum:,d}}) =====".format(args.type))
        if len(show_list) > 0:
            show_list = sorted(show_list, key=lambda t: t[0])
            logger.info("\nExample list ({:,d}):\n{}\n".format(len(show_list), '\n'.join(list(map(lambda t: "{}\t{:.02f}".format(t[1], t[0]), show_list)))))
    else:
        logger.error('{} does not exist!'.format(args.csv_path))


if __name__ == '__main__':
    main()
