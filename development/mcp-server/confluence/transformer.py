"""
Confluence 데이터 변환기
Confluence API 응답을 SpecGate 형식으로 변환하는 모듈
"""
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
        
        return {
            "id": result.get("id", ""),
            "title": result.get("title", ""),
            "content": content,
            "html_content": html_content,  # HTML 원본 추가
            "space_key": result.get("space", {}).get("key", ""),
            "space_name": result.get("space", {}).get("name", ""),
            "url": result.get("_links", {}).get("webui", ""),
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
            "labels": [],
            "created": "",
            "modified": "",
            "version": 1
        }
    
    def _convert_html_to_markdown(self, result: Dict[str, Any]) -> str:
        """HTML을 Markdown으로 변환"""
        content = result.get("body", {}).get("storage", {}).get("value", "")
        if not content:
            return ""
        
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
    
    def extract_metadata(self, confluence_response: Dict[str, Any]) -> Dict[str, Any]:
        """Confluence 응답에서 메타데이터 추출"""
        if not self.validate_confluence_response(confluence_response):
            return {}
        
        return {
            "total_count": len(confluence_response.get("results", [])),
            "has_more": confluence_response.get("_links", {}).get("next") is not None,
            "api_version": "confluence_rest_api_v1"
        }


