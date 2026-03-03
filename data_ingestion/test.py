from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
import asyncio
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

md_generator = DefaultMarkdownGenerator(
    content_filter=PruningContentFilter(threshold=0.4, threshold_type="fixed")
)

config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    markdown_generator=md_generator
)

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://ptithcm.edu.vn/tuyen-sinh/thong-bao-thong-tin-chi-tiet-cac-phuong-thuc-tuyen-sinh-dai-hoc-he-chinh-quy-nam-2026.html",
                                    config=config,
                                    css_selector=".post-wrapper")

        with open("main_only_output.md", "w", encoding="utf-8") as f:
            f.write(result.markdown.fit_markdown)

if __name__ == "__main__":
    asyncio.run(main())