@echo off
setlocal enabledelayedexpansion

REM pip install fonttools brotli
REM npm install -g ttf2woff

for /d %%d in (*) do (
    echo Processing directory: %%d
	
    :: 转换所有OTF文件
	for %%f in ("%%d\*.otf") do (
        echo Converting %%f
        python FontTools.py %%f
        if exist "%%~dpnf.woff2" (
            del "%%f"
            echo Deleted original TTF
        )
    )
	
	
    for %%f in ("%%d\*.ttc") do (
        echo Converting %%f
        python FontTools.py %%f
        del "%%f"
    )
    :: 转换所有TTF文件
    for %%f in ("%%d\*.ttf") do (
        echo Converting %%f
        ttf2woff "%%f" "%%~dpnf.woff2"
        if exist "%%~dpnf.woff2" (
            del "%%f"
            echo Deleted original TTF
        )
    )
    
    :: 设置目录名和CSS路径
    set "dirName=%%~nxd"
    set "cssPath=%%d\style.css"
    
    :: 清空或创建CSS文件
    echo /* Font faces for !dirName! */ > "!cssPath!"
    
    :: 收集所有字体名称
    set "fontList="
    for %%f in ("%%d\*.woff2") do (
        set "fontName=%%~nf"
        set "fileName=%%~nxf"
        
        (
            echo.
            echo @font-face {
            echo     font-family: '!fontName!';
            echo     src: url('https://source.pika.net.cn/ttf/!dirName!/!fileName!'^) format('woff2'^);
            echo     font-weight: normal;
            echo     font-style: normal;
            echo     font-display: swap;
            echo }
        ) >> "!cssPath!"
        
        :: 构建字体列表
        if "!fontList!"=="" (
            set "fontList='!fontName!'"
        ) else (
            set "fontList=!fontList!, '!fontName!'"
        )
    )
    
    :: 添加全局CSS规则
    if not "!fontList!"=="" (
        (
            echo.
            echo /* Global font settings */
            echo * {
            echo     font-family: !fontList!, sans-serif;
            echo }
            echo.
            echo body {
            echo     font-family: !fontList!, sans-serif;
            echo     -webkit-font-smoothing: antialiased;
            echo     -moz-osx-font-smoothing: grayscale;
            echo     line-height: 1.6;
            echo }
            echo.
            echo /* Ensure text elements use the font */
            echo h1, h2, h3, h4, h5, h6, p, span, div, a, li, td, th {
            echo     font-family: inherit;
            echo }
        ) >> "!cssPath!"
    )
    
    echo CSS generated: !cssPath!
    echo.
)

echo All directories processed.
pause