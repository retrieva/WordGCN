# 環境設定
- 前提：GPUを使用できること
- 確認
```
$ lspci | grep -i nvidia
```

## docker
1. dockerをインストール
2. nvidia-dockerをインストール
3. nvidia-dockerがインストールできているか確認
```
$ docker run --runtime=nvidia --rm nvidia/cuda nvidia-smi
```

4.  tensorflowの実行を確認
```
$ docker run --gpus all --runtime=nvidia -it --rm tensorflow/tensorflow:1.13.1-gpu-py3 \
       python -c "import tensorflow as tf; tf.enable_eager_execution(); print(tf.reduce_sum(tf.random_normal([1000, 1000])))" 
```

5. セッション開始
```
$ docker run --gpus all --runtime=nvidia --volume /path/to/this/repository:/path/in/docker -it tensorflow/tensorflow:1.13.1-gpu-py3 bash
```

6. 必要ライブラリのインストール
```
# cd /path/to/this/repository/in/docker
# pip install -r requirements-tfdocker.txt
```

# データの用意
## SynGCN
本家のREADMEにあるように以下のファイルが必要です。
* `voc2id.txt` 単語-idのファイル。単語を１列目、idを２列目としてタブ区切り
  - 例
```
serapion        132018
ab-soul 134274
312th   121873
buren   19100
```
* `id2freq.txt` idの頻度。idを1列目、頻度を2列名としてタブ区切り
 - 例
 ```
48073   635
121883  147
121769  148
 ```
* `de2id.txt` 係り受けのedgeのラベルとidのファイル。ラベルを1列目、idを２列目とする
  - 例
```
csubjpass       20
acl:relcl       9
xcomp   36
acl     13
```
* `data.txt` 原文をid列と係り受け列にしたファイル。先頭に、1文のtoken数と係り受けの数が必要
  - フォーマット

```java
    <num_words> <num_dep_rels> tok1 tok2 tok3 ... tokn dep_e1 dep_e2 .... dep_em
```

  - 例
```
15 14 24351 24351 10 7 436 2083 26 8385 121958 4986 215 13 6932 2293 2 1|0|26 5|1|11 5|2|23 5|3|34 5|4|7 7|6|11 5|7|9 9|8|7 7|9|38 9|10|13 13|11|2 13|12|7 10|13|16 5|14|10
25 24 90 29 272 494 15 41788 4986 3 301 131 3137 49 2135 142 66 2257 15 2293 215 13 120543 39 539 5204 2 3|0|3 3|1|21 3|2|15 6|4|2 6|5|7 3|6|16 3|7|10 12|8|0 10|9|7 12|10|11 12|11|27 3|12|17 12|13|38 15|14|15 17|15|15 17|16|2 12|17|16 17|18|13 20|19|2 18|20|16 20|21|33 20|22|19 20|23|5 3|24|10
```

### 作成方法
#### 依存ライブラリ
- spacy
- ginza
- MeCab

#### 手順
1. 以下のコマンドで、対象コーパス単語-頻度ペアのtxtファイルを作成(以下voc2freq.txtと呼ぶ)
- コーパスがtxtの場合
```
$ python make_voc2freq.py -i /path/to/corpus/dir -o /path/to/voc2freq.txt -t <tokenizer name> --maxlen <max token number in a sentence>
```

- コーパスがjsonlの場合
```
$ python make_voc2freq.py -i /path/to/corpus/dir -o /path/to/voc2freq.txt -t <tokenizer name> --format jsonl --text_fields <text field name at jsonl> --max_len <max token number in a sentence>
```

- 注意
  - 依存構造解析に[ginza](https://megagonlabs.github.io/ginza/)を利用しています。そのため、mecabでtokenizeすると、SynGCNのデータにする際、tokenizeに齟齬が生じて、不完全なデータになる可能性が高くなります。
    - ginzaのtokenizeは[sudachi](https://github.com/WorksApplications/SudachiPy)に依存しているため、mecabと齟齬が生じます。
    - 依存構造解析にginzaを使う理由は、SynGCNはUniversal Dependencyに基づいて、依存構造解析をする必要があるからです。
    - tokenizeはginzaの方が時間がかかります。(それでも、10分程度あれば、wikipedia全体を処理できます。)
  - syngcnを実行する際、ここで設定したmaxlenに揃えてください。最大長が合わず、エラーになります。

2. 以下のコマンドで、`voc2id.txt` と `id2freq.txt` を作成
```
$ python preproc.py -i /path/to/voc2freq.txt -o /path/to/outputdir -s <select_voc_size>
```

3. 以下のコマンドで、コーパスからSynGCNフォーマットのデータを作成
  - コーパスは指定したフォルダ直下の全てのファイルが該当する前提です。
  - 全てのファイルのフォーマットは、平文のtxtファイルまたはjsonlとしてください。

- txtの場合  
```
$ python make_syngcn_data.py -i /path/to/corpus/dir -v /path/to/voc2id.txt -f /path/to/id2freq.txt -o /path/to/outdir
```

- jsonlの場合
```
$ python make_syngcn_data.py -i /path/to/corpus/dir -v /path/to/voc2id.txt -f /path/to/id2freq.txt -o /path/to/outdir --text_field text --json
```


## SemGCN
学習済みのembeddingが必要です。embeddingのフォーマットは、gloveと同じで、単語と数値をスペース区切りとします。
### コーパス系データ
SynGCNで使用した、 `voc2id.txt` と `id2freq.txt` が必要です。
それらのデータがない場合は、学習済embeddingを学習させたコーパスに対して、[手順](#手順)の1,2を実行してください。
### シソーラスデータ
特定のフォルダ(デフォルトは `./semantic_info`)以下に、関係単語ペア毎に、 `関係名.txt`を用意してください。
`関係名.txt`は、スペース区切りで二単語ずつにしてください。(本家は、synonymだけ、なぜか2単語以上になってます。)
- 例　
  - 場所: `./semantic_info/antonyms.txt`
  - フォーマット
```
deciphering encode
accelerate slowing
unite divided
irritate soothe
```

## 評価
英語の場合、[word-embedding-benchmarks](https://github.com/kudkudak/word-embeddings-benchmarks) を使用して、評価を行えます。
こちらをインストールしたのちに、以下の手順で評価を行えます。

### 手順
```
$ evaluate.py -v2d /path/to/voc2id.txt -embed /path/to/embedding_file -embed_dim <dimmension number>
```

### 余談
- sslで失敗するので[こちら](https://shinespark.hatenablog.com/entry/2015/12/06/100000)を参考にした。ややセキュリティー的に怪しいので、心配
- numpyのversionの都合でめっちゃwarningでる。(vstackがdeplicateになるよ。みたいなやつ)
