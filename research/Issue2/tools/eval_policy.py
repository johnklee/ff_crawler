#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

r'''
This toolkit is used to evaluate the validity of created policy.

In order to run this tookit, you can have to provide below two environment variables for sending notification mail:
* EP_SENDER: The email address of sender
* EP_PASSWD: The password of email address
* EP_SMTP: SMTP Server e.g.: smtp.gmail.com:587
'''
import requests
import time
import sys
import os
import logging
import coloredlogs
import argparse
import pandas as pd
import configparser
import schedule
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))   # noqa

from github import Github
from datetime import datetime
from purifier.text_extractor import TEAgent
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


################################
# Constants
################################
MODU_PATH = os.path.dirname(__file__) if os.path.dirname(__file__) else './'
''' Path of current module '''

LOGGER_FORMAT = "%(threadName)s/%(levelname)s: <%(pathname)s#%(lineno)s> %(message)s"
''' Format of Logger '''

LOGGER_LEVEL = 20  # CRITICAL=50; ERROR=40; WARNING=30; INFO=20; DEBUG=10
''' Message level of Logger '''

CFG_PATH = os.path.abspath(os.path.join(MODU_PATH, "{}.ini".format(os.path.basename(__file__).split('.')[0])))
''' Configuration name in default'''

EP_SENDER = os.environ.get('EP_SENDER', '')
''' Sender of notification mail '''

EP_PASSWD = os.environ.get('EP_PASSWD', '')
''' Password of sender mail address '''

EP_SMTP = os.environ.get('EP_SMTP' '')
''' Location of SMTP server '''

CFG_SECT = 'DEFAULT'
''' Configuration section '''

CID_LIST = []
''' List to hold policy ID for evaluation '''

ECID_SET = set()
''' List to hold policy ID for exclusion for evaluation '''

IGNORED_CIDS_FILE = os.path.abspath(os.path.join(MODU_PATH, '.ignored_cids'))
''' File to keep ignored CID list '''

# REQUEST_HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
REQUEST_HEADERS = {'User-Agent': 'My research robot 0.1'}
''' Header of HTTP request to crawl page '''


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


config = configparser.ConfigParser()
logger.debug('Reading configuration file={}...'.format(CFG_PATH))
config.read(CFG_PATH)
''' Configuration object '''


################################
# Main
################################
def update_ignored_cids(ignored_cid_set, ignored_cids_fp=IGNORED_CIDS_FILE):
    r'''
    Stored ignored cid set into file system

    :param ignored_cid_set: set object to hold ignored cid
    :param ignored_cids_fp: File path to keep those ignored cid set
    '''
    if len(ignored_cid_set) > 0:
        ignored_cid_list = sorted(ignored_cid_set)
        with open(ignored_cids_fp, 'w') as fw:
            for cid in ignored_cid_list:
                fw.write('{}\n'.format(cid))

        logger.info('Total {:,d} cid being added into ignored cid set!'.format(len(ignored_cid_list)))


def load_ignored_cids(ignored_cids_fp=IGNORED_CIDS_FILE):
    r'''
    Loading back ignored cid set from file system

    :param ignored_cids_fp: File path to load back ignored cid set
    '''
    ignored_cid_set = set()
    if os.path.isfile(ignored_cids_fp):
        with open(ignored_cids_fp, 'r') as fh:
            for line in fh:
                line = line.strip()
                if line:
                    ignored_cid_set.add(line)

        logger.debug('{:,d} ignored cid being loaded...({})'.format(len(ignored_cid_set), ignored_cid_set))
    else:
        logger.debug('File={} does not exist!'.format(IGNORED_CIDS_FILE))

    return ignored_cid_set


def create_git_issue(failed_list):
    r'''
    Create Git issue to notify people into handle the broken policy
    '''
    global CFG_SECT
    global config
    date_msg = datetime.now().strftime('%Y/%m/%d')
    pnum = len(failed_list)
    git_base_url = config[CFG_SECT]['git_base_url'].strip()
    git_token = config[CFG_SECT]['git_token'].strip()
    if git_token.startswith('<') and git_token.endswith('>'):
        git_token = os.environ.get(git_token[1:-1], '')

    git_repo = config[CFG_SECT]['git_repo'].strip()
    git_assignees = list(filter(lambda e: e, map(lambda e: e.strip(), config[CFG_SECT]['git_assignees'].split(','))))
    git_labels = list(filter(lambda e: e, map(lambda e: e.strip(), config[CFG_SECT]['git_labels'].split(','))))
    logger.debug('Create issue in repo={} to {} with label={}...'.format(git_repo, git_assignees, git_labels))

    try:
        ghub = Github(base_url=git_base_url, login_or_token=git_token)
        repo = ghub.get_repo(git_repo)

        assignees = []
        for usr_name in git_assignees:
            assignees.append(ghub.get_user(usr_name))

        labels = []
        for label_name in git_labels:
            labels.append(repo.get_label(label_name))

        failure_msg = ''
        for rd in failed_list:
            failure_msg += "* **{}:{}**: {}\n".format(rd[0], rd[1], rd[5])

        ititle = '[BP] Broken policy found on {} ({})'.format(date_msg, len(failed_list))
        ibody = 'Below {pnum} policies are found to be broken:\n{failure_msg}'.format(pnum=pnum, failure_msg=failure_msg)
        repo.create_issue(ititle, ibody, assignees=assignees, labels=labels)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        except_msg = '{}: {}'.format(exc_type, exc_value)
        send_mail('Fail in creating github issue on {}'.format(date_msg), except_msg)
        logger.exception('Fail in creating github issue on {}'.format(date_msg, except_msg))


def send_mail(subject, body):
    r'''
    Sending notification mail to alert maintainer into handle broken policy or service

    :param subject: Mail subject
    :param body: Mail body

    :return:
        True means the mail is sent successfully; False otherwise.
    '''
    global CFG_SECT
    global config
    global EP_SENDER
    global EP_PASSWD
    global EP_SMTP
    if not EP_SENDER or not EP_PASSWD or not EP_SMTP:
        logger.error('Mail setting is not ready!')
        return False

    logger.debug('Config sections: {}'.format(config.sections()))
    receivers = config[CFG_SECT]['mail_to']
    to_emails = list(map(lambda e: e.strip(), receivers.split(',')))
    logger.debug('Mail to {}'.format(to_emails))

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = EP_SENDER
    msg['To'] = ','.join(to_emails)

    part = MIMEText(body.encode('utf-8'), 'html', 'utf-8')
    msg.attach(part)

    smtp = smtplib.SMTP(EP_SMTP)
    smtp.ehlo()
    smtp.starttls()
    status_code, log = smtp.login(EP_SENDER, EP_PASSWD)

    if status_code != 235:
        logger.error('Fail to login SMTP server! ({}, {})'.format(str(status_code), log))
        return False

    logger.debug("Message:\n{}\n\n".format(msg.as_string()))
    smtp.sendmail(msg['From'], to_emails, msg.as_string())
    logger.info('Notification mail sent at {}!'.format(datetime.now()))
    return True


def eval_policy(desired_policy, reason):
    r'''
    Evaluate reason to confirm the handler is from desired policy
    '''
    # purifier.policy.policy24 (policy_symantec04_2/online:r:<URL pattern>
    # {'reason': ('purifier.policy.policy24', 'policy_symantec04_2', 'online', '<url patterns>')}
    source = reason['reason']
    if type(source) in [list, tuple]:
        source = list(source)
        for i in range(0 if len(source) == 4 else 4 - len(source)):
            source.append(None)

        modu_name, policy_name, template_name, url_ptn = source
        modu_name = modu_name.split('.')[-1]
    else:
        logger.warning('Unknown source={}!'.format(source))
        modu_name = policy_name = template_name = None

    # mth = re.match(r'purifier\.policy\.(.+?) \((.+?)/(.+?):(.*)\)', reason)
    if modu_name:
        actua_tup = list(map(lambda e: e.strip() if e else '', [modu_name, policy_name, template_name]))
        logger.info('Module name={}; Policy name={}; Template name={}'.format(modu_name, policy_name, template_name))
        logger.debug('actua_tup={}'.format(actua_tup))
        check_tup = list(map(lambda e: e.strip(), desired_policy.split('.')))
        logger.debug('check_tup={}'.format(check_tup))
        return check_tup == actua_tup[:len(check_tup)]
    else:
        logger.warning('Unknown reason={}'.format(reason))
        return False


def parse_args():
    parser = argparse.ArgumentParser(
        usage='''
        $ python tools/eval_policy.py tools/policy_eval.csv

        You can modify `tools/eval_policy.ini to modify the mail list`.
        In order to enable the mail notification, you have to export below three environmental variables:
        * EP_SENDER=<Email address>
        * EP_PASSWD=<Password of your mail account>
        * EP_SMTP=<SMTP server: e.g.: 'smtp.gmail.com:587'>

        ''',
        description='Toolkit to evaluate the validity of policy'
    )
    parser.add_argument('--config_csv', type=str, default=os.path.abspath(os.path.join(MODU_PATH, 'policy_eval.csv')),
                        help='Configuration as CSV with columns as URL,expected policy name and desire content to check (default:%(default)s)')
    parser.add_argument('--dryrun', action='store_true', help='Launch dry run without evaluation')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Launch evaluation without further action (e.g.: disable evaluation if failed)')
    parser.add_argument('--enable_git', action='store_true', default=False, help='Enable auto creating git issue (default:%(default)s)')
    parser.add_argument('--config_sec', type=str, default=CFG_SECT, help='Section of configuration to apply. (default:%(default)s)')
    parser.add_argument('--enable_mail', action='store_true', help='Sending notification mail')
    parser.add_argument('--day', type=str, default=None, help='Setup daily job with format as HH:MM:SS/HH:MM')
    parser.add_argument('--cids', type=str, metavar='cids', nargs='+', default=[], help='Only work on policy id given here')
    parser.add_argument('--exclude_cids', type=str, metavar='ecids', nargs='+', default=[], help='Exclude the policy id given here')
    parser.add_argument('--monday', type=str, default=None, help='Setup weekly job on Monday with format as HH:MM:SS/HH:MM')
    parser.add_argument('--tuesday', type=str, default=None, help='Setup weekly job on Tuesday with format as HH:MM:SS/HH:MM')
    parser.add_argument('--wednesday', type=str, default=None, help='Setup weekly job on Wednesday with format as HH:MM:SS/HH:MM')
    parser.add_argument('--thursday', type=str, default=None, help='Setup weekly job on Thursday with format as HH:MM:SS/HH:MM')
    parser.add_argument('--friday', type=str, default=None, help='Setup weekly job on Friday with format as HH:MM:SS/HH:MM')
    parser.add_argument('--saturday', type=str, default=None, help='Setup weekly job on Saturday with format as HH:MM:SS/HH:MM')
    parser.add_argument('--sunday', type=str, default=None, help='Setup weekly job on Sunday with format as HH:MM:SS/HH:MM')

    return parser.parse_args()


def work(csv_df, dryrun, enable_mail, ignored_cid_set, enable_git, debug=False):
    global CID_LIST
    global ECID_SET
    today = datetime.now()
    exit_code = 0
    eval_rst = []
    tea = TEAgent()
    _st = datetime.now()
    pc = 0
    for ri, row in csv_df.iterrows():
        url = row['url'].strip()
        cid = str(row['cid']).strip()

        if CID_LIST and cid not in CID_LIST:
            logger.debug('Skip cid={}...'.format(cid))
            continue

        if ECID_SET and cid in ECID_SET:
            logger.debug('Skip cid={}...'.format(cid))
            continue

        if cid in ignored_cid_set:
            logger.debug('Skip cid={} by ignored set...'.format(cid))
            continue

        if cid.startswith('#'):
            logger.warn('Skip cid={}...({})'.format(cid, url))
            continue

        pc += 1
        desired_policy_name = row['policy']
        text2eval = list(map(lambda e: e.strip(), str(row['dtext']).split('|')))
        logger.info('{}: Evaluate URL={} with desired policy={}'.format(cid, url, desired_policy_name))
        if dryrun:
            eval_rst.append((cid, url, 200, True, 'Dryrun'))
        else:
            try:
                resp = requests.get(url, headers=REQUEST_HEADERS)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                eval_rst.append((cid, url, -1, None, False, '{}: {}'.format(exc_type, exc_value)))
                logger.exception('Fail to crawl URL={}'.format(url))
                ignored_cid_set.add(cid)
                continue

            sc = resp.status_code
            content = resp.text
            if sc not in [200, 202]:
                eval_rst.append((cid, url, sc, content, False, 'Status code is not 2xx!'))
                ignored_cid_set.add(cid)
                continue

            mime = resp.headers['content-type'] if 'content-type' in resp.headers else '\n'.join(resp.headers)
            is_suc, rst, reason = tea.parse(mime, url, content)
            text = rst['text']
            if is_suc:
                # debug code
                # with open('{}.txt'.format(cid), 'w') as fw:
                #    fw.write(text)

                eval_log = ''
                # Check if the URL is parsed by desired policy
                if eval_policy(desired_policy_name, reason):
                    logger.info('\tEvaluation on policy name...passed!')
                else:
                    logger.warn('\tEvaluation on policy name...failed! ({} not in {})'.format(desired_policy_name, reason))
                    eval_log += 'Fail in evaluation on policy name: {}\n'.format(reason)
                    ignored_cid_set.add(cid)

                # Check if the CTE contains wanted message(s)
                miss_txt_list = []
                for dt in text2eval:
                    if not dt:
                        continue

                    if dt not in text:
                        miss_txt_list.append(dt)

                if miss_txt_list:
                    logger.warn('\tEvaluation on CTE ({:,d})...failed! ({})'.format(len(text2eval), miss_txt_list))
                    eval_log += 'Fail in evaluation on CTE with missing text: {}\n'.format('\n'.join(miss_txt_list))
                    ignored_cid_set.add(cid)
                else:
                    logger.info('\tEvaluation on CTE ({:,d})...passed!'.format(len(text2eval)))

                eval_rst.append((cid, url, sc, content, True if len(eval_log) == 0 else False, eval_log))
            else:
                eval_rst.append((cid, url, sc, content, False, 'Fail in CTE({}) with reason={}'.format(desired_policy_name, reason)))
                logger.warn('\tEvaluation on policy id={}...failed!'.format(cid))
                ignored_cid_set.add(cid)

    tdiff = datetime.now() - _st
    logger.info('All done! ({:,d}, {})'.format(pc, tdiff))

    if debug:
        logger.info('Short quit from debug mode!\n')
        return

    # 2) Synchronized result
    # with open('eval_rst_{}.pkl'.format(today.strftime("%y%m%d%H%M%S")), 'wb') as fw:
    #    pickle.dump(eval_rst, fw)

    mail_subject = ''
    mail_body = "<font size='6' color='green'><b>All done!</b> ({:,d}, {})</font>".format(pc, tdiff)
    failed_list = list(filter(lambda t: not t[4], eval_rst))
    if failed_list:
        if enable_git:
            create_git_issue(failed_list)

        update_ignored_cids(ignored_cid_set)
        mail_subject = "[Fail] w4cs-text-purifier monitoring result ({})".format(today.strftime("%m/%d/%Y, %H:%M:%S"))
        mail_body = '<b><font size="6" color="red">List of failed record({:,d}):</font></b>\n'.format(len(failed_list))
        mail_body += '<ul>'
        for rd in failed_list:
            mail_body += "\t<li><font size='5'><b>{}:{}</b>: {}</font></li>\n".format(rd[0], rd[1], rd[5])

        mail_body += '</ul>'

        mail_body += '<br/>'
        if len(ignored_cid_set) > 0:
            mail_body = '<b><font size="6" color="darkgray">List of ignored cid({:,d}):</font></b>\n'.format(len(ignored_cid_set))
            mail_body += '<ul>'
            for cid in sorted(ignored_cid_set):
                mail_body += "\t<li><font size='5'><b>{}</b></font></li>\n".format(cid)

            mail_body += '</ul>'

        logger.debug("Mail body:\n{}\n\n".format(mail_body))
        exit_code = 1
    else:
        if len(ignored_cid_set) > 0:
            mail_subject = "[Warn] w4cs-text-purifier monitoring result ({})".format(today.strftime("%m/%d/%Y, %H:%M:%S"))
            mail_body = '<b><font size="6" color="darkgray">List of ignored cid({:,d}):</font></b>\n'.format(len(ignored_cid_set))
            mail_body += '<ul>'
            for cid in sorted(ignored_cid_set):
                mail_body += "\t<li><font size='5'><b>{}</b></font></li>\n".format(cid)

            mail_body += '</ul>'
        else:
            mail_subject = "[Pass] w4cs-text-purifier monitoring result ({})".format(today.strftime("%m/%d/%Y, %H:%M:%S"))

    # 3) Send notification mail
    if enable_mail:
        if not send_mail(mail_subject, mail_body):
            logger.warn('Fail to send notification mail!')
            exit_code = 1
    else:
        logger.warning('Notification mail is disabled!')

    return exit_code


def main():
    global CFG_SECT
    global CID_LIST
    global ECID_SET
    args = parse_args()
    debug = args.debug
    CFG_SECT = args.config_sec
    if args.cids:
        CID_LIST = args.cids
        logger.debug('Running evaluation on cid list={}...'.format(args.cids))

    if args.exclude_cids:
        for cid in args.exclude_cids:
            logger.debug('Exclude cid={}...'.format(cid))
            ECID_SET.add(cid)

    config_path = args.config_csv
    if not os.path.isfile(config_path):
        logger.error('The configuration={} does not exist!'.format(config_path))
        sys.exit(1)

    # 0) Loading evaluation data and ignored cid set
    logger.debug('Loading setting from {}...'.format(config_path))
    df = pd.read_csv(config_path, skiprows=1, names=['cid', 'url', 'policy', 'dtext'])
    ignored_cid_set = load_ignored_cids()

    # 1) Setup scheduler if any
    if args.day:
        schedule.every().day.at(args.day).do(work, csv_df=df, dryrun=args.dryrun, enable_mail=args.enable_mail, ignored_cid_set=ignored_cid_set, enable_git=args.enable_git)
    elif args.monday:
        schedule.every(1).week.monday.at(args.monday).do(work, csv_df=df, dryrun=args.dryrun, enable_mail=args.enable_mail, ignored_cid_set=ignored_cid_set, enable_git=args.enable_git)
    elif args.thursday:
        schedule.every(1).week.thursday.at(args.thursday).do(work, csv_df=df, dryrun=args.dryrun, enable_mail=args.enable_mail, ignored_cid_set=ignored_cid_set, enable_git=args.enable_git)
    elif args.tuesday:
        schedule.every(1).week.tuesday.at(args.tuesday).do(work, csv_df=df, dryrun=args.dryrun, enable_mail=args.enable_mail, ignored_cid_set=ignored_cid_set, enable_git=args.enable_git)
    elif args.wednesday:
        schedule.every(1).week.wednesday.at(args.wednesday).do(work, csv_df=df, dryrun=args.dryrun, enable_mail=args.enable_mail, ignored_cid_set=ignored_cid_set, enable_git=args.enable_git)
    elif args.friday:
        schedule.every(1).week.friday.at(args.friday).do(work, csv_df=df, dryrun=args.dryrun, enable_mail=args.enable_mail, ignored_cid_set=ignored_cid_set, enable_git=args.enable_git)
    elif args.saturday:
        schedule.every(1).week.saturday.at(args.saturday).do(work, csv_df=df, dryrun=args.dryrun, enable_mail=args.enable_mail, ignored_cid_set=ignored_cid_set, enable_git=args.enable_git)
    elif args.sunday:
        schedule.every(1).week.sunday.at(args.sunday).do(work, csv_df=df, dryrun=args.dryrun, enable_mail=args.enable_mail, ignored_cid_set=ignored_cid_set, enable_git=args.enable_git)

    # 2) Start evaluation process
    if schedule.default_scheduler.jobs:
        logger.info('Launch schedule with {:,d} jobs...'.format(len(schedule.default_scheduler.jobs)))
        while schedule.default_scheduler.jobs:
            schedule.run_pending()
            if schedule.default_scheduler.jobs[0].last_run:
                logger.info('Job done and next run will be {}!'.format(schedule.default_scheduler.jobs[0].next_run))
                schedule.default_scheduler.jobs[0].last_run = None

            time.sleep(1)
    else:
        work(df, args.dryrun, args.enable_mail, ignored_cid_set, enable_git=args.enable_git, debug=debug)


if __name__ == '__main__':
    main()
