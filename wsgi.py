import importlib.util
import sys

# 动态加载app.py模块
spec = importlib.util.spec_from_file_location("app_module", "app.py")
app_module = importlib.util.module_from_spec(spec)
sys.modules["app_module"] = app_module
spec.loader.exec_module(app_module)

# 获取app实例
app = app_module.app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) 