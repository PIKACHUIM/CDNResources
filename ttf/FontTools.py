#!/usr/bin/env python3
import os
import sys
import glob
from fontTools.ttLib import TTFont, TTLibError

def convert_font_to_woff2(input_path, out_dir=None):
    """
    将字体文件转换为WOFF2格式
    支持: .ttc, .otc, .ttf, .otf
    """
    out_dir = out_dir or os.path.dirname(input_path)
    os.makedirs(out_dir, exist_ok=True)
    
    ext = os.path.splitext(input_path)[1].lower()
    
    try:
        if ext in ['.ttc', '.otc']:
            # 处理字体集合文件
            return convert_ttc_to_woff2(input_path, out_dir)
        elif ext in ['.ttf', '.otf']:
            # 处理单个字体文件
            return convert_single_font_to_woff2(input_path, out_dir)
        else:
            print(f'❌ 不支持的格式: {ext}')
            return False
    except TTLibError as e:
        print(f'❌ 字体文件错误 {input_path}: {e}')
        return False
    except Exception as e:
        print(f'❌ 转换失败 {input_path}: {e}')
        return False

def convert_ttc_to_woff2(ttc_path, out_dir):
    """转换TTC/OTC字体集合文件"""
    base_name = os.path.splitext(os.path.basename(ttc_path))[0]
    
    try:
        # 获取字体集合中的字体数量
        with TTFont(ttc_path, fontNumber=0, lazy=True) as tmp:
            num_fonts = tmp.reader.numFonts
        
        success_count = 0
        for idx in range(num_fonts):
            font = TTFont(ttc_path, fontNumber=idx)
            
            # 获取字体名称
            font_name = get_font_name(font, base_name, idx)
            
            woff2_path = os.path.join(out_dir, f'{font_name}.woff2')
            
            # 转换为WOFF2
            font.flavor = 'woff2'
            font.save(woff2_path)
            print(f'✅ TTC字体 {idx+1}/{num_fonts}: {font_name}.woff2')
            font.close()
            success_count += 1
        
        return success_count > 0
        
    except Exception as e:
        print(f'❌ TTC转换失败 {ttc_path}: {e}')
        return False

def convert_single_font_to_woff2(font_path, out_dir):
    """转换单个TTF/OTF字体文件"""
    try:
        font = TTFont(font_path)
        base_name = os.path.splitext(os.path.basename(font_path))[0]
        
        # 获取字体名称
        font_name = get_font_name(font, base_name)
        
        woff2_path = os.path.join(out_dir, f'{font_name}.woff2')
        
        # 转换为WOFF2
        font.flavor = 'woff2'
        font.save(woff2_path)
        print(f'✅ 单个字体: {font_name}.woff2')
        font.close()
        
        return True
        
    except Exception as e:
        print(f'❌ 单个字体转换失败 {font_path}: {e}')
        return False

def get_font_name(font, base_name, index=None):
    """获取字体的PostScript名称"""
    try:
        # 尝试从不同平台获取字体名称
        name_records = [
            font['name'].getName(6, 1, 0),   # Mac platform
            font['name'].getName(6, 3, 1),   # Windows platform
            font['name'].getName(6, 3, 0),   # Windows Unicode
            font['name'].getName(6, 2, 0),   # ISO platform
        ]
        
        for name_record in name_records:
            if name_record is not None:
                ps_name = str(name_record).strip()
                # 清理文件名中的非法字符
                ps_name = ''.join(c for c in ps_name if c.isalnum() or c in ('-', '_', ' '))
                ps_name = ps_name.replace(' ', '-')
                return ps_name
        
        # 如果没有找到合适的名称，使用基础名称和索引
        if index is not None:
            return f"{base_name}-{index}"
        else:
            return base_name
            
    except Exception:
        if index is not None:
            return f"{base_name}-{index}"
        else:
            return base_name

def batch_convert_directory(input_dir, output_dir=None):
    """批量转换目录中的所有字体文件"""
    if output_dir is None:
        output_dir = os.path.join(input_dir, 'woff2_output')
    
    os.makedirs(output_dir, exist_ok=True)
    
    supported_extensions = ['.ttc', '.otc', '.ttf', '.otf']
    font_files = []
    
    # 收集所有支持的字体文件
    for ext in supported_extensions:
        font_files.extend(glob.glob(os.path.join(input_dir, f'*{ext}')))
    
    if not font_files:
        print(f'❌ 在目录 {input_dir} 中未找到支持的字体文件')
        return False
    
    print(f'📁 找到 {len(font_files)} 个字体文件')
    success_count = 0
    
    for font_file in font_files:
        if convert_font_to_woff2(font_file, output_dir):
            success_count += 1
    
    print(f'\n🎉 转换完成: {success_count}/{len(font_files)} 个文件成功')
    return success_count > 0

def main():
    if len(sys.argv) < 2:
        print('''
字体转换工具 - 支持 TTC, OTC, TTF, OTF 转 WOFF2

用法:
  python font2woff2.py 字体文件.ttc        # 转换单个文件
  python font2woff2.py 字体文件.otf        # 转换单个文件
  python font2woff2.py 目录路径           # 批量转换目录中的所有字体文件
  python font2woff2.py 字体文件.ttc 输出目录 # 指定输出目录

示例:
  python font2woff2.py font.ttc
  python font2woff2.py font.otf
  python font2woff2.py ./fonts
  python font2woff2.py font.ttc ./output
''')
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    if os.path.isfile(input_path):
        # 单个文件转换
        convert_font_to_woff2(input_path, output_dir)
    elif os.path.isdir(input_path):
        # 批量目录转换
        batch_convert_directory(input_path, output_dir)
    else:
        print(f'❌ 路径不存在: {input_path}')
        sys.exit(1)

if __name__ == '__main__':
    main()