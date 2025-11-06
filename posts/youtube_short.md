# CloudflareによるYouTube Shorts遮断に関する検証
### 1.当初の目的

iPhone（iOS）を組織のCloudflareOne（ZeroTrust）経由で接続させ，HTTPS 通信のパス構造(/shorts/ を含むリクエスト)をCloudflare Gateway側で検出し，Zero Trustポリシーにより遮断する構成を目指した。

### 2.実際に試した検討・作業の流れ（要約）
- 1.	CloudflareZeroTrustのアカウント作成，組織（team）を作成
- 2.	ZeroTrustのダッシュボードでWARP/Deviceenrollmentを設定（デバイス登録ポリシーの作成）。
- 3.	iOSに入れるべきCloudflareのクライアントアプリ（WARP/1.1.1.1/CloudflareOneAgent）を探してインストールし，組織への登録を試みた。
- 4.	WARP接続をオンにしたところ，「接続→遮断→再試行」を繰り返す不安定動作になり，接続が安定しなかったため運用できないと判断。なお，UI側でDeviceenrollmentポリシーのセレクタが変わっており，期待どおりの「DevicePlatform（iOS）」ではなくメールベースの条件でしか絞れないなど管理面でも齟齬が発生。


### 3. 試行手順

#### (1) アカウント作成および組織設定
- https://one.dash.cloudflare.com￼ にて Cloudflare アカウントを新規作成。
- 「Zero Trust」 > 「Settings」 > 「General」 にて Team name (shimaenaga-0110)を設定。この名称を iPhone 側 WARP クライアントの Team name 入力時に使用した。
#### (2) Zero Trust > Settings > WARP Client 構成
- 「Device Enrollment Permissions」 > Manage を開き，タブ 「Policies」 から Add policy を作成。
	-  https://one.dash.cloudflare.com/0adc667c2afcc07957558cb0b2f9a509/access/policies/add

設定内容を以下に示す。

| 項目            | 設定値                                   |
| :------------ | :------------------------------------ |
| Policy name   | Allow Yamawaki iPhone                 |
| Description   | 大学メールドメインからの登録を許可                     |
| Action        | Allow                                 |
| Include Rule  | Emails ending in → @ie.u-ryukyu.ac.jp |
| Policy Tester | 自身の大学メールで Allow を確認                   |
| Save          | 有効化                                   |

#### (3)認証方式の設定
- 「Settings>Authentication」でOne- timePIN（メール認証）を追加し有効化。
- iPhone側ログイン時にメール経由のPIN認証を使用する方式とした。

#### (4)iPhone側WARPクライアント設定
- AppStoreから「1.1.1.1:FasterInternetbyCloudflare」をインストール。
- 歯車>Advanced>Useadifferentaccount/teamを選択。
- Teamnameを入力。
- SafariでOne- timePINによる認証を完了。
- VPNプロファイルのインストールを許可。

#### (5)接続テスト
- 接続状態は「Connecting→Disconnected→Connecting」を繰り返し，安定接続に至らず。
- 他VPN・DNS保護アプリを停止しても改善せず。
- ルータおよび大学LANでUDP2408/500/1701/4500ポートが閉塞している可能性を確認。
- TunnelProtocol(WireGuard⇄MASQUE)切替を実施したが同様の結果となった。
### 4. 実施後の結果
1.	Cloudflare Zero Trustの設定完了後もiPhoneのWARPクライアントは安定接続できなかった。
2.	Zero Trustダッシュボード上の Device Enrollment Policyには，旧UIで存在したDevice Platformセレクタが表示されず，メールドメイン条件のみ設定可能であった。
3.	WARP クライアントは接続試行後に即時遮断を繰り返し，VPN セッションが確立しない状態であった。
4.	TLS 復号を伴う通信検査を行うには，ルートCA証明書をiPhone へ配布・信頼設定する必要があることを確認した。
5.	現状のネットワーク環境（学内・自宅LAN）では，WireGuard ベースのUDP通信が制限されている可能性が高い。

### 5. 技術的考察と判断
1.	主原因はUDPトンネル確立失敗である。
	　Cloudflare WARP は WireGuard プロトコルを使用し，UDP 2408 を既定ポートとする。これが環境側で遮断されているため，ハンドシェイクに失敗していると判断する。
2.	TLS 復号運用は個人環境では非現実的である。
	　Zero Trust Gateway のHTTPS検査を有効化するには，iOS 端末ごとにルート証明書を配布し信頼設定する必要があり，セキュリティリスク・管理負担が大きい。
3.	無料プランの機能制限が要件を満たさない。
	　現行UIでは Device Platform 指定など詳細条件が利用不可であり，想定していた端末単位の制御ポリシーを実現できない。

以上の技術的・運用的制約から，本試行は実用段階に移行できないと判断し，中止を決定した。
代替策の検討として，まずyoutubeアプリの削除を行いブラウザベースでのみ閲覧可能な状況を作った上で，AdGuardというブラウザの拡張機能を用いて，youtube shortの要素を非表示にすることを試みる。
この方式では，Cloudflare Zero Trust 導入時に問題となったUDP 通信・無料プランの限界という課題を回避できると考える。



# AdGuardによるYouTube Shorts遮断に関する検証

## 1. 目的
本報告は，YouTubeにおける短尺動画コンテンツ「YouTube Shorts」を，広告・トラッキング遮断ツールである**AdGuard**のユーザールール機能を用いて制限する試みについて記述するものである。目的は，通常のYouTube動画（`/watch?v=`形式）を維持しつつ，`/shorts/`形式の動画および関連要素を不可視化または再生不能とする設定手法を明確にすることである。

---

## 2. 使用環境
- **OS**：macOS Sonoma
- **ブラウザ**：Google Chrome
- **AdGuard**：AdGuard for Mac
- **対象サイト**：`https://www.youtube.com`

YouTubeはSingle Page Application（SPA）構造を採用しており，URL遷移時にページ全体の再読み込みを行わず，JavaScriptによる部分的なDOM（Document Object Model）更新を行う。この特性がフィルタリングルールの即時適用を困難にしている。

---

## 3. 設定ルール一覧
以下に最終的に採用したユーザールールを示す。

```adguard
www.youtube.com##ytd-reel-shelf-renderer
www.youtube.com##ytd-rich-section-renderer:has(a[href*="/shorts/"])
www.youtube.com##ytd-grid-renderer ytd-grid-video-renderer:has(a[href*="/shorts/"])
www.youtube.com##ytd-browse[page-subtype="subscriptions"] ytd-grid-video-renderer:has(a[href*="/shorts/"])
youtube.com/shorts^$redirect=abp-resource:blank-html
youtube.com/shorts/*$document
www.youtube.com##ytd-video-renderer:has(a[href*="/shorts/"])
www.youtube.com##ytd-rich-item-renderer:has(a[href*="/shorts/"])
```

⸻
### 4. 各ルールの機能的説明

####  `##`構文による要素隠蔽

AdGuardの構文`##selector`は，CSSセレクタ（HTML要素識別子）に該当する要素を非表示化する命令である。
以下の4行がこれに該当する。

| ルール                                                                                                          | 対象                      | 処理内容                                                                                |
| :----------------------------------------------------------------------------------------------------------- | :---------------------- | :---------------------------------------------------------------------------------- |
| `www.youtube.com##ytd-reel-shelf-renderer`                                                                   | ホーム画面上の「ショート動画」セクション    | `ytd-reel-shelf-renderer`はYouTube Shorts一覧のDOM要素を指す。このルールにより，ホーム画面のShorts表示を非表示化する。 |
| `www.youtube.com##ytd-rich-section-renderer:has(a[href*="/shorts/"])`                                        | 「おすすめ」や「関連」欄に含まれるShorts | `:has()`疑似クラスにより，リンク先に/shorts/を含む項目を選択し，非表示とする。                                     |
| `www.youtube.com##ytd-grid-renderer ytd-grid-video-renderer:has(a[href*="/shorts/"])`                        | チャンネル内のShorts           | グリッド形式で表示される動画群のうち，Shortsリンクを持つ動画カードを除外する。                                          |
| `www.youtube.com##ytd-browse[page-subtype="subscriptions"] ytd-grid-video-renderer:has(a[href*="/shorts/"])` | 登録チャンネル一覧（購読タブ）         | 購読ページでShortsが表示されないように制御する。                                                         |


#### 4.2 $redirect による空白ページリダイレクト

`youtube.com/shorts^$redirect=abp-resource:blank-html`

- `$redirect` オプションは，指定URLへのアクセスを別のリソースに転送する機能である。これにより，ユーザーがショート動画ページを直接開いた場合でも再生が行われない。
	- ここでは` abp-resource:blank-html`（AdBlock Plus互換の空白HTML）を指定しoutube.com/shorts/ 以下のURLをすべて白ページへリダイレクトする。
	- ^ はURLパス区切りのワイルドカード。

#### 4.3 `$document`によるページ全体遮断

`youtube.com/shorts/*$document`

- このルールは，`/shorts/` 以下のURLを「ドキュメント単位で」遮断する命令である。CSSによる非表示処理ではなく，HTTP応答レベルでアクセス自体を止めるため，YouTubeのSPA挙動にも対応できる。なお，`$document`はHTML文書を意味し，[[SPA（Single Page Application）]]に対してはこの指定が有効である。

### 5. 動作検証都考察
1.	/shorts タブに直接アクセスした場合，当初は一瞬再生が始まるが，リロード後にAdGuardルールが適用され白画面となる。
2. $document 指定を追加した後は，遷移直後から即座に再生が停止し，空白ページが表示される。
3.	ホーム画面および登録チャンネルページにおけるShorts欄は完全に非表示となり，通常動画の視聴には影響しなかった。

`$document` および`$redirect`指定は，HTTPリクエストレベルでのフィルタリングを行うため，SPA遷移後も継続的に有効となる。また，ytd-で始まる要素名はYouTubeが用いるWeb Components形式の独自タグであり，これらを対象にすることで特定コンテンツ（Shorts）のみを精密に制御できることがわかった。
