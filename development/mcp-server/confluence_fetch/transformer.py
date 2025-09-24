"""
Confluence 데이터 변환기
Confluence API 응답을 SpecGate 형식으로 변환하는 모듈
"""
import os
import re
import logging
from typing import Dict, Any, List


class ConfluenceDataTransformer:
    """Confluence 데이터 변환기"""
    
    def __init__(self):
        self.logger = logging.getLogger("specgate.confluence.transformer")
    
    def transform_to_specgate_format(self, confluence_response: Dict[str, Any]) -> Dict[str, Any]:
        """Confluence API 응답을 SpecGate 형식으로 변환"""
        if "results" not in confluence_response or not confluence_response["results"]:
            return self._create_empty_result()
        
        result = confluence_response["results"][0]  # 첫 번째 결과 사용
        
        # HTML 내용 추출
        html_content = result.get("body", {}).get("storage", {}).get("value", "")
        
        # HTML 내용을 Markdown으로 변환
        content = self._convert_html_to_markdown(result)
        
        # 상대경로(webui)를 절대 URL로 변환
        webui_path = result.get("_links", {}).get("webui", "")
        absolute_url = self._build_absolute_confluence_url(webui_path)
        
        return {
            "id": result.get("id", ""),
            "title": result.get("title", ""),
            "content": content,
            "html_content": html_content,  # HTML 원본 추가
            "space_key": result.get("space", {}).get("key", ""),
            "space_name": result.get("space", {}).get("name", ""),
            "url": absolute_url,  # 절대 URL
            "relative_url": webui_path,  # 참고용 상대 URL
            "labels": self._extract_labels(result),
            "created": result.get("version", {}).get("created", ""),
            "modified": result.get("version", {}).get("when", ""),
            "version": result.get("version", {}).get("number", 1)
        }
    
    def transform_batch_to_specgate_format(self, confluence_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """배치 Confluence API 응답을 SpecGate 형식으로 변환"""
        if "results" not in confluence_response or not confluence_response["results"]:
            return []
        
        specgate_documents = []
        for result in confluence_response["results"]:
            # 각 결과를 개별적으로 변환
            single_response = {"results": [result]}
            specgate_doc = self.transform_to_specgate_format(single_response)
            specgate_documents.append(specgate_doc)
        
        return specgate_documents
    
    def _create_empty_result(self) -> Dict[str, Any]:
        """빈 결과 생성"""
        return {
            "id": "",
            "title": "",
            "content": "",
            "space_key": "",
            "space_name": "",
            "url": "",
            "relative_url": "",
            "labels": [],
            "created": "",
            "modified": "",
            "version": 1
        }
    
    def _convert_html_to_markdown(self, result: Dict[str, Any]) -> str:
        """HTML을 Markdown으로 변환"""
        from html_to_md.converter import HTMLToMarkdownConverter
        
        content = result.get("body", {}).get("storage", {}).get("value", "")
        if not content:
            return ""
        
        document_title = result.get("title", "")
        
        # HTML to Markdown 변환기 사용
        converter = HTMLToMarkdownConverter()
        
        # 비동기 함수를 동기적으로 호출
        import asyncio
        
        # 이미 실행 중인 이벤트 루프가 있는지 확인
        try:
            # 실행 중인 이벤트 루프가 있으면 새 태스크로 실행
            loop = asyncio.get_running_loop()
            # 이 경우 동기적으로 실행할 수 없으므로 None 반환
            self.logger.warning("이벤트 루프가 이미 실행 중입니다. HTML to Markdown 변환을 건너뜁니다.")
            return None
        except RuntimeError:
            # 실행 중인 이벤트 루프가 없으면 새로 생성
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                conversion_result = loop.run_until_complete(
                    converter.convert(content, document_title=document_title)
                )
            finally:
                loop.close()
        
        if conversion_result and "markdown" in conversion_result:
            self.logger.info(f"HTML to Markdown 변환기 사용됨 - 제목: {document_title}")
            return conversion_result["markdown"]
        
        # 폴백: 간단한 변환
        self.logger.info(f"폴백 변환 사용됨 - 제목: {document_title}")
        return self._fallback_html_to_markdown(content, document_title)
    
    def _fallback_html_to_markdown(self, content: str, document_title: str = "") -> str:
        """HTML to Markdown 변환 폴백 방식"""
        # 제목이 없으면 추가 (h1 태그가 없고 document_title이 있는 경우)
        if document_title and not re.search(r'<h1>', content):
            content = f"<h1>{document_title}</h1>\n{content}"
            self.logger.info(f"제목 추가됨: {document_title}")
        
        # 간단한 HTML 태그 제거 및 변환
        content = content.replace("<p>", "").replace("</p>", "\n")
        content = content.replace("<br>", "\n").replace("<br/>", "\n")
        content = content.replace("<strong>", "**").replace("</strong>", "**")
        content = content.replace("<em>", "*").replace("</em>", "*")
        content = content.replace("<h1>", "# ").replace("</h1>", "\n")
        content = content.replace("<h2>", "## ").replace("</h2>", "\n")
        content = content.replace("<h3>", "### ").replace("</h3>", "\n")
        content = content.replace("<ul>", "").replace("</ul>", "\n")
        content = content.replace("<ol>", "").replace("</ol>", "\n")
        content = content.replace("<li>", "- ").replace("</li>", "\n")
        
        # HTML 태그 정리
        content = re.sub(r'<[^>]+>', '', content)
        
        # 연속된 공백 정리
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = content.strip()
        
        return content
    
    def _extract_labels(self, result: Dict[str, Any]) -> List[str]:
        """라벨 추출"""
        labels = result.get("metadata", {}).get("labels", {}).get("results", [])
        return [label.get("name", "") for label in labels if label.get("name")]
    
    def validate_confluence_response(self, response: Dict[str, Any]) -> bool:
        """Confluence 응답 유효성 검사"""
        if not isinstance(response, dict):
            return False
        
        if "results" not in response:
            return False
        
        if not isinstance(response["results"], list):
            return False
        
        return True

    def _build_absolute_confluence_url(self, webui_path: str) -> str:
        """상대경로(webui)를 절대 Confluence URL로 변환
        - webui가 '/spaces/...' 형태면 'https://{domain}/wiki{webui}'로 변환
        - 이미 절대 URL이면 그대로 반환
        - webui가 비어있으면 빈 문자열 반환
        도메인은 환경변수 CONFLUENCE_DOMAIN을 사용하며, 미설정 시 기본값 유지
        """
        if not webui_path:
            return ""
        if webui_path.startswith("http://") or webui_path.startswith("https://"):
            return webui_path
        domain = os.getenv("CONFLUENCE_DOMAIN", "your-domain.atlassian.net")
        # Confluence Cloud 기본 경로는 '/wiki'
        prefix = "/wiki" if not webui_path.startswith("/wiki/") else ""
        return f"https://{domain}{prefix}{webui_path}"
    
    def extract_metadata(self, confluence_response: Dict[str, Any]) -> Dict[str, Any]:
        """Confluence 응답에서 메타데이터 추출"""
        if not self.validate_confluence_response(confluence_response):
            return {}
        
        return {
            "total_count": len(confluence_response.get("results", [])),
            "has_more": confluence_response.get("_links", {}).get("next") is not None,
            "api_version": "confluence_rest_api_v1"
        }


