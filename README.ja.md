
# Pausable Unittest

[![Build Status](https://travis-ci.org/masamitsu-murase/pausable_unittest.svg?branch=master)](https://travis-ci.org/masamitsu-murase/pausable_unittest)
[![Build status](https://ci.appveyor.com/api/projects/status/5n4gt33gmd9clo0m/branch/master?svg=true)](https://ci.appveyor.com/project/masamitsu-murase/pausable-unittest/branch/master)

## 概要

Pausable Unittest ライブラリでは、 Python の標準ライブラリ [unittest](http://docs.python.jp/2/library/unittest.html) を拡張し、以下のことができる。

* テストの途中に再起動などの Power Cycle をまたぐ
* テストの実行を途中で中断する
* システムの再起動後にそのテストを継続する

このライブラリの実行には、 Stackless Python もしくは PyPy が必要である。

EFI Shell 版の Stackless Python のバイナリは、私の [GitHub のページ](https://github.com/masamitsu-murase/edk2_for_mruby/blob/stackless_python279_release/StacklessPython279.efi?raw=true) からダウンロードすることができる。

## サンプル

### EFI Shell 上で、再起動に要する時間を測定する

EFI 起動できる PC 上であれば、下記のようなスクリプトで再起動に要する時間を測定することができる。

```python
# sample_efi.py

import pausable_unittest
import pausable_unittest.efipauser

import time

class Sample(pausable_unittest.TestCase):
    def test_reboot(self):
        reboot_time = []                        # (*1)
        for i in range(3):
            print("Reboot %d..." % i)
            time.sleep(3)

            start = time.time()
            # Reboot the system.
            self.reboot()                       # (*2)
            end = time.time()

            reboot_time.append(end - start)     # (*3)

        avg_time = sum(reboot_time) / len(reboot_time)
        self.assertLess(avg_time, 8)            # (*4)

if __name__ == "__main__":
    pausable_unittest.main(pausable_unittest.efipauser.Pauser())
```

上記のスクリプトを EFI Shell 上で下記のように実行する。

```shell
> StacklessPython279.efi sample_efi.py
```


このサンプルは、 PC を 3回再起動し、その時間を測定する。

* `reboot_time` リストは、 (\*1) で初期化される。
* PC は (\*2) で再起動される。  
  Stackless Python インタプリタが中断され、 `reboot_time` や `start` などのすべての変数は保存される。  
  その後、 PC が再起動される。
* 再起動後、 Stackless Python インタプリタが再開される。すべての変数が復旧される。  
  測定された時間は、 (\*3) で `reboot_time` に追加される。  
  `reboot_time` や `start` 変数は、再起動前に作られているが、特別な処理をすることなく読み書きできる。
* 標準ライブラリの unittest と同様に、 (\*4) では `assertLess` で結果をチェックできる。

VirtualBox 上での挙動を [YouTube の動画](https://youtu.be/gb7-UKnkjrM) で見ることができる。


## 使い方

### テストケースの記述方法

標準ライブラリの [unittest](http://docs.python.jp/2/library/unittest.html) と同じように、 Pausable Unittest ライブラリの `TestCase` クラスを継承してテストケースを記述する。

```python
class Sample(pausable_unittest.TestCase):
    def test_reboot(self):
        start = time.time()
        self.reboot()
        end = time.time()
        self.assertLess(end - start, 5)

```

#### unittest の `TestCase` との違い

Pausable Unittest の `TestCase` は、標準ライブラリの unittest の `TestCase` に加えて、 Python インタプリタ中断用のメソッドを持っている。  
上の例の場合は `self.reboot()` がそのメソッドである。

この Python インタプリタ中断用のメソッドは、テスト実行時に指定する `Pauser` クラスによって追加されている。

### テストケースの実行方法

作成した `TestCase` を実行するには、 Pauser Unittest が提供している `TestRunner` の `run` メソッドを呼ぶことで実行する。  
`run` メソッドに渡す `TestSuite` インスタンスは、標準ライブラリの unittest と同様の方法で作成する。  
`run` メソッドには、もう一つ Python インタプリタ中断用のメソッドを提供する `Pauser` クラスのインスタンスを渡す。

```python
suite = unittest.TestLoader().loadTestsFromTestCase(SampleTest)
pausable_unittest.TestRunner().run(suite, efipauser.Pauser())
```

`Pauser` としては Windows 向けの `windowspauser` と EFI Shell 向けの `efipauser` が実装されている。  
これをベースに、各種環境向けの `Pauser` を実装することができる。


## ライセンス

MIT License に基づく。

[English README](https://github.com/masamitsu-murase/pausable_unittest/blob/master/README.md#license) を参照すること。

## 内部実装仕様の詳細

標準ライブラリの [unittest](http://docs.python.jp/2/library/unittest.html) と同じように、 Pausable Unittest も `TestCase`, `TestRunner` などを提供している。  
その他にも `Pauser` や `PicklableLogger` など、同時に使うべきクラスを提供している。

ここでは、これらのクラスの実装仕様や使い方についてまとめる。

### 各クラスの関係

Pausable Unittest の「テストを途中で中断できる」動作は、 `Pauser`, `TestRunner`, `TestCase` が主要な処理を担っている。

`TestCase` を継承して記述されたテストケースは、 `TestRunner` によって、実行される。  
このとき、メインとは異なる `tasklet` でテストケースが実行される。 PyPy の場合は、メインとは異なる `continulet` で実行される。  
`Pauser` クラスは、 `TestCase` クラスにいくつかの「テスト中断用メソッド」を追加する。  
テストケースのメソッドで、テストを中断したくなった場合は、 `Pauser` によって追加されたメソッドを呼ぶ。  
`Pauser` の中断用メソッドを呼ぶと、実行中の `tasklet` を中断する。

まとめると以下のようになる。

* ユーザーは `TestCase` を継承して、自身のテストケースを記述する。
* `TestCase` は `TestRunner` によって実行される。  
  `TestSuite` は unittest ライブラリのものを用いる。
* `Pauser` は `TestCase` に Python インタプリタを中断するためのメソッドを追加する。  
  `Pauser` は中断用のメソッドを `TestCase` のインスタンスメソッドとして追加する。


以下、各クラスについて詳細を述べる。

### TestCase

テストを記述するユーザーは、このクラスを継承し、自身のテストケースを書くことができる。

```
class SampleTest(pausable_unittest.TestCase):
    def test_sample1(self):
        # ...
```

このクラスは unittest の `TestCase` を継承しており、 `TestCase` で提供されているすべてのメソッドを使うことができる。  
例えば、 `assertEqual` などのメソッドは同じように呼び出すことができる。  
`setUp`, `tearDown` メソッドの働きも同じである。

unittest の `TestCase` との違いは、「`Pauser` が追加したメソッドを呼び出せるか」である。  

(T.B.D.)

### Pauser

(T.B.D.)

### TestRunner

(T.B.D.)

### PicklableLogger

(T.B.D.)

