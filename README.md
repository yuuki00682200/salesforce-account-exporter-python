# Salesforce Company Search Tool

*Read this in [English](#english) or [日本語](#japanese)*

<a id="english"></a>
## English

A Python utility for searching company information in Salesforce and exporting results to CSV files.

### Features

- Search companies by name (partial or exact match)
- Enter company names directly or load from a CSV file
- View account details and related contacts
- Export results to CSV files for further analysis
- Multi-language character normalization support

### Prerequisites

- Python 3.6+
- Salesforce account with API access
- Connected App set up in Salesforce with OAuth credentials

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yuuki00682200/salesforce-company-search.git
cd salesforce-company-search
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

### Configuration

There are three ways to provide your Salesforce credentials:

1. **Environment variables**:
```bash
export SALESFORCE_USERNAME="your.email@example.com"
export SALESFORCE_PASSWORD="your-password"
export SALESFORCE_CLIENT_ID="your-client-id"
export SALESFORCE_CLIENT_SECRET="your-client-secret"
```

2. **Config file**:
Create a file named `config.ini` in the project directory with the following content:
```ini
[Salesforce]
username = your.email@example.com
password = your-password
client_id = your-client-id
client_secret = your-client-secret
```

3. **Interactive prompt**:
If credentials are not found in environment variables or config file, the program will prompt you to enter them.

### Usage

Run the script:
```bash
python sf_company_search.py
```

Follow the interactive prompts to:
1. Enter your Salesforce credentials (if not configured)
2. Select search mode (partial or exact match)
3. Choose input method (direct input or CSV file)
4. Enter company names or CSV file path
5. View search results
6. Export results to CSV files

### CSV File Format

When loading company names from a CSV file, the program expects each company name in the first column. The file can have a header row.

### Output Files

The tool generates two CSV files:
- `salesforce_companies_TIMESTAMP.csv`: Contains basic company information
- `salesforce_contacts_TIMESTAMP.csv`: Contains company information with related contacts

### Security Notes

- Never commit your Salesforce credentials to version control
- Use environment variables or a config file that is excluded from version control
- Consider using Salesforce's IP restrictions for API access

### License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<a id="japanese"></a>
## 日本語

Salesforceの企業情報を検索し、結果をCSVファイルにエクスポートするPythonユーティリティです。

### 機能

- 会社名での検索（部分一致または完全一致）
- 会社名の直接入力またはCSVファイルからの読み込み
- 取引先の詳細と関連する取引先責任者の表示
- 結果のCSVファイルへのエクスポート
- 多言語文字正規化サポート

### 必要条件

- Python 3.6以上
- API アクセス権を持つSalesforceアカウント
- OAuthクレデンシャルを設定したSalesforceの接続アプリケーション

### インストール

1. このリポジトリをクローンします:
```bash
git clone https://github.com/yuuki00682200/salesforce-company-search.git
cd salesforce-company-search
```

2. 必要なパッケージをインストールします:
```bash
pip install -r requirements.txt
```

### 設定

Salesforceの認証情報を提供する方法は3つあります:

1. **環境変数**:
```bash
export SALESFORCE_USERNAME="your.email@example.com"
export SALESFORCE_PASSWORD="your-password"
export SALESFORCE_CLIENT_ID="your-client-id"
export SALESFORCE_CLIENT_SECRET="your-client-secret"
```

2. **設定ファイル**:
プロジェクトディレクトリに`config.ini`という名前のファイルを作成し、以下の内容を記述します:
```ini
[Salesforce]
username = your.email@example.com
password = your-password
client_id = your-client-id
client_secret = your-client-secret
```

3. **対話式プロンプト**:
環境変数または設定ファイルに認証情報が見つからない場合、プログラムは入力を求めます。

### 使用方法

スクリプトを実行します:
```bash
python sf_company_search.py
```

対話式プロンプトに従って操作します:
1. Salesforceの認証情報を入力（設定されていない場合）
2. 検索モードを選択（部分一致または完全一致）
3. 入力方法を選択（直接入力またはCSVファイル）
4. 会社名またはCSVファイルのパスを入力
5. 検索結果を確認
6. 結果をCSVファイルにエクスポート

### CSVファイル形式

会社名をCSVファイルから読み込む場合、プログラムは各会社名が最初の列にあることを想定しています。ファイルにはヘッダー行があっても構いません。

### 出力ファイル

このツールは2つのCSVファイルを生成します:
- `salesforce_companies_TIMESTAMP.csv`: 基本的な会社情報を含みます
- `salesforce_contacts_TIMESTAMP.csv`: 関連する取引先責任者を含む会社情報を含みます

### セキュリティに関する注意

- Salesforceの認証情報をバージョン管理システムにコミットしないでください
- バージョン管理から除外された環境変数または設定ファイルを使用してください
- SalesforceのAPI アクセスにはIP制限の使用を検討してください

### ライセンス

このプロジェクトはMITライセンスの下で公開されています - 詳細はLICENSEファイルをご覧ください。