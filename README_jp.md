# Maya PivotPainter  

目次
-----------------

  * [Description](#description)  
  * [Requirement](#requirement)  
  * [Infomation about Python Script](#infomation-about-python-script)  
  * [Install](#install)  
  * [Usage](#usage)  
  * [License](#license)  
  * [Author](#author)  

Description  
------------  
## 解説
このツールはUnrealEngine4にあるMax版PivotPainter1のMaya版です。  

![ri_maya_pivot_painter_v4 2](https://user-images.githubusercontent.com/29208747/46820973-8431b600-cdc2-11e8-81a9-49f264f77a0b.PNG)

Requirement  
------------  
## 必要条件
 Maya 2016 以上  


Infomation about Python Script
------------
## スクリプトについて
Maxのスクリプト部分は出来る限り元を真似て作成しており、オリジナルのツールが何をしているのか  
分るようにしています。その為、最適化はあえて最小限にとどめています。  
残りの部分は OpenMaya を使い、特にベクターを計算する部分は、buildMatrix や buildRotation の  
知識を使わせて頂いています。  


Install  
------------  
## インストール

1,  
ri_maya_pivot_painter.py をMayaのスクリプトエディターにドラッグ＆ドロップし、最後の行に  
```py
 "maya_pivot_painter_menu()"   
```
を追加、全てを選択して、Maya のシェルフボタンをPythonの種類で作成します。  

あるいは  

2,  
Maya のパスが通ったディレクトリーに ri_maya_pivot_painter.py をコピーし、  
```py
"maya_pivot_painter_menu()"  
```
を用いて起動します。  


Usage  
------------  
## 使い方

### Setup Polygon Tools
 * [Detach Selected Polygon (Separate)]  
> 1つにまとめられたポリゴンを、その UV Shell の情報に基づいて個々のポリゴンに分割します。  
> FBXの草のデータを入力する時に便利です。  

 * [Rotate Pivot]  
> Pivot をその場でグルグル回転させます。  
> Xアップに変換したり、Ｙアップに戻したりするのに便利です。  
> 回転軸値に値が入っていた場合はそれをゼロにリセットし、回転値に変換します。  


 * [Show On/Off Vertex Color]  
> 頂点色データがポリゴンに存在する場合に、頂点色の表示/非表示をトグルします。  

 * [Paint Black VertexColor (NoAnimation)]  
> 頂点色として黒色を設定し、PivotPointのマテリアルアニメーションに置いてアニメーションなしを設定します。  
> 木の幹を設定する時に便利です。  


### Per Polygon PivotPainter
 * [Make X-Up Pivot for Grass]  
> このツールは自動的に草ポリゴンの最低点にＸアップのベクターを設定します。  
> 最低のポリゴン面を検出して設定しています。  

 * [] Optimize for Foliage Placement (No VectorColor)  
> チェックが入っている時、頂点色を設定しません。  

  ... 各値の説明はMax版を参照 ...  


 * [Do!! Per Polygon PivotPaiter]  
> PivotPaiterを個々に分割したポリゴン郡に対して実行します。  
> MayaのデフォルトのUVset名である"map1"は"UVChannel_1"に改名されます。  
> このツールを使う時、UVset名に留意してください。  



### Hierachy PivotPainter
 *   + Minimum Side - Maximum Side  
 * [Make X-Up Pivot for Branch (Use when Y-up)]  
> このツールは自動的に枝ポリゴンの最低面側か最高面側にXアップのPivotを設定します。  
> このツールはYアップの状態で実行するツールなので、もしそうでない場合は  
> 上記 [Rotate Pivot] ツールを使ってYアップにしておいてから実行します。  

 * [_] Optimize for Foliage Placement (No VectorColor)  
> チェックが入っている時、頂点色を設定しません。  


 * Set A Parent [______]  [SetParent]  
> 親に設定するポリゴンを選択状態にして `[SetParent]` ボタンを押して親として登録します。  

 * SetAllChild  
> `[Set]`  `[Add]`  `[DeleteSelected]`  `[Clear All]`   

> 子に設定するポリゴン群を選択状態にして `[Set]` ボタンを押すと、その下のリストに登録されます。  
> `[Add]` は選択してポリゴン群をリストに追加登録し、  
> `[DeleteSelected]` はリストの選択したポリゴン名をリストから削除し、  
> `[Clear All]`  はリストを空にします。  

 * [Do!! Hierachy PivotPaiter]  
> PivotPaiterをリストに登録されたポリゴン郡に対して実行します。  
> MayaのデフォルトのUVset名である"map1"は"UVChannel_1"に改名されます。  
> このツールを使う時、UVset名に留意してください。  


Licence  
------------  
## ライセンス
[MIT] (https://github.com/O-Ritaro/Maya_PivotPainter/blob/master/LICENSE)

Author  
------------  
## 記載者
Ritaro (https://github.com/O-Ritaro)