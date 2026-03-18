import argparse
from data_ingestion import ingest
from evaluation import evaluate

def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command", help="Các lệnh có sẵn")
    subparsers.required = True

    parser_ingest = subparsers.add_parser(
        "ingest", help="Chạy pipeline thu thập và xử lý dữ liệu"
    )

    parser_eval = subparsers.add_parser(
        "evaluate",
        help="Chạy đánh giá hệ thống"
    )

    parser_ingest.add_argument("--crawl", action="store_true", help="Cào HTML gốc về")
    parser_ingest.add_argument("--parse", action="store_true", help="Parse HTML vào MongoDB")
    parser_ingest.add_argument("--chunk", action="store_true", help="Chunk dữ liệu")
    parser_ingest.add_argument("--embed", action="store_true", help="Embed vào vector DB")
    parser_ingest.add_argument("--rag", choices=["naive", "rerank", "hybrid"])

    parser_eval.add_argument("--retrieval", action="store_true", help="Đánh giá retriever")
    parser_eval.add_argument("--generation", action="store_true", help="Đánh giá generator")
    parser_eval.add_argument("--rag", required=True, choices=["naive", "rerank", "hybrid"])
    parser_eval.add_argument("--topk", required=True, choices=[5, 10, 20])

    args = parser.parse_args()

    if args.command == "ingest":
        ingest.run(
            crawl=args.crawl,
            parse=args.parse,
            chunk=args.chunk,
            embed=args.embed,
            rag=args.rag
        )
    elif args.commad == "evaluate":
        evaluate.run(
            retrieval=args.retrieval,
            generation=args.generation,
            rag=args.rag,
            topk=args.topk
        )

if __name__ == "__main__":
    main()