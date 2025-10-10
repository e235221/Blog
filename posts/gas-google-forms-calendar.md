### 目的
本レポートは，Googleフォームに入力された欠席連絡をトリガーとして，Googleカレンダーに終日の予定として当該欠席情報を自動的に表示させるシステムを構築する目的で実施された一連の作業について記述する。

### 概要
- 背景
	- 従来の欠席連絡が役員のみに来る方式だと管理が大変・入力する側も複数人に送信する必要がある・確認する側も抜け漏れが生じることが発生したため，これを作成した。
- メリット
	部員はいちいち部長・副部長・議長に連絡する手間が減る，確認漏れの防止，役員全員が同じ画面を閲覧できる。部のgoogle  calendarをprivateに追加すると個人のスマホやPCといった環境で閲覧できる。
- デメリット
	- URLがバレたら個人情報流出の可能性。したがって，URLは決して外部（部内）に漏らさないように。

- **使用するもの**
	- ダイビング部用google account
- **使用サービス**
	- Googleフォーム，Googleスプレッドシート，Googleカレンダー，Google Apps Script

### システム概要
本システムは，Googleの各種サービスとDiscordを連携させて動作する。\UTF{00A0}部員がGoogleフォームに情報を入力すると，そのデータがGoogleスプレッドシートに記録され，それをトリガーとしてGoogle Apps Scriptが実行される。\UTF{00A0}スクリプトは，Googleカレンダーに予定を作成し，同時にDiscordへ通知を送信を行う。
![システム概要](assets/images/gas_system_arc.png)



#### システム化の範囲
本システムは，部員による欠席連絡の申請から，カレンダーへの自動登録，および関係者への通知までを対象とする。
- **入力**: Googleフォームによる欠席情報の受付\UTF{00A0}。
- **処理**: Google Apps Scriptによるデータ処理と外部サービス連携\UTF{00A0}。
- **出力**: Googleカレンダーへの予定登録と，Discordへの通知\UTF{00A0}。
- **閲覧**: Googleカレンダー，Googleスプレッドシート，Discordによる情報確認\UTF{00A0}。

#### ユースケース図
システムで出来ることを示す。
- **部員**: 欠席連絡を行う。\UTF{00A0}%
- **役員**: 欠席情報を閲覧・確認する。
![ユースケース図](assets/images/gas_UseCase.png)


#### 処理シーケンス
部員が欠席連絡を行ってから，各システムがどのように連携して処理を行うかを時系列で示す。
![処理シーケンス](assets/images/gas_sequence.png)

#### 機能要件
1. Googleフォームを用いて，以下の項目を含む欠席連絡を受け付ける。
	- 氏名: 短文形式
	- 欠席日: 日付形式
	- 欠席理由: 任意
2. データ連携・処理
	- データ保存: フォームから送信されたすべての回答を，Googleスプレッドシートに自動で記録し，保存する。
	- カレンダー連携
		- フォームの回答をトリガーとして，指定されたGoogleカレンダーに終日の予定を自動で作成する。
		- 形式：「氏名)が欠席」

3. 通知機能（応用）:
- フォームが送信された際，Discordの指定したチャンネルに通知を送信できる 。
- 通知メッセージには，氏名，欠席日，欠席理由を含めること 。メッセージはMarkdown形式で装飾される 。
---
a. 閲覧機能
- カレンダー閲覧: 共有されたURLを通じて，関係者がGoogleカレンダー上の欠席情報を閲覧できる。
- 詳細情報閲覧: Googleスプレッドシートにアクセスし，欠席理由を含む詳細な情報を閲覧できる。

### 実装詳細
- **手順概要**
	- google formsの作成
	- formsをスプレッドシートとリンクし，スプレッドシート>回答>拡張機能メニュー>Apps Script にGAS(google Apps script)を記述
	- google calendarの設定から calendarIDを取得し，スクリプトに追加する。

#####  Googleフォームの作成
欠席連絡を受け付けるためのGoogleフォームを新規に作成した。フォームには以下の項目を設定した。
- **氏名**: 短文形式
- **欠席日**: 日付形式

##### Googleカレンダーの準備
部のアカウントでログインした状態でgoogle calendarにアクセスする。
- 新規カレンダーの作成
- 左側「他のカレンダー」の横にある+ボタン > 新しくカレンダーを作成
	- 新しく「U.R.D.C.欠席連絡」というカレンダーを作成した
	- GAS作成後もう一度使う！

##### Google Apps Script (GAS) の作成
GoogleフォームとGoogleカレンダーを連携させるためのスクリプトを記述した。
1. **スプレッドシートの作成**: フォームの「回答」タブから，フォーム回答が保存される新しいGoogleスプレッドシートを作成した。
2. **Apps Scriptエディタの起動**: 作成されたスプレッドシートの「拡張機能」メニューから「Apps Script」を選択し，エディタを起動した。
3. **スクリプトの記述**: 以下のJavaScriptコードをApps Scriptエディタに記述した。
    ```
    function onFormSubmit(e) {
      // フォームの回答から情報を取得する。
      // フォームの項目名「名前」と「いつ欠席しますか？」に対応させる。
      const name = e.namedValues['名前'][0]; // フォームの「名前」項目
      const absenceDate = e.namedValues['いつ欠席しますか？'][0]; // フォームの「いつ欠席しますか？」項目
    
      // 欠席日をDateオブジェクトに変換する。
      const dateObj = new Date(absenceDate);
    
      // GoogleカレンダーのIDを指定する。
      // 特定のカレンダーIDを直接スクリプト内に記述した。
      const calendarId = '89c2c4ae37d0890acad95c6cbeb6aad58c5a06836e960433d5d2568dfd5812f7@group.calendar.google.com'; 
      // カレンダーオブジェクトを取得する。
      const calendar = CalendarApp.getCalendarById(calendarId);
    
      // イベントのタイトルを作成する。
      const eventTitle = `${name}が欠席`;
    
      // 終日のイベントとしてカレンダーに作成する。
      calendar.createAllDayEvent(eventTitle, dateObj);
    }
    ```


5. **カレンダーIDの確認と設定**: 先ほど使用したgoogle calendarのタブにもどって，使用するGoogleカレンダー（上記例であれば「U.R.D.C.欠席連絡」）の「設定と共有」からカレンダーIDを取得し，スクリプト内の`calendarId`変数に設定した。
    
6. **トリガーの設定**: フォームの回答が送信されたときに`onFormSubmit`関数が自動的に実行されるよう，トリガーを設定した。
    - **実行する関数を選択**: `onFormSubmit`
    - **イベントのソースを選択**: `スプレッドシートから`
    - **イベントの種類を選択**: `フォーム送信時`

##### 閲覧
閲覧は，最下部「使用方法」の章で書いています。



---
応用事例：欠席連絡の通知をdiscordに来るように設定する。
### discordに欠席連絡を通知
##### discordの事前準備
- Discordにフォーム回答の通知を送る機能を追加する。
- dicscordのチャンネルを新規作成し，チャンネルを編集.> 連携サービス > ウェブフックを作成した。その後，ウェブフックURLを取得する。
	- ウェブフックとは，他のアプリケーションやwebサイトからのメッセージをdiscordに投稿できるものである。
	- ref. https://discord.com/developers/docs/resources/webhook

##### Apps Script にGASを記述
- スプレッドシート>回答>拡張機能メニュー>Apps Script にGAS(google Apps script)を記述する。すでに上記のソースコードを実行している場合はこれに上書きする。
- 次に，右側のバー下部にある歯車マーク（設定） > スクリプトプロパティに移動する。
- スクリプトプロパティの欄で，プロパティをDISCORD_WEBHOOK_URLとし，値を先ほどのdiscordで取得したウェブフックURLにする。

```
function onFormSubmit(e) {

// フォームの回答から情報を取得

const name = e.namedValues['名前'][0];

const absenceDate = e.namedValues['いつ欠席しますか？'][0];

// フォームに「欠席理由」がある場合のみ取得

const absenceReason = e.namedValues['欠席理由'] ? e.namedValues['欠席理由'][0] : 'なし';

  

// 欠席日をDateオブジェクトに変換

const dateObj = new Date(absenceDate);

  

// カレンダー連携部分

const calendarId = '89c2c4ae37d0890acad95c6cbeb6aad58c5a06836e960433d5d2568dfd5812f7@group.calendar.google.com';

const calendar = CalendarApp.getCalendarById(calendarId);

const eventTitle = `${name}が欠席`;

calendar.createAllDayEvent(eventTitle, dateObj);

  
  

// ここから Discordとの共有設定

// Discordへの通知部分を追加

// DiscordのメッセージはMarkdown形式で装飾できます。

const notificationMessage = `**欠席連絡がありました**\n>>> 氏名: ${name}\n欠席日: ${absenceDate}\n理由: ${absenceReason}`;

sendDiscordNotification(notificationMessage);

}

  

function sendDiscordNotification(messageText) {

// Discordで取得したウェブフックURLを設定

//スクリプトプロパティにウェブフックURLは保存

const DISCORD_WEBHOOK_URL = PropertiesService.getScriptProperties().getProperty('DISCORD_WEBHOOK_URL');

  

if (!DISCORD_WEBHOOK_URL) {

Logger.log('Discord Webhook URLが設定されていません。');

return;

}

  

const payload = {

"content": messageText // Discordに送信するメッセージ

};

  

const options = {

"method": "post",

"contentType": "application/json",

"payload": JSON.stringify(payload)

};

  

try {

UrlFetchApp.fetch(DISCORD_WEBHOOK_URL, options);

Logger.log('Discord通知が正常に送信されました。');

} catch (e) {

Logger.log('Discord通知の送信に失敗しました: ' + e.message);

}

}
```

#### デプロイメントの作成
- 設定からエディタに戻る。
- エディタ右上の青色で「デプロイ」と書かれたボタンがある。
- クリックするとこの画像になる。
![ deployボタン押下](assets/images/deploy1.jpg)


- 「デプロイ」 > デプロイを管理 > デプロイメントの作成 をクリックし，新規デプロイメントを作成する。
![ deployの作成](assets/images/deploy2.jpg)

- デプロイのウインドウの歯車マークをクリックすると、「ウェブアプリ」「実行可能API」「アドオン」「ライブラリ」とあるのでウェブアプリを選択
	- これで、フォームの回答をトリガーとして実行されるWebアプリケーションとしてスクリプトがデプロイされる。
- 以下のように設定する。
	- **説明**: 任意で入力
	-  **実行するユーザー**: `自分` (デフォルトでそうなっているはずです)
	- **アクセスできるユーザー**: `全員` (**ここが重要！。フォーム送信のトリガーが機能するためには、この設定が必要**。)

注意:デプロイメントを新規作成した場合，この画面になります。デプロイメント作成済みで編集したい場合，青いボタン「デプロイ」> 
