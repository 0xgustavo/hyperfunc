import argparse

from .consumer import consume


def main():
    parser = argparse.ArgumentParser(description="CLI tool example.")
    subparsers = parser.add_subparsers(dest="command")

    # 定义 consume 子命令
    parser_worker = subparsers.add_parser("work", help="Start working")
    parser_worker.set_defaults(func=consume)

    # 解析命令行参数
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
