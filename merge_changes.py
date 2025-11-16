#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
合并脚本：将"已修改内容"目录中的更新合并到主项目
使用方法: python merge_changes.py
"""

import os
import shutil
import filecmp
import difflib
from pathlib import Path
from datetime import datetime

# 配置
SOURCE_DIR = "已修改内容"  # 源目录（合作开发者的修改）
TARGET_DIR = "."  # 目标目录（主项目）
BACKUP_DIR = f"备份_{datetime.now().strftime('%Y%m%d_%H%M%S')}"  # 备份目录

# 要合并的应用目录
APPS_TO_MERGE = ['accessment', 'ELW', 'stu_practice']

# 要忽略的文件和目录
IGNORE_PATTERNS = [
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '*.rar',
    '.git',
    'migrations',  # 数据库迁移文件需要特别处理
]

def should_ignore(file_path):
    """检查文件是否应该被忽略"""
    for pattern in IGNORE_PATTERNS:
        if pattern in str(file_path):
            return True
    return False

def get_all_files(directory, app_name):
    """获取应用目录下的所有文件"""
    app_path = Path(directory) / app_name
    if not app_path.exists():
        return []
    
    files = []
    for root, dirs, filenames in os.walk(app_path):
        # 过滤掉忽略的目录
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d))]
        
        for filename in filenames:
            file_path = Path(root) / filename
            if not should_ignore(file_path):
                # 获取相对路径
                rel_path = file_path.relative_to(app_path)
                files.append(rel_path)
    
    return files

def compare_files(source_file, target_file):
    """比较两个文件，返回差异信息"""
    if not os.path.exists(source_file):
        return None, "源文件不存在"
    
    if not os.path.exists(target_file):
        return "new", "目标文件不存在，将创建新文件"
    
    if filecmp.cmp(source_file, target_file, shallow=False):
        return "same", "文件相同，无需更新"
    
    # 文件不同，返回差异
    with open(source_file, 'r', encoding='utf-8', errors='ignore') as f1:
        source_lines = f1.readlines()
    with open(target_file, 'r', encoding='utf-8', errors='ignore') as f2:
        target_lines = f2.readlines()
    
    diff = list(difflib.unified_diff(
        target_lines, source_lines,
        fromfile=str(target_file),
        tofile=str(source_file),
        lineterm=''
    ))
    
    return "different", diff

def backup_file(file_path):
    """备份文件"""
    if not os.path.exists(file_path):
        return
    
    backup_path = Path(BACKUP_DIR) / file_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file_path, backup_path)

def merge_file(source_file, target_file, dry_run=False):
    """合并单个文件"""
    if not os.path.exists(source_file):
        return False, "源文件不存在"
    
    # 创建备份
    if not dry_run and os.path.exists(target_file):
        backup_file(target_file)
    
    # 确保目标目录存在
    target_dir = os.path.dirname(target_file)
    if not dry_run:
        os.makedirs(target_dir, exist_ok=True)
    
    # 复制文件
    if not dry_run:
        shutil.copy2(source_file, target_file)
        return True, "文件已合并"
    else:
        return True, "（模拟）文件将被合并"

def merge_app(app_name, dry_run=True):
    """合并整个应用"""
    print(f"\n{'='*60}")
    print(f"处理应用: {app_name}")
    print(f"{'='*60}")
    
    source_app = Path(SOURCE_DIR) / app_name
    target_app = Path(TARGET_DIR) / app_name
    
    if not source_app.exists():
        print(f"⚠️  源目录不存在: {source_app}")
        return
    
    # 获取所有文件
    source_files = get_all_files(SOURCE_DIR, app_name)
    
    if not source_files:
        print(f"⚠️  源目录中没有找到文件")
        return
    
    # 统计信息
    stats = {
        'new': [],
        'updated': [],
        'same': [],
        'errors': []
    }
    
    print(f"\n找到 {len(source_files)} 个文件需要检查...\n")
    
    for rel_file in source_files:
        source_file = source_app / rel_file
        target_file = target_app / rel_file
        
        status, info = compare_files(source_file, target_file)
        
        if status == "new":
            print(f"📄 新文件: {rel_file}")
            stats['new'].append(rel_file)
            if not dry_run:
                success, msg = merge_file(source_file, target_file, dry_run=False)
                if success:
                    print(f"   ✅ {msg}")
                else:
                    print(f"   ❌ {msg}")
                    stats['errors'].append((rel_file, msg))
        
        elif status == "different":
            print(f"🔄 已修改: {rel_file}")
            stats['updated'].append(rel_file)
            if not dry_run:
                success, msg = merge_file(source_file, target_file, dry_run=False)
                if success:
                    print(f"   ✅ {msg}")
                else:
                    print(f"   ❌ {msg}")
                    stats['errors'].append((rel_file, msg))
            else:
                # 显示差异预览（前10行）
                if isinstance(info, list) and len(info) > 0:
                    print(f"   差异预览（前10行）:")
                    for line in info[:10]:
                        print(f"   {line}")
                    if len(info) > 10:
                        print(f"   ... 还有 {len(info) - 10} 行差异")
        
        elif status == "same":
            stats['same'].append(rel_file)
            # 不显示相同文件，减少输出
        
        elif status is None:
            print(f"❌ 错误: {rel_file} - {info}")
            stats['errors'].append((rel_file, info))
    
    # 打印统计信息
    print(f"\n{'='*60}")
    print(f"统计信息 ({app_name}):")
    print(f"  新文件: {len(stats['new'])}")
    print(f"  已更新: {len(stats['updated'])}")
    print(f"  无变化: {len(stats['same'])}")
    print(f"  错误: {len(stats['errors'])}")
    print(f"{'='*60}")
    
    return stats

def main():
    """主函数"""
    print("="*60)
    print("合并脚本：将合作开发者的更新合并到主项目")
    print("="*60)
    
    # 检查源目录
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ 错误: 源目录不存在: {SOURCE_DIR}")
        return
    
    # 创建备份目录
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"📦 已创建备份目录: {BACKUP_DIR}")
    
    # 首先进行模拟运行（dry run）
    print("\n" + "="*60)
    print("第一步: 模拟运行（预览将要进行的更改）")
    print("="*60)
    
    all_stats = {}
    for app_name in APPS_TO_MERGE:
        stats = merge_app(app_name, dry_run=True)
        if stats:
            all_stats[app_name] = stats
    
    # 询问用户是否继续
    print("\n" + "="*60)
    print("预览完成！")
    print("="*60)
    
    total_new = sum(len(s.get('new', [])) for s in all_stats.values())
    total_updated = sum(len(s.get('updated', [])) for s in all_stats.values())
    
    print(f"\n总计:")
    print(f"  新文件: {total_new}")
    print(f"  将更新: {total_updated}")
    print(f"\n备份目录: {BACKUP_DIR}")
    
    response = input("\n是否继续执行合并？(yes/no): ").strip().lower()
    
    if response not in ['yes', 'y', '是']:
        print("❌ 已取消合并操作")
        return
    
    # 执行实际合并
    print("\n" + "="*60)
    print("第二步: 执行实际合并")
    print("="*60)
    
    for app_name in APPS_TO_MERGE:
        merge_app(app_name, dry_run=False)
    
    print("\n" + "="*60)
    print("✅ 合并完成！")
    print("="*60)
    print(f"\n备份已保存到: {BACKUP_DIR}")
    print("\n⚠️  重要提示:")
    print("1. 请检查合并后的代码")
    print("2. 运行测试确保功能正常")
    print("3. 如有问题，可以从备份目录恢复文件")
    print("4. 数据库迁移文件（migrations）需要特别处理，请手动检查")

if __name__ == "__main__":
    main()

