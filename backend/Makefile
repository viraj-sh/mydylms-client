nuitka-linux:
	uv run nuitka \
	--standalone \
	--remove-output \
	--lto=yes \
	--jobs=4 \
	--prefer-source-code \
	--assume-yes-for-downloads \
	--product-name="MYDYLMS" \
	--company-name="viraj-sh" \
	--file-description="Effortlessly access DY LMS course materials" \
	--copyright="Copyright © 2025 github.com/viraj-sh" \
	--file-version=2.0.0 \
	--follow-imports \
    --disable-console \
	--no-deployment-flag=excluded-module-usage \
	--disable-plugin=pywebview \
	--enable-plugin=pyside6 \
	--include-package-data=fastapi \
	--include-package-data=uvicorn \
	--include-package-data=pydantic_settings \
	--include-package-data=httpx \
	--include-package-data=qtpy \
	--include-package-data=webview \
	--include-data-dir=app/static=static \
	--output-filename=MYDYLMS \
	--output-dir=dist \
	desktop.py


nuitka-mac:
	uv run nuitka \
	--mode=app \
	--macos-app-name="MYDYLMS" \
	--macos-app-icon=../.github/assets/icon.icns \
	--remove-output \
	--lto=yes \
	--jobs=4 \
	--prefer-source-code \
	--assume-yes-for-downloads \
	--product-name="MYDYLMS" \
	--company-name="viraj-sh" \
	--file-description="Effortlessly access DY LMS course materials" \
	--copyright="Copyright © 2025 github.com/viraj-sh" \
	--file-version=2.0.0 \
	--product-version=2.0.0 \
	--follow-imports \
    --disable-console \
	--no-deployment-flag=excluded-module-usage \
	--disable-plugin=pywebview \
	--enable-plugin=pyqt6 \
	--include-package-data=fastapi \
	--include-package-data=uvicorn \
	--include-package-data=pydantic_settings \
	--include-package-data=httpx \
	--include-package-data=qtpy \
	--include-package-data=webview \
	--include-data-dir=app/static=static \
	--output-filename=MYDYLMS \
	--output-dir=dist \
	desktop.py


nuitka-win:
	uv run nuitka \
	--standalone \
	--remove-output \
	--lto=yes \
	--jobs=4 \
	--prefer-source-code \
	--assume-yes-for-downloads \
	--product-name="MYDYLMS" \
	--company-name="viraj-sh" \
	--file-description="Effortlessly access DY LMS course materials" \
	--copyright="Copyright © 2025 github.com/viraj-sh" \
	--file-version=2.0.0 \
	--product-version=2.0.0 \
	--follow-imports \
	--windows-console-mode=disable \
	--no-deployment-flag=excluded-module-usage \
	--windows-icon-from-ico=../.github/assets/icon.ico \
	--disable-plugin=pywebview \
	--include-module=webview.platforms.edgechromium \
	--include-module=webview.platforms.win32 \
	--include-package-data=fastapi \
	--include-package-data=uvicorn \
	--include-package-data=pydantic_settings \
	--include-package-data=httpx \
	--include-package-data=webview \
	--include-data-dir=app/static=static \
	--output-filename=MYDYLMS \
	--output-dir=dist \
	desktop.py

desktop:
	uv run desktop.py

sync:
	uv sync --dev --extra desktop