"""
离线数据扫描脚本
训练前跑一次，检查 dataset/ 下所有图片的有效性
输出清洗报告，不做删除/移动操作
"""
import os
from PIL import Image


def is_valid_image(filepath):
    """检查单张图片是否有效，返回 (bool, str)"""
    # 1. PIL 能否打开
    try:
        img = Image.open(filepath)
    except Exception as e:
        return False, f"PIL open failed: {e}"

    # 2. verify 解码
    try:
        img.verify()
    except Exception as e:
        return False, f"verify failed: {e}"

    # verify 之后对象可能不可用，重新打开
    try:
        img = Image.open(filepath)
        # 3. 检查模式 RGB
        if img.mode != "RGB":
            return False, f"mode={img.mode}, expected RGB"
        # 4. 尺寸下限
        w, h = img.size
        if w < 32 or h < 32:
            return False, f"size={w}x{h}, min 32x32 required"
    except Exception as e:
        return False, f"re-open failed: {e}"

    return True, "ok"


def is_valid_file(filepath):
    """
    运行时快速过滤函数，给 ImageFolder 的 is_valid_file 用
    只做 Image.open() 基本检查，不 verify（性能考虑）
    坏图应该先由 check_data.py 离线扫描发现
    """
    try:
        img = Image.open(filepath)
        img.load()  # 强制解码，空文件会在这里报错
        return True
    except Exception:
        return False


def scan_directory(root_dir, label=""):
    """扫描一个目录下所有 .png 文件"""
    bad = []
    good = 0
    total = 0

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for fname in sorted(filenames):
            if not fname.lower().endswith(".png"):
                continue
            total += 1
            fpath = os.path.join(dirpath, fname)
            ok, reason = is_valid_image(fpath)
            if ok:
                good += 1
            else:
                bad.append((fpath, reason))

    print(f"\n{'='*60}")
    print(f"  {label or root_dir}")
    print(f"{'='*60}")
    print(f"  Total files : {total}")
    print(f"  Valid       : {good}")
    print(f"  Bad         : {len(bad)}")

    if bad:
        print(f"\n  Bad file details:")
        for path, reason in bad:
            rel = os.path.relpath(path, start=os.getcwd())
            print(f"    {rel}")
            print(f"      -> {reason}")

    return total, good, bad


if __name__ == "__main__":
    # 项目根目录（src/ 的父目录）
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base = os.path.join(project_root, "dataset")
    dirs = ["train", "test1", "test2"]

    total_all, good_all, bad_all = 0, 0, []

    for d in dirs:
        dpath = os.path.join(base, d)
        if os.path.isdir(dpath):
            t, g, b = scan_directory(dpath, label=d)
            total_all += t
            good_all += g
            bad_all.extend(b)
        else:
            print(f"[WARN] Directory not found: {dpath}")

    print(f"\n{'='*60}")
    print(f"  Summary")
    print(f"{'='*60}")
    print(f"  Total files : {total_all}")
    print(f"  Valid       : {good_all}")
    print(f"  Bad         : {len(bad_all)}")
