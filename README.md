Apache Lucene Japanese User-Defined Dictionary with NEologd
===

Our Python script enables you to utilize [NEologd](https://github.com/neologd/mecab-ipadic-neologd), a neologism dictionary for [the MeCab morphological analyzer](http://taku910.github.io/mecab/), to enhance Japanese tokenization of Apache Lucene.

Since [Lucene's custom dictionary](https://lucene.apache.org/core/7_4_0/analyzers-kuromoji/index.html) does not allow us to specify word score which is necessary to make more accurate tokenization, the script aggressively filters out less important words from original NEologd (e.g., non-noun words, short word which might be tokenizable even by the standard tokenizer).

Note that tokenizer implemented in Lucene is based on [Kuromoji](http://www.atilika.org/), and the latest version of Kuromoji already supports custom dictionary format with word scores: [atilika/kuromoji#91](https://github.com/atilika/kuromoji/pull/91). However, unfortunately Lucene does not include the update at this moment.

## Usage

Following command downloads the latest version of NEologd and converts it into Lucene user-defined dictionary format:

```sh
$ python build.py
```

Eventually, `lucene-ja-userdict-neologd.csv.gz` is created. The CSV file contains custom rules for better Japanese tokenization as:

```
ten create,ten-create,,名詞
ハインリヒ・ベル,ハインリヒ・ベル,,名詞
佐竹笙悟,佐竹笙悟,,名詞
小貝澤,小貝澤,,名詞
神田達成,神田達成,,名詞
西村ツチカ,西村ツチカ,,名詞
愛と涙の蔵出し物語,愛と涙の蔵出し物語,,名詞
ヨンマンキュウセンヒャクエン,ヨンマンキュウセンヒャクエン,,名詞
mfブックス,mfブックス,,名詞
ハイイロガン,ハイイロガン,,名詞
...
```