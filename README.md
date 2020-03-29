## 简介
xray for pytest插件
能够实现自动化测试结果导入xray的Test Execution功能，并提取测试用例json文件中的test_key字段，在Xray中将该test_key的Test加入到Test Execution中
## 安装

如果在虚拟环境中安装使用pipenv安装：

`pipenv install pytest-xray`

## 使用

首先需要准备自己的Jira用户名密码的base64编码，使用下面的代码即可

```python
import base64

base64.b64encode('nsername:password'.encode('utf-8')).decode()

```
得到base64编码后，配置到命令行参数中，用于上传报告时登入Jira
在ini文件中为pytest的运行添加参数--authentication=base64_code_generated_above
若不配置此选项，则不会上传report

务必需要在命令行中通过--test-plan-key参数指定要导入xray的Test Execution属于哪一个Test Plan

通过命令行参数--test-exec-key可以将报告导入到指定的Test Execution中，如果不添加该参数，则会创建新的Test Execution，并将测试用例及结果导入

在项目根目录的pytest.ini中添加xray url配置

```ini
addopts = -vv --authentication=base64_code_generated_above --test-plan-key=TPJ-1 --test-exec-key=TPJ-2

[xray]
XRAY_API_BASE_URL = https://jira.XXXXX.com
```
pytest测试文件放于项目内的tests目录下，测试用例的json文件放于项目内的data目录下，且测试程序python文件和测试用例json文件命名需一致，路径示例：

```yaml
--your_project_name
  --data
    --test_fixture_A.json
    --test_fixture_B.json
  --tests
    --test_fixture_A.py
    --test_fixture_B.py
```

测试程序示例：
```python
# test_file
import pytest


def test_case():
    pass
```

在json测试文件的case中指定其在Xray中的test_key：
```json
{
    "test": [
        {
            "test_key": "TPJ-1"
        }
    ]
}
```

可以在命令行中通过--revision参数指定测试的修正版本（开发提测时的版本号）

可以在命令行中通过--test-environment参数指定要导入xray的Test Execution的执行环境（如iOS、Android）

可以在命令行中通过--test-plan-version参数指定要导入xray的Test Execution的测试版本（测试计划版本）
