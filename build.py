from urllib.request import urlopen
from optparse import OptionParser

import shutil
import gzip
import lzma
import csv
import io
import re
import os

RE_VALID_WORD = re.compile('^[ぁ-んァ-ヶー一-龠a-zA-Zａ-ｚＡ-Ｚ・！？\s　]+$')
RE_INVALID_SHORT_WORD = re.compile('^([0-9０-９]+|[^一-龠]{1,2}|[ぁ-んー]{1,3})$')
RE_ALPHANUMERIC_TOKEN = re.compile('^[A-Za-z0-9]+$')
RE_HIRA_KATA_TOKEN = re.compile('^[ぁ-んァ-ヶー]+$')
RE_KANJI_TOKEN = re.compile('^[一-龠]+$')
RE_WHITESPACES = re.compile('\s+')


def get_latest_release_date():
    re_path_mecab = re.compile('seed/mecab-user-dict-seed.([0-9]+).csv.xz')
    url_changelog = 'https://raw.githubusercontent.com/neologd/mecab-ipadic-neologd/master/ChangeLog'
    data = urlopen(url_changelog)
    for line in data:
        m = re_path_mecab.search(line.decode('utf-8'))
        if m is not None:
            return m.group(1)
    raise Exception('Failed to read NEologd changelog: ' + url_changelog)


def download_mecab_user_dict(version, path):
    with open(path, 'wb') as f:
        url_mecab = 'https://github.com/neologd/mecab-ipadic-neologd/raw/master/seed/mecab-user-dict-seed.{}.csv.xz'.format(version)
        f.write(urlopen(url_mecab).read())


def main():
    parser = OptionParser()
    parser.add_option('-d', '--path_dest', default=os.path.join(os.path.dirname(__file__)))
    parser.add_option('-v', '--version', default=get_latest_release_date())
    opts, args = parser.parse_args()

    print('Reading NEologd custom dictionary for MeCab (published on %s)' % opts.version)
    filename_mecab = 'mecab-user-dict-neologd.csv.xz'
    path_mecab = os.path.join(opts.path_dest, filename_mecab)
    download_mecab_user_dict(opts.version, path_mecab)
    src = lzma.open(path_mecab)
    reader = csv.reader(io.TextIOWrapper(src, newline=''))
    os.remove(path_mecab)

    print('Converting into Lucene user dictionary format')
    filename_userdict = 'lucene-ja-userdict-neologd.csv'
    path_userdict = os.path.join(opts.path_dest, filename_userdict)
    dst = open(path_userdict, 'w', newline='')
    writer = csv.writer(dst)

    print('-> Finding candidate words')
    candidates = dict()
    for line in reader:
        if line[4] != '名詞':
            continue

        word = line[0].strip().lower()

        # filter out meaningless words
        if len(word) < 2 or \
           (len(word) == 2 and not RE_KANJI_TOKEN.match(word)) or \
           (len(word) < 4 and RE_HIRA_KATA_TOKEN.match(word)) or \
           RE_INVALID_SHORT_WORD.match(word) or \
           not RE_VALID_WORD.match(word) or \
           RE_ALPHANUMERIC_TOKEN.match(word):
            continue

        tag = '-'.join(line[4:7]).replace('-*', '')
        if word not in candidates:
            candidates[word] = [tag]
        else:
            candidates[word].append(tag)

    print('-> Filtering and writing to file')

    # load pre-defined stoptags
    with open(os.path.join(os.path.dirname(__file__), 'resources', 'stoptag.txt')) as f:
        stoptags = set(map(lambda l: l.rstrip(), f.readlines()))

        # talent name is not included because it is 人名-一般
        stoptags.add('名詞-固有名詞-人名-姓')
        stoptags.add('名詞-固有名詞-人名-名')

        stoptags.add('名詞-固有名詞-地域')
        stoptags.add('名詞-固有名詞-地域-一般')
        stoptags.add('名詞-固有名詞-地域-国')

    for word, tags in candidates.items():
        # filtering based on stoptags
        if len([tag for tag in tags if tag in stoptags]) > 0:
            continue

        segmentation = RE_WHITESPACES.sub('-', word)

        # <word>,<segmentation>,<read>,<class>
        # furigana is omitted to reduce file size
        writer.writerow([word, segmentation, None, '名詞'])

    dst.close()
    src.close()

    print('Compressing')
    with open(path_userdict, 'rb') as raw:
        with gzip.open(path_userdict + '.gz', 'wb') as compressed:
            shutil.copyfileobj(raw, compressed)
    os.remove(path_userdict)


if __name__ == '__main__':
    main()
