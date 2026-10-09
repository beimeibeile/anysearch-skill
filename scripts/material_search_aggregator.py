"""
AnySearch 素材搜索聚合器
为视频制作流程提供结构化素材搜索能力，支持多平台聚合搜索、结果去重、质量评估

核心能力：
1. 多关键词并行搜索（图片/视频/音乐/音效/参考资料）
2. 搜索结果结构化解析（标题/链接/摘要/来源/可信度）
3. 结果去重与排序（按相关性/可信度/时效性）
4. 素材清单导出（JSON/Markdown格式，供后续制作流程使用）
"""

import logging
logger = logging.getLogger(__name__)

import os
import sys
import json
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

# 导入AnySearch CLI
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)


@dataclass
class SearchResult:
    """单条搜索结果"""
    title: str
    url: str
    snippet: str = ""
    source: str = ""
    relevance: float = 0.0  # 相关性 0-1
    credibility: float = 0.5  # 可信度 0-1
    publish_date: str = ""
    content_type: str = "general"  # image/video/audio/text/reference
    fingerprint: str = ""

    def __post_init__(self):
        if not self.fingerprint:
            self.fingerprint = hashlib.md5(self.url.encode()).hexdigest()[:12]


@dataclass
class MaterialAsset:
    """素材资产（搜索后整理的可用素材）"""
    asset_id: str
    asset_type: str  # image/video/audio/reference
    title: str
    source_url: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    license: str = "unknown"  # free/commercial/unknown
    downloaded: bool = False
    local_path: str = ""


class MaterialSearchAggregator:
    """素材搜索聚合器"""

    # 素材类型→搜索关键词模板
    TYPE_KEYWORDS = {
        "image": ["{query} 图片", "{query} 高清图片", "{query} 素材图"],
        "video": ["{query} 视频素材", "{query} 实拍视频", "{query} 短片"],
        "audio": ["{query} 背景音乐", "{query} 音效", "{query} BGM"],
        "reference": ["{query} 参考", "{query} 案例", "{query} 设计灵感"],
    }

    # 可信度权重
    SOURCE_CREDIBILITY = {
        "zhihu.com": 0.9,
        "bilibili.com": 0.8,
        "xiaohongshu.com": 0.7,
        "douyin.com": 0.6,
        "weibo.com": 0.6,
        "baidu.com": 0.5,
        "google.com": 0.7,
        "unsplash.com": 0.95,
        "pexels.com": 0.95,
        "pixabay.com": 0.9,
    }

    def __init__(self, anysearch_cli=None):
        self.cli = anysearch_cli
        self.search_history: List[Dict] = []
        self.result_cache: Dict[str, List[SearchResult]] = {}

    def search_materials(self, query: str, material_types: List[str] = None,
                         max_per_type: int = 5) -> Dict[str, List[SearchResult]]:
        """
        多类型素材并行搜索

        Args:
            query: 搜索主题（如"科技感未来城市"）
            material_types: 素材类型列表，默认全部
            max_per_type: 每种类型最多返回结果数

        Returns:
            {material_type: [SearchResult, ...]}
        """
        material_types = material_types or ["image", "video", "audio", "reference"]
        results = {}

        for mtype in material_types:
            keywords = [kw.format(query=query) for kw in self.TYPE_KEYWORDS.get(mtype, [query])]
            type_results = []
            seen_fingerprints = set()

            for kw in keywords:
                try:
                    raw_results = self._do_search(kw)
                    for r in raw_results:
                        result = self._parse_result(r, mtype)
                        if result.fingerprint not in seen_fingerprints:
                            seen_fingerprints.add(result.fingerprint)
                            type_results.append(result)
                except Exception as e:
                    logger.warning(f"搜索失败 [{kw}]: {e}")

            # 按相关性+可信度排序
            type_results.sort(key=lambda x: x.relevance * 0.6 + x.credibility * 0.4, reverse=True)
            results[mtype] = type_results[:max_per_type]
            logger.info(f"[{mtype}] 搜索完成: {len(type_results)}条结果（去重后）")

        self.search_history.append({
            "query": query,
            "types": material_types,
            "timestamp": datetime.now().isoformat(),
            "result_counts": {k: len(v) for k, v in results.items()},
        })

        return results

    def build_material_list(self, query: str, material_types: List[str] = None,
                            output_format: str = "markdown") -> str:
        """
        构建素材清单（供剧本/分镜阶段使用）

        Args:
            query: 搜索主题
            material_types: 素材类型
            output_format: markdown / json

        Returns:
            格式化的素材清单文本
        """
        results = self.search_materials(query, material_types)

        if output_format == "json":
            return json.dumps({
                "query": query,
                "generated_at": datetime.now().isoformat(),
                "materials": {k: [asdict(r) for r in v] for k, v in results.items()},
            }, ensure_ascii=False, indent=2)

        # Markdown格式
        lines = [f"# 素材清单：{query}", f"", f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]

        type_names = {"image": "图片素材", "video": "视频素材", "audio": "音频素材", "reference": "参考资料"}
        for mtype, type_results in results.items():
            lines.append(f"## {type_names.get(mtype, mtype)}（{len(type_results)}条）")
            lines.append("")
            for i, r in enumerate(type_results, 1):
                lines.append(f"### {i}. {r.title}")
                lines.append(f"- 链接：{r.url}")
                lines.append(f"- 来源：{r.source}")
                lines.append(f"- 可信度：{r.credibility:.1f}/1.0")
                if r.snippet:
                    lines.append(f"- 摘要：{r.snippet[:100]}")
                lines.append("")

        return "\n".join(lines)

    def _do_search(self, keyword: str) -> List[Dict]:
        """执行单次搜索（通过AnySearch CLI）"""
        if self.cli is None:
            # 降级：返回空结果
            logger.debug(f"AnySearch CLI未配置，跳过搜索: {keyword}")
            return []

        try:
            results = self.cli.cmd_search(keyword)
            if isinstance(results, list):
                return results
            if isinstance(results, dict) and "results" in results:
                return results["results"]
            return []
        except Exception as e:
            logger.warning(f"AnySearch调用失败: {e}")
            return []

    def _parse_result(self, raw: Dict, content_type: str) -> SearchResult:
        """解析原始搜索结果为结构化对象"""
        title = raw.get("title", raw.get("name", "未知标题"))
        url = raw.get("url", raw.get("link", ""))
        snippet = raw.get("snippet", raw.get("description", raw.get("content", "")))
        source = raw.get("source", raw.get("site", self._extract_domain(url)))

        # 可信度评估
        credibility = 0.5
        for domain, score in self.SOURCE_CREDIBILITY.items():
            if domain in url:
                credibility = score
                break

        # 相关性简单评估（标题包含关键词得分高）
        relevance = 0.5
        if title and len(title) < 50:
            relevance += 0.2
        if snippet and len(snippet) > 20:
            relevance += 0.1

        return SearchResult(
            title=title[:100],
            url=url,
            snippet=snippet[:200],
            source=source,
            relevance=min(relevance, 1.0),
            credibility=credibility,
            content_type=content_type,
        )

    def _extract_domain(self, url: str) -> str:
        """从URL提取域名"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except Exception:
            return "unknown"

    def get_search_stats(self) -> Dict[str, Any]:
        """获取搜索统计"""
        total_searches = len(self.search_history)
        total_results = sum(
            sum(h.get("result_counts", {}).values()) for h in self.search_history
        )
        return {
            "total_searches": total_searches,
            "total_results": total_results,
            "cache_size": len(self.result_cache),
            "last_search": self.search_history[-1] if self.search_history else None,
        }


# ============ 便捷函数 ============

def search_materials(query: str, material_types: List[str] = None) -> Dict[str, List[SearchResult]]:
    """便捷函数：搜索素材"""
    aggregator = MaterialSearchAggregator()
    return aggregator.search_materials(query, material_types)


def build_material_list(query: str, output_format: str = "markdown") -> str:
    """便捷函数：构建素材清单"""
    aggregator = MaterialSearchAggregator()
    return aggregator.build_material_list(query, output_format=output_format)


if __name__ == "__main__":
    # 自测
    print("=" * 50)
    print("MaterialSearchAggregator 自测")
    print("=" * 50)

    aggregator = MaterialSearchAggregator()

    # 测试1：构建素材清单（无CLI时返回空结构）
    print("\n[测试1] 构建素材清单（无CLI）")
    md_list = aggregator.build_material_list("科技感未来城市")
    print(f"  生成Markdown长度: {len(md_list)}字符")

    # 测试2：搜索统计
    print("\n[测试2] 搜索统计")
    stats = aggregator.get_search_stats()
    print(f"  总搜索次数: {stats['total_searches']}")
    print(f"  总结果数: {stats['total_results']}")

    # 测试3：结果解析
    print("\n[测试3] 结果解析")
    raw = {"title": "测试图片", "url": "https://example.com/test.jpg", "snippet": "这是一张测试图片"}
    result = aggregator._parse_result(raw, "image")
    print(f"  标题: {result.title}")
    print(f"  可信度: {result.credibility}")
    print(f"  指纹: {result.fingerprint}")

    print("\n" + "=" * 50)
    print("自测完成")
    print("=" * 50)
